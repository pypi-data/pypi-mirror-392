import io
import json
import logging
import time
import urllib.parse
import base64
from typing import Any, Dict, List, Optional, Union

import requests

from baltra_sdk.shared.config import settings
from baltra_sdk.legacy.dashboards_folder.models import db
from baltra_sdk.infra.ads_wizard.sqlalchemy_models import CompanyMetaLink
from baltra_sdk.domain.ads_wizard.ports import MetaAdsApi


logger = logging.getLogger(__name__)


def _strip_token_from_url(url: Optional[str]) -> Optional[str]:
    """Redacta cualquier access_token presente en la URL."""
    if not url:
        return url
    try:
        parsed = urllib.parse.urlsplit(url)
        qs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        cleaned = []
        for k, v in qs:
            if k.lower() == "access_token":
                cleaned.append((k, "[REDACTED]"))
            else:
                cleaned.append((k, v))
        new_query = urllib.parse.urlencode(cleaned, doseq=True)
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment))
    except Exception:
        # Fallback muy conservador
        return url.replace("access_token=", "access_token=[REDACTED]&")


class MetaApiAdapter(MetaAdsApi):
    """Concrete adapter that talks to the Meta Graph API with detailed logging (sin exponer tokens)."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.api_version = settings.META_GRAPH_VERSION or "v23.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.business_id = settings.META_BUSINESS_ID
        self._default_token = token or settings.META_SYSTEM_USER_TOKEN_DEFAULT
        self._http_timeout = getattr(settings, "META_HTTP_TIMEOUT", 30)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _resolve_token(self, token: Optional[str]) -> str:
        if token:
            return token
        if not self._default_token:
            raise RuntimeError("META_SYSTEM_USER_TOKEN_DEFAULT must be configured")
        return self._default_token

    def _format_act_id(self, ad_account_id: str) -> str:
        return ad_account_id if ad_account_id.startswith("act_") else f"act_{ad_account_id}"

    def _stringify_fields(self, payload: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        processed = payload.copy()
        for field in fields:
            value = processed.get(field)
            if isinstance(value, (dict, list)):
                processed[field] = json.dumps(value)
        return processed

    def _prepare_image_asset(self, asset: Any) -> Dict[str, Any]:
        if isinstance(asset, str):
            response = requests.get(asset, timeout=self._http_timeout)
            response.raise_for_status()
            filename = asset.split("?")[0].rsplit("/", 1)[-1] or "upload.jpg"
            return {"bytes": (filename, response.content)}

        if isinstance(asset, bytes):
            return {"bytes": ("upload.jpg", io.BytesIO(asset))}

        filename = getattr(asset, "filename", getattr(asset, "name", "upload.jpg"))
        mimetype = getattr(asset, "mimetype", None)
        stream: Optional[Any] = None

        if hasattr(asset, "stream"):
            stream = asset.stream
        elif hasattr(asset, "read"):
            stream = asset

        if stream is None:
            raise ValueError("Unsupported asset type for Meta ad image upload")

        if hasattr(stream, "seek"):
            stream.seek(0)

        if mimetype:
            file_tuple: Union[tuple[str, Any, str], tuple[str, Any]] = (filename, stream, mimetype)
        else:
            file_tuple = (filename, stream)
        return {"bytes": file_tuple}

    # ------------------------------------------------------------------ #
    # Logging utils
    # ------------------------------------------------------------------ #
    @staticmethod
    def _redact(obj: Any) -> Any:
        """Redacta campos sensibles en estructuras (nunca imprime access_token)."""
        if isinstance(obj, dict):
            clean = {}
            for k, v in obj.items():
                if k.lower() in {"access_token", "authorization"}:
                    clean[k] = "[REDACTED]"
                else:
                    clean[k] = MetaApiAdapter._redact(v)
            return clean
        if isinstance(obj, list):
            return [MetaApiAdapter._redact(v) for v in obj]
        return obj

    def _log_meta_call(
            self,
            *,
            phase: str,  # "request" | "response" | "error"
            method: str,
            path: str,
            url: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[Dict[str, Any]] = None,
            status_code: Optional[int] = None,
            headers: Optional[Dict[str, Any]] = None,
            body_json: Optional[Any] = None,
            body_text: Optional[str] = None,
            duration_ms: Optional[int] = None,
            exc: Optional[BaseException] = None,
    ) -> None:
        files_info = None
        if files:
            files_info = {
                k: (getattr(v, "name", None) or (v[0] if isinstance(v, tuple) and v else "bytes"))
                if hasattr(v, "read") or hasattr(v, "name") or isinstance(v, tuple)
                else "bytes"
                for k, v in files.items()
            }

        safe_params = self._redact(params)
        safe_data = self._redact(data)
        safe_url = _strip_token_from_url(url)

        meta_headers = {}
        if headers:
            for hk in ["x-fb-request-id", "x-fb-trace-id", "x-business-use-case-usage", "x-app-usage"]:
                if hk in headers:
                    meta_headers[hk] = headers.get(hk)

        # prepara cuerpos seguros
        safe_body_json = body_json
        safe_body_text = body_text
        if isinstance(safe_body_text, str) and len(safe_body_text) > 4000:
            safe_body_text = safe_body_text[:4000] + "... [truncated]"

        log_payload = {
            "phase": phase,
            "method": method,
            "path": path,
            "url": safe_url,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "params": safe_params,
            "data": safe_data,
            "files": files_info,
            "response_headers": meta_headers or None,
            "body_json": safe_body_json,  # 👈 JSON si hay
            "body_text": safe_body_text,  # 👈 texto crudo siempre que se tenga
        }
        if exc:
            log_payload["error"] = repr(exc)

        try:
            msg_json = json.dumps(log_payload, ensure_ascii=False)
        except Exception:
            msg_json = str(log_payload)

        prefix = "Meta API"
        if phase == "error":
            logger.exception(f"{prefix} {phase} {method} {path} -> {msg_json}")
        elif phase == "request":
            logger.info(f"{prefix} {phase} {method} {path} -> {msg_json}")
        else:
            logger.info(f"{prefix} {phase} {method} {path} -> {msg_json}")

    # ------------------------------------------------------------------ #
    # HTTP wrappers (token nunca se loguea)
    # ------------------------------------------------------------------ #
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None, token: Optional[str] = None):
        base_params = params or {}
        params_for_log = dict(base_params)  # sin token
        params_with_token = dict(base_params)
        params_with_token["access_token"] = self._resolve_token(token)
        url = f"{self.base_url}/{path}"

        # ---- CURL DEBUG TEMPORAL ----
        safe_qs = urllib.parse.urlencode({**params_for_log, "access_token": "[REDACTED]"}, doseq=True)
        curl_line = f"curl -X GET '{url}?{safe_qs}'"
        logger.debug(f"[CURL DEBUG] {curl_line}")
        # -----------------------------

        # Log de request (sin token)
        self._log_meta_call(
            phase="request",
            method="GET",
            path=path,
            url=url,
            params=params_for_log,
        )

        start = time.perf_counter()
        try:
            r = requests.get(url, params=params_with_token, timeout=self._http_timeout)
            duration_ms = int((time.perf_counter() - start) * 1000)

            # Log de response con JSON y texto crudo
            resp_json = self._resp_json(r)
            resp_text = self._resp_text(r)
            if resp_json is None and resp_text is None:
                # Fallback: intenta _safe_json para no perder detalles de error
                safe = self._safe_json(r)
                if isinstance(safe, dict):
                    resp_json = safe
                else:
                    resp_text = str(safe)

            self._log_meta_call(
                phase="response",
                method="GET",
                path=path,
                url=_strip_token_from_url(r.url),
                params=params_for_log,  # sin token
                status_code=r.status_code,
                headers=dict(r.headers),
                body_json=resp_json,  # << JSON si existe
                body_text=resp_text,  # << texto crudo siempre
                duration_ms=duration_ms,
            )

            r.raise_for_status()
            return self._resp_json(r) if self._resp_json(r) is not None else self._resp_text(r)
        except Exception as e:
            duration_ms = int((time.perf_counter() - start) * 1000)
            resp = getattr(e, "response", None)

            # Log de error con ambos cuerpos (fallback incluido)
            err_json = self._resp_json(resp)
            err_text = self._resp_text(resp)
            if err_json is None and err_text is None:
                safe = self._safe_json(resp)
                if isinstance(safe, dict):
                    err_json = safe
                else:
                    err_text = str(safe)

            err_url = None
            try:
                err_url = _strip_token_from_url(getattr(resp, "url", None)) or _strip_token_from_url(url)
            except Exception:
                err_url = _strip_token_from_url(url)

            self._log_meta_call(
                phase="error",
                method="GET",
                path=path,
                url=err_url,
                params=params_for_log,  # sin token
                status_code=getattr(resp, "status_code", None),
                headers=dict(getattr(resp, "headers", {}) or {}),
                body_json=err_json,
                body_text=err_text,
                duration_ms=duration_ms,
                exc=e,
            )
            raise

    def _post(
            self,
            path: str,
            data: Optional[Dict[str, Any]] = None,
            token: Optional[str] = None,
            files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        base_data = data or {}
        data_for_log = dict(base_data)  # sin token
        payload_with_token = {**base_data, "access_token": self._resolve_token(token)}
        url = f"{self.base_url}/{path}"

        # ---- CURL DEBUG TEMPORAL ----
        def _sq(val: Any) -> str:
            """
            Envuelve en comillas simples y escapa comillas simples internas para shell:
            foo'bar -> 'foo'"'"'bar'
            """
            s = str(val)
            return "'" + s.replace("'", "'\"'\"'") + "'"

        url_q = f"\"{url}\""  # URL entre comillas dobles como en el ejemplo

        if files:
            # Para uploads usamos -F; mantenemos el token redactado
            parts = [f"-F {_sq('access_token=[REDACTED]')}"]
            for k, v in (files or {}).items():
                # Detecta si es campo normal (tuple con filename None) o archivo
                if isinstance(v, tuple):
                    fname = v[0] if len(v) > 0 else None
                    if fname is None:
                        # Campo normal en multipart (p. ej., 'bytes' base64). No imprimimos el valor real por longitud.
                        parts.append(f"-F {_sq(f'{k}=[BASE64]')}")
                    else:
                        parts.append(f"-F {_sq(f'{k}=@{fname}')}")
                else:
                    # file-like: intentar obtener nombre, si no, usar marcador
                    fname = getattr(v, 'name', None) or 'bytes'
                    parts.append(f"-F {_sq(f'{k}=@{fname}')}")
            curl_line = f"curl -X POST {url_q} " + " ".join(parts)
        else:
            # Para application/x-www-form-urlencoded usamos -d y el header explícito
            # Aseguramos serializar listas/dicts igual que se envían en requests (form)
            form_kv = []
            for k, v in (data_for_log or {}).items():
                if isinstance(v, (dict, list)):
                    v = json.dumps(v)
                form_kv.append(f"-d {_sq(f'{k}={v}')}")
            form_kv.append(f"-d {_sq('access_token=[REDACTED]')}")
            curl_line = (
                f"curl -X POST {url_q} "
                f"-H \"Content-Type: application/x-www-form-urlencoded\" "
                + " ".join(form_kv)
            )

        logger.debug(f"[CURL DEBUG] {curl_line}")
        # -----------------------------


        # Log de request (sin token)
        self._log_meta_call(
            phase="request",
            method="POST",
            path=path,
            url=url,
            data=data_for_log,
            files=files,
        )

        start = time.perf_counter()
        try:
            response = requests.post(url, data=payload_with_token, files=files, timeout=self._http_timeout)
            duration_ms = int((time.perf_counter() - start) * 1000)

            # Log de response con JSON y texto crudo
            resp_json = self._resp_json(response)
            resp_text = self._resp_text(response)
            if resp_json is None and resp_text is None:
                safe = self._safe_json(response)
                if isinstance(safe, dict):
                    resp_json = safe
                else:
                    resp_text = str(safe)

            self._log_meta_call(
                phase="response",
                method="POST",
                path=path,
                url=_strip_token_from_url(response.url),
                data=data_for_log,  # sin token
                files=files,
                status_code=response.status_code,
                headers=dict(response.headers),
                body_json=resp_json,  # << JSON si existe
                body_text=resp_text,  # << texto crudo siempre
                duration_ms=duration_ms,
            )

            response.raise_for_status()
            # Devuelve JSON si se puede, si no, texto (útil para algunos endpoints)
            body_json = self._resp_json(response)
            return body_json if body_json is not None else {"_raw": self._resp_text(response)}
        except Exception as e:
            duration_ms = int((time.perf_counter() - start) * 1000)
            resp = getattr(e, "response", None)

            # Log de error con ambos cuerpos (fallback incluido)
            err_json = self._resp_json(resp)
            err_text = self._resp_text(resp)
            if err_json is None and err_text is None:
                safe = self._safe_json(resp)
                if isinstance(safe, dict):
                    err_json = safe
                else:
                    err_text = str(safe)

            err_url = None
            try:
                err_url = _strip_token_from_url(getattr(resp, "url", None)) or _strip_token_from_url(url)
            except Exception:
                err_url = _strip_token_from_url(url)

            self._log_meta_call(
                phase="error",
                method="POST",
                path=path,
                url=err_url,
                data=data_for_log,  # sin token
                files=files,
                status_code=getattr(resp, "status_code", None),
                headers=dict(getattr(resp, "headers", {}) or {}),
                body_json=err_json,
                body_text=err_text,
                duration_ms=duration_ms,
                exc=e,
            )
            raise

    @staticmethod
    def _safe_json(resp: Optional[requests.Response]) -> Any:
        if not resp:
            return None
        try:
            return resp.json()
        except ValueError:
            txt = resp.text or ""
            return txt[:2000] + ("... [truncated]" if len(txt) > 2000 else "")

    @staticmethod
    def _resp_json(resp: Optional[requests.Response]) -> Any:
        """Devuelve el JSON parseado de la respuesta si es posible, o None."""
        if not resp:
            return None
        try:
            return resp.json()
        except Exception:
            return None

    @staticmethod
    def _resp_text(resp: Optional[requests.Response]) -> Optional[str]:
        """Devuelve el texto crudo de la respuesta (truncado si es muy largo)."""
        if not resp:
            return None
        try:
            txt = resp.text or ""
            return txt[:4000] + ("... [truncated]" if len(txt) > 4000 else "")
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Discovery endpoints
    # ------------------------------------------------------------------ #
    def get_ad_accounts(self, token: Optional[str] = None) -> List[Dict[str, Any]]:
        owned = self.get_owned_ad_accounts(token).get("data", [])
        client = self.get_client_ad_accounts(token).get("data", [])
        return owned + client

    def get_user_businesses(self, token: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        try:
            payload = self._get("me/businesses", token=token)
        except requests.HTTPError:
            payload = {}

        data = payload.get("data") if isinstance(payload, dict) else None
        businesses: List[Dict[str, Any]] = [entry for entry in data or [] if entry.get("id")]

        business_id = self.business_id
        if business_id and not any(entry.get("id") == business_id for entry in businesses):
            try:
                detail = self._get(business_id, params={"fields": "id,name"}, token=token)
            except requests.HTTPError:
                detail = None

            if isinstance(detail, dict) and detail.get("id"):
                businesses.append({"id": detail["id"], "name": detail.get("name") or detail["id"]})
            elif business_id:
                businesses.append({"id": business_id, "name": business_id})

        return {"data": businesses}

    def get_pages(self, token: Optional[str] = None) -> Dict[str, Any]:
        if not self.business_id:
            raise RuntimeError("META_BUSINESS_ID must be configured to list pages")
        params = {"fields": "id,name,link"}
        return self._get(f"{self.business_id}/owned_pages", params=params, token=token)

    def get_client_ad_accounts(self, token: Optional[str] = None) -> Dict[str, Any]:
        params = {"fields": "id,account_id,name,account_status,currency,timezone_id,business{id,name}"}
        return self._get(f"{self.business_id}/client_ad_accounts", params=params, token=token)

    def get_owned_ad_accounts(self, token: Optional[str] = None) -> Dict[str, Any]:
        params = {"fields": "id,account_id,name,account_status,currency,timezone_id,business{id,name}"}
        return self._get(f"{self.business_id}/owned_ad_accounts", params=params, token=token)

    def get_ad_account_detail(self, ad_account_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        act_id = self._format_act_id(ad_account_id)
        params = {
            "fields": (
                "id,account_id,name,account_status,currency,timezone_name,"
                "business{id,name},amount_spent,balance"
            )
        }
        return self._get(act_id, params=params, token=token)

    def targeting_search(self, act_id: str, params: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        params.setdefault("country_code", "MX")
        params.setdefault("type", "adgeolocation")
        formatted = self._format_act_id(act_id)
        return self._get(f"{formatted}/targetingsearch", params=params, token=token)

    # ------------------------------------------------------------------ #
    # Mutation endpoints
    # ------------------------------------------------------------------ #
    def create_campaign(
        self,
        ad_account_id: str,
        payload: Dict[str, Any],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        act_id = self._format_act_id(ad_account_id)
        prepared = self._stringify_fields(payload, ["special_ad_categories"])
        return self._post(f"{act_id}/campaigns", data=prepared, token=token)

    def create_ad_set(
        self,
        ad_account_id: str,
        ad_set_payload: Dict[str, Any],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        act_id = self._format_act_id(ad_account_id)
        prepared = self._stringify_fields(ad_set_payload, ["targeting", "promoted_object"])
        return self._post(f"{act_id}/adsets", data=prepared, token=token)

    def create_ad_image(self, ad_account_id: str, asset: Any, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Uploads an ad image using the 'bytes' field as base64-encoded content, as required by Meta.
        Accepts:
          - asset: URL (str), raw bytes, or file-like object. Any of these will be read into bytes
            and base64-encoded before sending.
        """
        act_id = self._format_act_id(ad_account_id)

        # Resolve content bytes from different asset types
        content_bytes: Optional[bytes] = None
        if isinstance(asset, str):
            # Treat as URL
            resp = requests.get(asset, timeout=self._http_timeout)
            resp.raise_for_status()
            content_bytes = resp.content
        elif isinstance(asset, (bytes, bytearray)):
            content_bytes = bytes(asset)
        else:
            # Try file-like
            stream = None
            if hasattr(asset, "stream"):
                stream = asset.stream
            elif hasattr(asset, "read"):
                stream = asset
            if stream is None:
                raise ValueError("Unsupported asset type for Meta ad image upload")
            if hasattr(stream, "seek"):
                try:
                    stream.seek(0)
                except Exception:
                    pass
            content_bytes = stream.read()

        if not content_bytes:
            raise ValueError("Empty image content; cannot upload to Meta")

        # Base64 encode as required by Meta for the 'bytes' field
        b64 = base64.b64encode(content_bytes).decode("ascii")

        # Use multipart/form-data with a normal form field (not file upload)
        # requests encodes (None, value) tuples in 'files' as regular fields in multipart
        files = {"bytes": (None, b64)}
        resp = self._post(f"{act_id}/adimages", token=token, files=files)
        # Normalize Meta's response: it returns {"images": {"<key>": {"hash": "...", ...}}}
        # We prefer returning the inner image object directly (with 'hash', 'url', etc.).
        try:
            if isinstance(resp, dict) and isinstance(resp.get("images"), dict):
                images_dict = resp.get("images") or {}
                if images_dict:
                    first_item = next(iter(images_dict.values()))
                    if isinstance(first_item, dict) and first_item.get("hash"):
                        return first_item
        except Exception:
            # If normalization fails, fall back to raw response
            pass
        return resp

    def create_ad_creative(
        self,
        ad_account_id: str,
        payload: Dict[str, Any],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        act_id = self._format_act_id(ad_account_id)
        prepared = self._stringify_fields(payload, ["object_story_spec"])
        return self._post(f"{act_id}/adcreatives", data=prepared, token=token)

    def create_ad(
        self,
        ad_account_id: str,
        payload: Dict[str, Any],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        act_id = self._format_act_id(ad_account_id)
        prepared = payload.copy()
        if isinstance(prepared.get("creative"), (dict, list)):
            prepared["creative"] = json.dumps(prepared["creative"])
        return self._post(f"{act_id}/ads", data=prepared, token=token)

    def get_ads(self, ad_account_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        act_id = self._format_act_id(ad_account_id)
        params = {"fields": "id,name,status,effective_status,adset_id,campaign_id"}
        return self._get(f"{act_id}/ads", params=params, token=token).get("data", [])

    def get_insights(self, scope: str, scope_id: str, window: str, token: Optional[str] = None) -> Dict[str, Any]:
        preset_map = {"7d": "last_7d", "14d": "last_14d", "28d": "last_28d"}
        date_preset = preset_map.get(window, "last_28d")
        params = {
            "level": scope or "ad",
            "date_preset": date_preset,
            "fields": "spend,impressions,reach,cpm,cpp,clicks,conversions",
        }
        return self._get(f"{scope_id}/insights", params=params, token=token)

    def update_ad_status(self, ad_id: str, status: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._post(ad_id, data={"status": status}, token=token)

    def duplicate_ad(self, ad_id: str, deep_copy: bool, token: Optional[str] = None) -> Dict[str, Any]:
        return self._post(f"{ad_id}/copies", data={"deep_copy": deep_copy}, token=token)

    def update_ad_budget(self, ad_id: str, daily_budget_cents: int, token: Optional[str] = None) -> Dict[str, Any]:
        ad_info = self._get(ad_id, params={"fields": "adset_id"}, token=token)
        adset_id = ad_info.get("adset_id")
        if not adset_id:
            raise ValueError("Could not find adset for the given ad.")
        return self._post(adset_id, data={"daily_budget": daily_budget_cents}, token=token)

    def update_ad_dates(self, ad_id: str, end_time: str, token: Optional[str] = None) -> Dict[str, Any]:
        ad_info = self._get(ad_id, params={"fields": "adset_id"}, token=token)
        adset_id = ad_info.get("adset_id")
        if not adset_id:
            raise ValueError("Could not find adset for the given ad.")
        return self._post(adset_id, data={"end_time": end_time}, token=token)

    # ------------------------------------------------------------------ #
    # WhatsApp helpers
    # ------------------------------------------------------------------ #
    def _get_user_businesses(self, token: Optional[str] = None) -> Dict[str, Any]:
        return self._get("me/businesses", token=token)

    def _get_owned_whatsapp_business_accounts(self, business_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._get(f"{business_id}/owned_whatsapp_business_accounts", token=token)

    def _get_phone_numbers(self, waba_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        params = {"fields": "display_phone_number,verified_name,id"}
        return self._get(f"{waba_id}/phone_numbers", params=params, token=token)

    def _get_client_whatsapp_business_accounts(self, business_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._get(f"{business_id}/client_whatsapp_business_accounts", token=token)

    def get_whatsapp_business_account(self, waba_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        params = {"fields": "owner_business_info"}
        return self._get(waba_id, params=params, token=token)

    def _get_whatsapp_business_account(self, waba_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self.get_whatsapp_business_account(waba_id, token=token)

    def get_owned_whatsapp_business_accounts(
        self,
        business_id: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        target_business = business_id or self.business_id
        if not target_business:
            raise RuntimeError("business_id is required to list WhatsApp Business Accounts")
        return self._get_owned_whatsapp_business_accounts(target_business, token=token)

    def get_client_whatsapp_business_accounts(
        self,
        business_id: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        target_business = business_id or self.business_id
        if not target_business:
            raise RuntimeError("business_id is required to list WhatsApp Business Accounts")
        return self._get_client_whatsapp_business_accounts(target_business, token=token)

    def get_phone_numbers(self, waba_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Public wrapper for testing/auto-linking helpers."""
        return self._get_phone_numbers(waba_id, token=token)

    # ------------------------------------------------------------------ #
    # Drafts & listings
    # ------------------------------------------------------------------ #
    def create_campaign_draft(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Draft generation is handled entirely on the backend without calling Meta.
        return {"draft_id": "draft_local", "payload": payload}

    def get_campaigns(self, ad_account_id: str, token: Optional[str] = None):
        act_id = self._format_act_id(ad_account_id)
        params = {
            "fields": "id,name,status,objective,special_ad_categories,created_time,updated_time",
            # JSON en una sola cadena para forzar formato correcto
            "effective_status": json.dumps(["ACTIVE", "PAUSED", "ARCHIVED"]),
        }
        res = self._get(f"{act_id}/campaigns", params=params, token=token)
        return res.get("data", []) if isinstance(res, dict) else []

    def get_ad_sets(self, campaign_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"fields": "id,name,status,daily_budget,targeting,campaign_id,created_time,updated_time"}
        response = self._get(f"{campaign_id}/adsets", params=params, token=token)
        if isinstance(response, dict):
            return response.get("data", [])
        return []

    def get_ads_for_ad_set(self, ad_set_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"fields": "id,name,status,creative{id},created_time,updated_time"}
        response = self._get(f"{ad_set_id}/ads", params=params, token=token)
        if isinstance(response, dict):
            return response.get("data", [])
        return []

    def update_campaign_status(self, campaign_id: str, status: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._post(campaign_id, data={"status": status}, token=token)

    def update_ad_set_status(self, ad_set_id: str, status: str, token: Optional[str] = None) -> Dict[str, Any]:
        return self._post(ad_set_id, data={"status": status}, token=token)
