from __future__ import annotations

import logging
import re
import base64
from datetime import datetime
from typing import Any, Dict, List, Optional

from baltra_sdk.domain.ads_wizard.ports import (
    AdTemplatesRepository,
    CompanyMetaLinkRepository,
    CompaniesRepository,
    CompanyRolesRepository,
    MetaAdRepository,
    MetaAdSetRepository,
    MetaAdAccountRepository,
    MetaAdsApi,
    MetaCampaignRepository,
)


def deep_merge(*mappings: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Deep merge dictionaries from left to right, later values override earlier ones."""
    result: Dict[str, Any] = {}
    for mapping in mappings:
        if not mapping:
            continue
        for key, value in mapping.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
    return result


class AdsWizardService:
    def __init__(
        self,
        meta_ads_api: MetaAdsApi,
        ad_templates_repository: AdTemplatesRepository,
        link_repository: CompanyMetaLinkRepository,
        companies_repository: CompaniesRepository,
        company_roles_repository: CompanyRolesRepository,
        meta_campaign_repository: MetaCampaignRepository,
        meta_ad_set_repository: MetaAdSetRepository,
        meta_ad_repository: MetaAdRepository,
        meta_ad_account_repository: MetaAdAccountRepository,
    ) -> None:
        self.meta_ads_api = meta_ads_api
        self.ad_templates_repository = ad_templates_repository
        self.link_repository = link_repository
        self.companies_repository = companies_repository
        self.company_roles_repository = company_roles_repository
        self.meta_campaign_repository = meta_campaign_repository
        self.meta_ad_set_repository = meta_ad_set_repository
        self.meta_ad_repository = meta_ad_repository
        self.meta_ad_account_repository = meta_ad_account_repository
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    # Context helpers
    # ------------------------------------------------------------------ #
    def _get_context(self, company_id: int) -> Optional[Dict[str, Any]]:
        context = self.link_repository.get_link_by_company_id(company_id)
        if not context:
            raise ValueError(f"No Meta link configured for company_id={company_id}")
        return context

    def _get_token(self, context: Optional[Dict[str, Any]]) -> Optional[str]:
        if not context:
            return None
        return context.get("system_user_token")

    def _ensure_campaign_record(
        self,
        remote_campaign: Dict[str, Any],
        company_id: int,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        meta_id = remote_campaign.get("id")
        if not meta_id:
            raise ValueError("Meta campaign response missing id.")

        existing = self.meta_campaign_repository.get_by_meta_id(meta_id)
        if existing:
            return existing

        record = {
            "meta_campaign_id": meta_id,
            "company_id": company_id,
            "name": remote_campaign.get("name") or payload.get("name"),
            "objective": remote_campaign.get("objective") or payload.get("objective"),
            "status": remote_campaign.get("status") or payload.get("status"),
            "special_ad_categories": payload.get("special_ad_categories"),
        }
        return self.meta_campaign_repository.create_campaign(record)

    def _ensure_ad_set_record(
        self,
        remote_ad_set: Dict[str, Any],
        campaign_meta_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        meta_id = remote_ad_set.get("id")
        if not meta_id:
            raise ValueError("Meta ad set response missing id.")

        existing = self.meta_ad_set_repository.get_by_meta_id(meta_id)
        if existing:
            return existing

        campaign = self.meta_campaign_repository.get_by_meta_id(campaign_meta_id)
        if not campaign:
            raise ValueError("Campaign must be persisted before linking ad sets.")

        record = {
            "meta_ad_set_id": meta_id,
            "campaign_id": campaign["id"],
            "name": remote_ad_set.get("name") or payload.get("name"),
            "status": remote_ad_set.get("status") or payload.get("status"),
            "daily_budget_cents": payload.get("daily_budget"),
            "targeting": payload.get("targeting"),
        }
        return self.meta_ad_set_repository.create_ad_set(record)

    def _ensure_ad_record(
        self,
        remote_ad: Dict[str, Any],
        ad_set_meta_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        meta_id = remote_ad.get("id")
        if not meta_id:
            raise ValueError("Meta ad response missing id.")

        existing = self.meta_ad_repository.get_by_meta_id(meta_id)
        if existing:
            return existing

        ad_set = self.meta_ad_set_repository.get_by_meta_id(ad_set_meta_id)
        if not ad_set:
            raise ValueError("Ad set must be persisted before linking ads.")

        record = {
            "meta_ad_id": meta_id,
            "ad_set_id": ad_set["id"],
            "creative_id": payload.get("creative_id"),
            "status": remote_ad.get("status") or payload.get("status"),
        }
        return self.meta_ad_repository.create_ad(record)

    # ------------------------------------------------------------------ #
    # Campaign lifecycle
    # ------------------------------------------------------------------ #
    def create_campaign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.copy()
        company_id = data.pop("company_id", None)
        role_id = data.pop("role_id", None)
        ad_account_id = data.pop("ad_account_id", None)

        context = None
        if company_id is not None:
            context = self._get_context(company_id)
            ad_account_id = ad_account_id or context.get("ad_account_id")
        if not ad_account_id:
            raise ValueError("ad_account_id is required to create a campaign.")

        campaign_name = data.get("name") or "Campaña CTWA"

        def _normalize_special_ad_categories(value: Any) -> Optional[List[str]]:
            if not value:
                return None
            if isinstance(value, dict):
                items = value.get("items")
                if isinstance(items, (list, tuple)):
                    return [str(item) for item in items]
            if isinstance(value, (list, tuple)):
                return [str(item) for item in value]
            if isinstance(value, str):
                return [value]
            return None

        normalized_specials = _normalize_special_ad_categories(data.get("special_ad_categories"))
        if normalized_specials is not None:
            data["special_ad_categories"] = normalized_specials
        else:
            data.pop("special_ad_categories", None)

        company_defaults = (context or {}).get("defaults", {}).get("campaign", {})

        final_payload = deep_merge(
            {
                "name": campaign_name,
                "objective": "MESSAGES",
                "special_ad_categories": ["EMPLOYMENT"],
                "status": "PAUSED",
                "buying_type": "AUCTION",
            },
            company_defaults,
            data,
        )
        # Guarantee required fields
        final_payload["name"] = campaign_name
        if not final_payload.get("special_ad_categories"):
            final_payload["special_ad_categories"] = ["EMPLOYMENT"]

        token = self._get_token(context)
        self.logger.info(
            "Create campaign payload for account %s: %s",
            ad_account_id,
            final_payload,
        )
        remote = self.meta_ads_api.create_campaign(ad_account_id, final_payload, token)

        local = None
        if company_id is not None:
            local = self._ensure_campaign_record(remote, company_id, final_payload)

        return {**remote, "local_id": (local or {}).get("id")}

    def create_ad_set(self, ad_set_payload: Dict[str, Any], company_id: int, role_id: Optional[int] = None) -> Dict[
        str, Any]:
        context = self._get_context(company_id)
        ad_account_id = context.get("ad_account_id")
        if not ad_account_id:
            raise ValueError("Company is not linked to a Meta ad account.")

        campaign_id = ad_set_payload.get("campaign_id")
        if not campaign_id:
            raise ValueError("campaign_id is required to create an ad set.")

        # Resolver page_id para CTWA (promoted_object)
        # Preferimos lo que venga en el payload (promoted_object.page_id o page_id plano),
        # luego caemos al vínculo de la empresa.
        payload_promoted = ad_set_payload.get("promoted_object") or {}
        page_id = (
            payload_promoted.get("page_id")
            or ad_set_payload.get("page_id")
            or (context or {}).get("page_id")
        )
        if not page_id:
            raise ValueError("Company Meta link or payload must include page_id to create a CTWA ad set (promoted_object).")

        company_defaults = context.get("defaults", {}).get("ad_set", {})

        # NOTA: respetamos valores del payload del front si ya vienen;
        #       si no, aplicamos defaults que piden tus cURLs de referencia.
        final_payload = deep_merge(
            {
                "campaign_id": campaign_id,
                "status": ad_set_payload.get("status") or "PAUSED",
                "optimization_goal": "CONVERSATIONS",
                "billing_event": "IMPRESSIONS",
                "destination_type": "WHATSAPP",
                "bid_strategy": ad_set_payload.get("bid_strategy") or "LOWEST_COST_WITHOUT_CAP",
                "promoted_object": {"page_id": str(page_id)},
            },
            company_defaults,
            ad_set_payload,  # ← deja pasar daily_budget, start_time, end_time, targeting, etc.
        )

        # Sanitiza custom_locations: Meta no acepta el campo 'address'
        try:
            geo = (final_payload.get("targeting") or {}).get("geo_locations") or {}
            custom_locations = geo.get("custom_locations") or []
            if isinstance(custom_locations, list):
                for loc in custom_locations:
                    if isinstance(loc, dict):
                        loc.pop("address", None)
        except Exception:
            # No obstaculizar la creación si algo sale mal al sanitizar
            pass

        # No transformamos start_time/end_time; Meta acepta ISO-8601 con 'Z' como en tu ejemplo
        token = self._get_token(context)
        self.logger.info("Create ad set payload for account %s: %s", ad_account_id, final_payload)

        remote = self.meta_ads_api.create_ad_set(ad_account_id, final_payload, token)
        local = self._ensure_ad_set_record(remote, campaign_id, final_payload)

        return {**remote, "local_id": local.get("id")}

    def create_full_campaign(self, full_payload: Dict[str, Any]) -> Dict[str, Any]:
        company_id = full_payload.get("company_id")
        if company_id is None:
            raise ValueError("company_id is required to create a full campaign.")
        role_id = full_payload.get("role_id")

        # Campaign
        campaign_payload = {
            **full_payload.get("campaign", {}),
            "company_id": company_id,
            "role_id": role_id,
        }
        campaign_result = self.create_campaign(campaign_payload)
        campaign_meta_id = campaign_result["id"]

        # Ad set
        ad_set_payload = full_payload.get("ad_set", {}).copy()
        ad_set_payload["campaign_id"] = campaign_meta_id

        # Ensure page_id is present in promoted_object if available
        context = None
        try:
            context = self._get_context(company_id)
        except Exception:
            context = None

        promoted_in = (ad_set_payload.get("promoted_object") or {})
        page_id = (
            promoted_in.get("page_id")
            or ad_set_payload.get("page_id")
            or full_payload.get("page_id")
            or ((context or {}).get("page_id"))
        )
        if page_id:
            # merge without clobbering other promoted_object keys
            promoted_out = dict(promoted_in)
            promoted_out["page_id"] = str(page_id)
            ad_set_payload["promoted_object"] = promoted_out

        ad_set_result = self.create_ad_set(ad_set_payload, company_id, role_id)
        ad_set_meta_id = ad_set_result["id"]

        # Creative image
        creative_payload = full_payload.get("creative", {}) or {}
        # Accept either base64 data or URL from the frontend
        image_b64 = creative_payload.get("image_base64") or creative_payload.get("imageBase64")
        image_source = creative_payload.get("image_url") or creative_payload.get("imageUrl")
        if not image_b64 and not image_source:
            raise ValueError("Provide creative.image_base64 or creative.image_url to upload the ad image.")

        # Log base64 separately for debugging as requested
        if image_b64:
            try:
                self.logger.info("[AdsWizard] Received creative.image_base64: length=%s, head=%s", len(image_b64), image_b64[:80])
                # Log full base64 so you can copy it easily from logs for testing
                self.logger.info("[AdsWizard] creative.image_base64 FULL: %s", image_b64)
            except Exception:
                pass

        image_payload: Dict[str, Any] = {"company_id": company_id}
        if image_b64:
            image_payload["image_base64"] = image_b64
        else:
            image_payload["image_url"] = image_source

        image_result = self.create_ad_image(image_payload)
        # Normalize/parse image hash from adapter response
        image_hash = None
        if isinstance(image_result, dict):
            image_hash = image_result.get("hash")
            if not image_hash and isinstance(image_result.get("images"), dict):
                images_dict = image_result.get("images") or {}
                if images_dict:
                    first_item = next(iter(images_dict.values()))
                    if isinstance(first_item, dict):
                        image_hash = first_item.get("hash")
        if not image_hash:
            try:
                self.logger.error("[AdsWizard] Unable to parse image hash from response: keys=%s", list(image_result.keys()) if isinstance(image_result, dict) else type(image_result))
            except Exception:
                pass
            raise KeyError("hash")

        # Creative
        creative_body = {
            **creative_payload,
            "company_id": company_id,
            "role_id": role_id,
            "image_hash": image_hash,
        }
        creative_result = self.create_ad_creative(creative_body)
        creative_id = creative_result["id"]

        # Ad
        ad_payload = {
            **full_payload.get("ad", {}),
            "company_id": company_id,
            "adset_id": ad_set_meta_id,
            "creative_id": creative_id,
        }
        ad_result = self.create_ad(ad_payload)

        return {
            "campaign_id": campaign_meta_id,
            "adset_id": ad_set_meta_id,
            "creative_id": creative_id,
            "ad_id": ad_result.get("id"),
            "status": ad_result.get("status"),
        }

    # ------------------------------------------------------------------ #
    # Assets
    # ------------------------------------------------------------------ #
    def create_ad_image(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.copy()
        company_id = data.pop("company_id", None)
        ad_account_id = data.pop("ad_account_id", None)
        # Accept base64, URL, or uploaded file
        image_b64 = data.pop("image_base64", None) or data.pop("imageBase64", None)
        image_source = data.pop("image_url", None) or data.pop("imageUrl", None) or data.pop("file", None)

        context = None
        if company_id is not None:
            context = self._get_context(company_id)
            ad_account_id = ad_account_id or context.get("ad_account_id")
        if not ad_account_id:
            raise ValueError("ad_account_id is required to upload images.")
        if image_b64 is None and image_source is None:
            raise ValueError("image_base64, image_url or file is required to upload images.")

        # If base64 is provided, decode and pass bytes to adapter
        asset: Any
        if image_b64 is not None:
            # Log base64 provided for the standalone image upload endpoint as well
            try:
                preview = image_b64[:80] if isinstance(image_b64, str) else ""
                self.logger.info(
                    "[AdsWizard] Received image_base64: length=%s, head=%s",
                    len(image_b64) if hasattr(image_b64, "__len__") else "?",
                    preview,
                )
            except Exception:
                pass
            # Strip optional data URI prefix like: data:image/png;base64,
            if isinstance(image_b64, str):
                header_sep = image_b64.find(",")
                if image_b64.startswith("data:") and header_sep != -1:
                    image_b64 = image_b64[header_sep + 1 :]
                try:
                    asset = base64.b64decode(image_b64, validate=True)
                except Exception:
                    # Fallback without validate in case some clients send with whitespace
                    asset = base64.b64decode(image_b64)
            else:
                raise ValueError("image_base64 must be a base64-encoded string")
        else:
            asset = image_source

        token = self._get_token(context)
        return self.meta_ads_api.create_ad_image(ad_account_id, asset, token)

    def create_ad_creative(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.copy()
        company_id = data.pop("company_id")
        data.pop("role_id", None)
        image_hash = data.pop("image_hash", None) or data.pop("imageHash", None)

        context = self._get_context(company_id)
        ad_account_id = context.get("ad_account_id")
        # Resolver page_id con prioridad: payload.object_story_spec.page_id -> payload.page_id -> context.page_id
        obj_story_in = (data.get("object_story_spec") or {})
        page_id_override = obj_story_in.get("page_id") or data.get("page_id")
        page_id = page_id_override or context.get("page_id")
        if not ad_account_id or not page_id:
            raise ValueError("Company Meta link must include ad_account_id and page_id, or provide page_id in payload.")
        if not image_hash:
            raise ValueError("image_hash is required to create an ad creative.")

        company_defaults = context.get("defaults", {}).get("creative", {})
        variant_defaults: Dict[str, Any] = {}

        variants = data.pop("variants", None) or []
        variant_payload = variants[0] if variants else {}

        link_data = {
            "message": variant_payload.get("primaryText") or variant_defaults.get("primaryText", ""),
            "name": variant_payload.get("title") or variant_defaults.get("title", ""),
            "description": variant_payload.get("description") or variant_defaults.get("description", ""),
            "image_hash": image_hash,
            "call_to_action": {
                "type": "WHATSAPP_MESSAGE",
                "value": {"app_destination": "WHATSAPP"},
            },
        }
        whatsapp_number = context.get("wa_number_id") or context.get("whatsapp_number")
        if whatsapp_number:
            link_data["call_to_action"]["value"]["whatsapp_number"] = whatsapp_number
        else:
            self.logger.warning(
                "create_ad_creative: whatsapp number not found for company_id=%s; call_to_action will omit whatsapp_number",
                company_id,
            )

        # Ensurar que object_story_spec.page_id final sea el resuelto
        object_story_spec_out = deep_merge({"page_id": str(page_id), "link_data": link_data}, obj_story_in)

        final_payload = deep_merge(
            {
                "name": data.get("name") or "CTWA Creative",
                "object_story_spec": object_story_spec_out,
            },
            company_defaults,
            data,
        )

        # Remove legacy image fields if present (after merging defaults/payload)
        for key in ("image_url", "imageUrl", "image_base64", "imageBase64", "variants"):
            final_payload.pop(key, None)

        token = self._get_token(context)
        self.logger.info(
            "Create ad creative payload for account %s: %s",
            ad_account_id,
            final_payload,
        )
        return self.meta_ads_api.create_ad_creative(ad_account_id, final_payload, token)

    def create_ad(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload.copy()
        company_id = data.pop("company_id", None)
        ad_account_id = data.pop("ad_account_id", None)
        adset_id = data.pop("adset_id") or data.pop("adSetId", None)
        creative_id = data.pop("creative_id") or data.pop("creativeId", None)

        if not adset_id or not creative_id:
            raise ValueError("adset_id and creative_id are required to create an ad.")

        context = None
        if company_id is not None:
            context = self._get_context(company_id)
            ad_account_id = ad_account_id or context.get("ad_account_id")
        if not ad_account_id:
            raise ValueError("ad_account_id is required to create an ad.")

        status = data.pop("status", None)
        activate_on_create = data.pop("activate_on_create", None)
        if status:
            status_value = status.upper()
        else:
            status_value = "ACTIVE" if activate_on_create else "PAUSED"

        final_payload = deep_merge(
            {
                "name": data.get("name") or "Anuncio CTWA",
                "adset_id": adset_id,
                "creative": {"creative_id": creative_id},
                "status": status_value,
            },
            data,
        )

        token = self._get_token(context)
        remote = self.meta_ads_api.create_ad(ad_account_id, final_payload, token)

        if company_id is not None:
            self._ensure_ad_record(
                remote,
                adset_id,
                {"creative_id": creative_id, "status": status_value},
            )

        return remote

    # ------------------------------------------------------------------ #
    # Insights & management
    # ------------------------------------------------------------------ #
    def get_ads(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        data = params.copy()
        company_id = data.pop("company_id", None)
        ad_account_id = data.pop("ad_account_id", None)

        context = None
        if company_id is not None:
            context = self._get_context(company_id)
            ad_account_id = ad_account_id or context.get("ad_account_id")
        if not ad_account_id:
            raise ValueError("ad_account_id is required to list ads.")

        token = self._get_token(context)
        return self.meta_ads_api.get_ads(ad_account_id, token)

    def get_insights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        data = params.copy()
        scope = data.get("scope") or "ad"
        scope_id = data.get("scope_id")
        window = data.get("window", "28d")
        if not scope_id:
            raise ValueError("scope_id is required to retrieve insights.")
        company_id = data.get("company_id")

        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.get_insights(scope, scope_id, window, token)

    def update_ad_status(self, ad_id: str, status: str, company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.update_ad_status(ad_id, status, token)

    def duplicate_ad(self, ad_id: str, deep_copy: bool, company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.duplicate_ad(ad_id, deep_copy, token)

    def update_ad_budget(self, ad_id: str, daily_budget_cents: int, company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.update_ad_budget(ad_id, daily_budget_cents, token)

    def update_ad_dates(self, ad_id: str, end_time: str, company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.update_ad_dates(ad_id, end_time, token)

    # ------------------------------------------------------------------ #
    # Discovery & utilities
    # ------------------------------------------------------------------ #
    def create_template(self, kind: str, key: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.ad_templates_repository.create_template(kind, key, json_data)

    def get_ad_accounts(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return {"data": self.meta_ads_api.get_ad_accounts(token)}

    def get_company_roles(self, company_id: int) -> Dict[str, Any]:
        if company_id is None:
            raise ValueError("company_id is required")
        roles = self.company_roles_repository.list_roles_for_company(company_id)
        return {"data": roles}

    @staticmethod
    def _format_timestamp(value: Any) -> Optional[str]:
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    @staticmethod
    def _parse_meta_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value or not isinstance(value, str):
            return None
        cleaned = value.strip()
        if cleaned.endswith("Z"):
            cleaned = cleaned[:-1] + "+00:00"
        if cleaned.endswith("+0000"):
            cleaned = cleaned[:-5] + "+00:00"
        try:
            return datetime.fromisoformat(cleaned)
        except ValueError:
            return None

    @staticmethod
    def _parse_int(value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _build_campaign_hierarchy(self, company_id: int) -> List[Dict[str, Any]]:
        campaigns = self.meta_campaign_repository.list_by_company(company_id)
        hierarchy: List[Dict[str, Any]] = []

        for campaign in campaigns:
            internal_campaign_id = campaign.get("id")
            ad_sets_payload: List[Dict[str, Any]] = []

            if internal_campaign_id is not None:
                ad_sets = self.meta_ad_set_repository.list_by_campaign_internal_id(internal_campaign_id)
                for ad_set in ad_sets:
                    internal_ad_set_id = ad_set.get("id")
                    ads_payload: List[Dict[str, Any]] = []

                    if internal_ad_set_id is not None:
                        ads = self.meta_ad_repository.list_by_ad_set_internal_id(internal_ad_set_id)
                        for ad in ads:
                            ads_payload.append(
                                {
                                    "meta_ad_id": ad.get("meta_ad_id"),
                                    "creative_id": ad.get("creative_id"),
                                    "status": ad.get("status"),
                                    "created_at": self._format_timestamp(ad.get("created_at")),
                                    "updated_at": self._format_timestamp(ad.get("updated_at")),
                                }
                            )

                    ad_sets_payload.append(
                        {
                            "meta_ad_set_id": ad_set.get("meta_ad_set_id"),
                            "name": ad_set.get("name"),
                            "status": ad_set.get("status"),
                            "daily_budget_cents": ad_set.get("daily_budget_cents"),
                            "targeting": ad_set.get("targeting"),
                            "created_at": self._format_timestamp(ad_set.get("created_at")),
                            "updated_at": self._format_timestamp(ad_set.get("updated_at")),
                            "ads": ads_payload,
                        }
                    )

            hierarchy.append(
                {
                    "meta_campaign_id": campaign.get("meta_campaign_id"),
                    "name": campaign.get("name"),
                    "objective": campaign.get("objective"),
                    "status": campaign.get("status"),
                    "special_ad_categories": campaign.get("special_ad_categories"),
                    "created_at": self._format_timestamp(campaign.get("created_at")),
                    "updated_at": self._format_timestamp(campaign.get("updated_at")),
                    "ad_sets": ad_sets_payload,
                }
            )

        return hierarchy

    def _normalize_campaign(self, remote: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "meta_campaign_id": remote.get("id"),
            "name": remote.get("name"),
            "objective": remote.get("objective"),
            "status": remote.get("status"),
            "special_ad_categories": remote.get("special_ad_categories"),
            "created_at": self._parse_meta_datetime(remote.get("created_time")),
            "updated_at": self._parse_meta_datetime(remote.get("updated_time")),
        }

    def _normalize_ad_set(self, remote: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "meta_ad_set_id": remote.get("id"),
            "name": remote.get("name"),
            "status": remote.get("status"),
            "daily_budget_cents": self._parse_int(remote.get("daily_budget")),
            "targeting": remote.get("targeting"),
            "created_at": self._parse_meta_datetime(remote.get("created_time")),
            "updated_at": self._parse_meta_datetime(remote.get("updated_time")),
        }

    def _normalize_ad(self, remote: Dict[str, Any]) -> Dict[str, Any]:
        creative = remote.get("creative") or {}
        return {
            "meta_ad_id": remote.get("id"),
            "creative_id": creative.get("id"),
            "status": remote.get("status"),
            "created_at": self._parse_meta_datetime(remote.get("created_time")),
            "updated_at": self._parse_meta_datetime(remote.get("updated_time")),
        }

    @staticmethod
    def _normalize_ad_account_detail(detail: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not detail:
            return None
        account_id = detail.get("account_id")
        if not account_id:
            raw_id = detail.get("id")
            if raw_id:
                account_id = str(raw_id).replace("act_", "")
        if not account_id:
            return None
        business = detail.get("business") or {}
        return {
            "fb_ad_account_id": account_id,
            "name": detail.get("name") or "",
            "currency": detail.get("currency"),
            "timezone_name": detail.get("timezone_name"),
            "business_id": business.get("id") or detail.get("business_id"),
            "amount_spent": detail.get("amount_spent"),
            "balance": detail.get("balance"),
            "raw": detail,
        }

    def sync_company_campaigns(self, company_id: int) -> Dict[str, Any]:
        context = self._get_context(company_id)
        ad_account_id = context.get("ad_account_id")
        if not ad_account_id:
            raise ValueError("Company is not linked to a Meta ad account.")

        token = self._get_token(context)
        ad_account_detail = self.meta_ads_api.get_ad_account_detail(ad_account_id, token)
        normalized_account = self._normalize_ad_account_detail(ad_account_detail)
        if normalized_account:
            self.meta_ad_account_repository.upsert(normalized_account)
        campaigns_remote = self.meta_ads_api.get_campaigns(ad_account_id, token)
        summary = {"campaigns": 0, "ad_sets": 0, "ads": 0}

        for campaign_remote in campaigns_remote:
            normalized_campaign = self._normalize_campaign(campaign_remote)
            if not normalized_campaign.get("meta_campaign_id"):
                continue
            local_campaign = self.meta_campaign_repository.upsert(
                company_id=company_id,
                payload=normalized_campaign,
            )
            summary["campaigns"] += 1
            campaign_internal_id = local_campaign.get("id")
            if campaign_internal_id is None:
                continue

            ad_sets_remote = self.meta_ads_api.get_ad_sets(campaign_remote.get("id"), token)
            for ad_set_remote in ad_sets_remote:
                normalized_ad_set = self._normalize_ad_set(ad_set_remote)
                if not normalized_ad_set.get("meta_ad_set_id"):
                    continue
                local_ad_set = self.meta_ad_set_repository.upsert(
                    campaign_internal_id=campaign_internal_id,
                    payload=normalized_ad_set,
                )
                summary["ad_sets"] += 1
                ad_set_internal_id = local_ad_set.get("id")
                if ad_set_internal_id is None:
                    continue

                ads_remote = self.meta_ads_api.get_ads_for_ad_set(ad_set_remote.get("id"), token)
                for ad_remote in ads_remote:
                    normalized_ad = self._normalize_ad(ad_remote)
                    if not normalized_ad.get("meta_ad_id"):
                        continue
                    self.meta_ad_repository.upsert(
                        ad_set_internal_id=ad_set_internal_id,
                        payload=normalized_ad,
                    )
                    summary["ads"] += 1

        campaigns = self._build_campaign_hierarchy(company_id)

        return {
            "company_id": company_id,
            "summary": summary,
            "campaigns": campaigns,
        }

    def get_company_campaigns(self, company_id: int, sync: bool = False) -> Dict[str, Any]:
        if company_id is None:
            raise ValueError("company_id is required")
        if sync:
            self.sync_company_campaigns(company_id)
        campaigns = self._build_campaign_hierarchy(company_id)
        return {"data": campaigns}

    def update_campaign_status(self, campaign_id: str, status: str, company_id: int) -> Dict[str, Any]:
        if not campaign_id:
            raise ValueError("campaign_id is required")
        if not status:
            raise ValueError("status is required")
        context = self._get_context(company_id)
        token = self._get_token(context)
        response = self.meta_ads_api.update_campaign_status(campaign_id, status, token)
        try:
            self.meta_campaign_repository.upsert(
                company_id=company_id,
                payload={"meta_campaign_id": campaign_id, "status": status},
            )
        except Exception:
            self.logger.warning(
                "Failed to upsert campaign status locally for %s", campaign_id, exc_info=True
            )
        return response

    def update_ad_set_status(self, ad_set_id: str, status: str, company_id: int) -> Dict[str, Any]:
        if not ad_set_id:
            raise ValueError("ad_set_id is required")
        if not status:
            raise ValueError("status is required")
        context = self._get_context(company_id)
        token = self._get_token(context)
        response = self.meta_ads_api.update_ad_set_status(ad_set_id, status, token)
        try:
            ad_set_record = self.meta_ad_set_repository.get_by_meta_id(ad_set_id)
            campaign_internal_id = (ad_set_record or {}).get("campaign_id")
            if campaign_internal_id is not None:
                self.meta_ad_set_repository.upsert(
                    campaign_internal_id=campaign_internal_id,
                    payload={"meta_ad_set_id": ad_set_id, "status": status},
                )
        except Exception:
            self.logger.warning(
                "Failed to upsert ad set status locally for %s", ad_set_id, exc_info=True
            )
        return response

    def get_linked_company_assets(self) -> Dict[str, Any]:
        links = self.link_repository.list_links()
        if not links:
            return {"data": []}

        company_ids = [link["company_id"] for link in links if link.get("company_id") is not None]
        companies_map: Dict[int, Dict[str, Any]] = {}

        if company_ids:
            limit = max(len(company_ids), 1)
            companies, _ = self.companies_repository.list_companies(
                search=None,
                limit=limit,
                offset=0,
                company_ids=company_ids,
            )
            for company in companies:
                company_id = company.get("companyId")
                if company_id is None:
                    continue
                companies_map[company_id] = {
                    "name": company.get("name"),
                    "phone": company.get("phone"),
                }

        ad_account_cache: Dict[str, Dict[str, Any]] = {}
        response: List[Dict[str, Any]] = []

        for link in links:
            company_id = link.get("company_id")
            company_info = companies_map.get(company_id, {})

            ad_account_id = link.get("ad_account_id")
            ad_account_detail: Optional[Dict[str, Any]] = None
            if ad_account_id:
                cached_detail = ad_account_cache.get(ad_account_id)
                if cached_detail is None:
                    try:
                        cached_detail = self.meta_ads_api.get_ad_account_detail(
                            ad_account_id, link.get("system_user_token")
                        )
                    except Exception:
                        self.logger.warning(
                            "Linked assets: failed to fetch ad account detail for %s",
                            ad_account_id,
                            exc_info=True,
                        )
                        cached_detail = {}
                    ad_account_cache[ad_account_id] = cached_detail or {}

                detail = ad_account_cache.get(ad_account_id) or {}
                if detail:
                    normalized_account = self._normalize_ad_account_detail(detail)
                    if normalized_account:
                        try:
                            self.meta_ad_account_repository.upsert(normalized_account)
                        except Exception:
                            self.logger.warning(
                                "Linked assets: failed to persist ad account %s",
                                ad_account_id,
                                exc_info=True,
                            )
                    ad_account_detail = {
                        "id": detail.get("id") or f"act_{ad_account_id}",
                        "account_id": detail.get("account_id") or ad_account_id,
                        "name": detail.get("name"),
                        "currency": detail.get("currency"),
                        "timezone_name": detail.get("timezone_name"),
                    }
                else:
                    ad_account_detail = {
                        "id": f"act_{ad_account_id}",
                        "account_id": ad_account_id,
                        "name": None,
                        "currency": None,
                        "timezone_name": None,
                    }

            page_info: Optional[Dict[str, Any]] = None
            page_id = link.get("page_id")
            page_name = link.get("page_name")
            if page_id:
                page_info = {
                    "id": page_id,
                    "name": page_name,
                }

            whatsapp_info: Optional[Dict[str, Any]] = None
            wa_number_id = link.get("wa_number_id")
            if wa_number_id:
                whatsapp_info = {
                    "id": wa_number_id,
                    "display_phone_number": company_info.get("phone"),
                }

            campaigns = self._build_campaign_hierarchy(company_id)

            response.append(
                {
                    "company_id": company_id,
                    "company_name": company_info.get("name"),
                    "assets": {
                        "business_id": link.get("business_id"),
                        "ad_account": ad_account_detail,
                        "page": page_info,
                        "whatsapp_number": whatsapp_info,
                        "has_system_user_token": bool(link.get("system_user_token")),
                        "campaigns": campaigns,
                    },
                    "defaults": link.get("defaults") or {},
                }
            )

        return {"data": response}

    def verify_ad_account_link(self, ad_account_id: str) -> Dict[str, Any]:
        normalized = ad_account_id.replace("act_", "")
        link = self.link_repository.get_link_by_ad_account_id(normalized)

        if link:
            return {
                "linked": True,
                "company_id": link.get("company_id"),
                "linked_ad_account_id": link.get("ad_account_id"),
                "message": "La cuenta publicitaria ya está vinculada a una compañía.",
                "auto_link_attempted": False,
            }

        auto_result = self.auto_link_companies(ad_account_id=normalized)
        self.logger.info(
            "Verify ad account %s: auto-link attempted -> %s linked, %s skipped, %s errors",
            normalized,
            len(auto_result.get("linked", [])),
            len(auto_result.get("skipped", [])),
            len(auto_result.get("errors", [])),
        )

        for entry in auto_result.get("linked", []):
            if entry.get("ad_account_id") == normalized:
                return {
                    "linked": True,
                    "company_id": entry.get("company_id"),
                    "linked_ad_account_id": entry.get("ad_account_id"),
                    "message": "Se vinculó automáticamente la cuenta publicitaria con la compañía detectada.",
                    "auto_link_attempted": True,
                    "auto_link_result": auto_result,
                }

        return {
            "linked": False,
            "linked_ad_account_id": None,
            "message": "La cuenta publicitaria no está vinculada a ninguna compañía.",
            "auto_link_attempted": True,
            "auto_link_result": auto_result,
        }

    def get_client_ad_accounts(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        context: Optional[Dict[str, Any]] = None
        linked_ad_account: Optional[str] = None
        needs_link = False

        linked_page_id: Optional[str] = None
        linked_wa_number_id: Optional[str] = None
        business_id: Optional[str] = None

        if company_id is not None:
            try:
                context = self._get_context(company_id)
            except ValueError:
                needs_link = True
            else:
                if hasattr(context, "get"):
                    linked_ad_account = context.get("ad_account_id") or context.get("ad_account")
                    linked_page_id = context.get("page_id")
                    linked_wa_number_id = context.get("wa_number_id")
                    business_id = context.get("business_id")
                else:
                    linked_ad_account = getattr(context, "ad_account_id", None)
                    linked_page_id = getattr(context, "page_id", None)
                    linked_wa_number_id = getattr(context, "wa_number_id", None)
                    business_id = getattr(context, "business_id", None)
                if not linked_ad_account:
                    needs_link = True

        if company_id is not None and context is None:
            return {
                "data": [],
                "meta": {
                    "linked_ad_account_id": linked_ad_account,
                    "linked_page_id": linked_page_id,
                    "linked_wa_number_id": linked_wa_number_id,
                    "business_id": business_id,
                    "needs_link": True,
                    "message": "La compañía necesita vincular una cuenta publicitaria.",
                },
            }

        token = self._get_token(context)
        client_payload = self.meta_ads_api.get_client_ad_accounts(token)
        owned_payload = self.meta_ads_api.get_owned_ad_accounts(token)

        accounts: List[Dict[str, Any]] = []

        def _extend_from_payload(payload: Any):
            if isinstance(payload, dict):
                items = payload.get("data", [])
                if isinstance(items, list):
                    accounts.extend(items)
            elif isinstance(payload, list):
                accounts.extend(payload)

        _extend_from_payload(client_payload)
        _extend_from_payload(owned_payload)

        # Remove duplicates preferring the last occurrence
        unique_accounts: Dict[str, Dict[str, Any]] = {}
        for account in accounts:
            account_key = account.get("id") or account.get("account_id")
            if account_key:
                unique_accounts[str(account_key)] = account
        accounts = list(unique_accounts.values())

        def _normalize_ad_account(value: Optional[str]) -> Optional[str]:
            if not value:
                return None
            return value.replace("act_", "")

        normalized_linked = _normalize_ad_account(linked_ad_account)

        if normalized_linked:
            linked_match = any(
                _normalize_ad_account(account.get("account_id")) == normalized_linked
                or _normalize_ad_account(account.get("id")) == normalized_linked
                for account in accounts
            )
            if not linked_match:
                needs_link = True

        message = None
        if needs_link:
            message = "La compañía necesita vincular una cuenta publicitaria."

        return {
            "data": accounts,
            "meta": {
                "linked_ad_account_id": linked_ad_account,
                "linked_page_id": linked_page_id,
                "linked_wa_number_id": linked_wa_number_id,
                "business_id": business_id,
                "needs_link": needs_link,
                "message": message,
            },
        }

    def get_owned_ad_accounts(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        context: Optional[Dict[str, Any]] = None
        if company_id is not None:
            try:
                context = self._get_context(company_id)
            except ValueError:
                return {
                    "data": [],
                    "meta": {
                        "needs_link": True,
                        "message": "La compañía necesita vincular una cuenta publicitaria.",
                    },
                }
        token = self._get_token(context)
        payload = self.meta_ads_api.get_owned_ad_accounts(token)
        if isinstance(payload, dict) and "data" in payload:
            return payload
        if isinstance(payload, list):
            return {"data": payload}
        return {"data": []}

    def get_ad_account_detail(self, ad_account_id: str, company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.get_ad_account_detail(ad_account_id, token)

    def get_pages(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        context: Optional[Dict[str, Any]] = None
        token: Optional[str] = None

        if company_id is not None:
            try:
                context = self._get_context(company_id)
            except ValueError:
                return {
                    "data": [],
                    "meta": {
                        "needs_link": True,
                        "message": "La compañía necesita vincular una cuenta publicitaria para listar sus páginas.",
                    },
                }
        token = self._get_token(context)
        pages = self.meta_ads_api.get_pages(token)
        if isinstance(pages, dict) and "data" in pages:
            return pages
        if isinstance(pages, list):
            return {"data": pages}
        return {"data": []}

    def targeting_search(self, act_id: str, params: Dict[str, Any], company_id: Optional[int] = None) -> Dict[str, Any]:
        context = self._get_context(company_id) if company_id is not None else None
        token = self._get_token(context)
        return self.meta_ads_api.targeting_search(act_id, params, token)

    def link_company_ad_account(self, company_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        def _normalize_optional(value: Any) -> Optional[str]:
            if value is None:
                return None
            text = str(value).strip()
            return text or None

        business_id = _normalize_optional(payload.get("business_id"))
        if not business_id:
            raise ValueError("business_id is required")

        ad_account_id = _normalize_optional(payload.get("ad_account_id"))
        if not ad_account_id:
            raise ValueError("ad_account_id is required")
        normalized_ad_account = ad_account_id.replace("act_", "")
        if not normalized_ad_account:
            raise ValueError("ad_account_id is required")

        defaults = payload.get("defaults") or {}
        if defaults is None:
            defaults = {}
        if not isinstance(defaults, dict):
            raise ValueError("defaults must be an object")

        update_payload: Dict[str, Any] = {
            "business_id": business_id,
            "ad_account_id": normalized_ad_account,
            "page_id": _normalize_optional(payload.get("page_id")),
            "wa_number_id": _normalize_optional(payload.get("wa_number_id")),
            "system_user_token": _normalize_optional(payload.get("system_user_token")),
            "defaults": defaults,
        }

        return self.link_repository.link_company_ad_account(company_id, update_payload)

    def auto_link_companies(self, ad_account_id: Optional[str] = None) -> Dict[str, Any]:
        def _get_meta_callable(preferred: str, fallback: str):
            if hasattr(self.meta_ads_api, preferred):
                return getattr(self.meta_ads_api, preferred)
            return getattr(self.meta_ads_api, fallback)

        def _normalize_digits(value: Optional[str]) -> Optional[str]:
            if not value:
                return None
            digits = re.sub(r"\D", "", value)
            return digits or None

        def _normalize_ad_account_id(value: Optional[str]) -> Optional[str]:
            if not value:
                return None
            return str(value).replace("act_", "")

        target_ad_account_id = _normalize_ad_account_id(ad_account_id)

        def _normalize_text(value: Optional[str]) -> str:
            return re.sub(r"\W+", "", (value or "")).lower()

        def _resolve_ad_account(company_name: str, business_id: Optional[str]) -> Optional[Dict[str, Any]]:
            if business_id:
                candidates = [acct for acct in ad_accounts if acct.get("business_id") == business_id]
            else:
                candidates = ad_accounts.copy()

            if business_id and not candidates:
                return None
            if not candidates:
                return None

            if target_ad_account_id:
                for account in candidates:
                    if account.get("account_id") == target_ad_account_id:
                        return account
                return None

            if len(candidates) == 1:
                return candidates[0]

            normalized_company = _normalize_text(company_name)
            if not normalized_company:
                return None

            for account in candidates:
                account_name = account.get("normalized_name", "")
                if normalized_company in account_name or account_name in normalized_company:
                    return account

            return None

        token = None
        results: Dict[str, List[Dict[str, Any]]] = {"linked": [], "skipped": [], "errors": []}

        get_businesses = _get_meta_callable("get_user_businesses", "_get_user_businesses")
        get_owned_wabas = _get_meta_callable(
            "get_owned_whatsapp_business_accounts", "_get_owned_whatsapp_business_accounts"
        )
        get_client_wabas = _get_meta_callable(
            "get_client_whatsapp_business_accounts", "_get_client_whatsapp_business_accounts"
        )
        get_phone_numbers = _get_meta_callable("get_phone_numbers", "_get_phone_numbers")
        get_waba_detail = _get_meta_callable(
            "get_whatsapp_business_account", "_get_whatsapp_business_account"
        )

        ad_accounts: List[Dict[str, Any]] = []
        businesses_payload: Optional[Dict[str, Any]] = None

        if target_ad_account_id:
            try:
                detail = self.meta_ads_api.get_ad_account_detail(target_ad_account_id, token)
            except Exception as exc:
                self.logger.exception("Auto-link: failed to fetch ad account detail for %s", target_ad_account_id)
                raise ValueError(f"Failed to fetch ad account detail: {exc}") from exc

            business_info = detail.get("business") or {}
            business_id = business_info.get("id") or detail.get("business_id")
            ad_accounts.append(
                {
                    "account_id": target_ad_account_id,
                    "name": detail.get("name"),
                    "normalized_name": _normalize_text(detail.get("name")),
                    "business_id": business_id,
                }
            )
            if business_id:
                businesses_payload = {"data": [{"id": business_id, "name": business_info.get("name")}]}
            self.logger.info(
                "Auto-link: targeting ad account %s (business=%s)",
                target_ad_account_id,
                business_id,
            )
        else:
            try:
                ad_accounts_payload: List[Dict[str, Any]] = []
                try:
                    owned = self.meta_ads_api.get_owned_ad_accounts(token)
                    if isinstance(owned, dict):
                        ad_accounts_payload.extend(owned.get("data", []))
                except Exception:
                    pass

                try:
                    client = self.meta_ads_api.get_client_ad_accounts(token)
                    if isinstance(client, dict):
                        ad_accounts_payload.extend(client.get("data", []))
                except Exception:
                    pass

                adapter_business_id = getattr(self.meta_ads_api, "business_id", None)
                for account in ad_accounts_payload:
                    account_id = _normalize_ad_account_id(account.get("account_id") or account.get("id"))
                    if not account_id:
                        continue
                    ad_accounts.append(
                        {
                            "account_id": account_id,
                            "name": account.get("name"),
                            "normalized_name": _normalize_text(account.get("name")),
                            "business_id": (account.get("business") or {}).get("id") or adapter_business_id,
                        }
                    )
                self.logger.info("Auto-link: resolved %s ad accounts", len(ad_accounts))
            except Exception as exc:
                self.logger.exception("Auto-link: failed to resolve ad accounts")
                raise ValueError(f"Failed to resolve ad accounts: {exc}") from exc

        if businesses_payload is None:
            try:
                businesses_payload = get_businesses(token)
            except Exception as exc:
                self.logger.exception("Auto-link: failed to fetch businesses from Meta")
                raise ValueError(f"Failed to fetch Meta businesses: {exc}") from exc

        business_list = businesses_payload.get("data", []) if isinstance(businesses_payload, dict) else []
        target_business_ids: Optional[set[str]] = None
        if target_ad_account_id:
            target_business_ids = {
                entry.get("business_id")
                for entry in ad_accounts
                if entry.get("business_id")
            }
        self.logger.info(
            "Auto-link: scanning %s businesses (targeted=%s)",
            len(business_list),
            target_business_ids,
        )

        processed_companies: set[int] = set()

        for business in business_list:
            business_id = business.get("id")
            if not business_id:
                continue
            if target_business_ids and business_id not in target_business_ids:
                continue
            self.logger.info("Auto-link: processing business %s", business_id)

            waba_collections: List[Dict[str, Any]] = []
            try:
                waba_collections.append(get_owned_wabas(business_id, token))
            except Exception as exc:
                self.logger.warning(
                    "Auto-link: failed to fetch owned WABAs for business %s: %s",
                    business_id,
                    exc,
                )
                results["errors"].append(
                    {
                        "business_id": business_id,
                        "error": f"failed_to_fetch_owned_wabas: {exc}",
                    }
                )
            try:
                waba_collections.append(get_client_wabas(business_id, token))
            except Exception as exc:
                self.logger.warning(
                    "Auto-link: failed to fetch client WABAs for business %s: %s",
                    business_id,
                    exc,
                )
                results["errors"].append(
                    {
                        "business_id": business_id,
                        "error": f"failed_to_fetch_client_wabas: {exc}",
                    }
                )

            has_wabas = False
            for collection in waba_collections:
                for waba in (collection or {}).get("data", []):
                    has_wabas = True
                    waba_id = waba.get("id")
                    if not waba_id:
                        continue
                    waba_owner_business_id: Optional[str] = None
                    try:
                        detail = get_waba_detail(waba_id, token)
                        owner_info = (detail or {}).get("owner_business_info") or {}
                        waba_owner_business_id = (
                            owner_info.get("business_id")
                            or owner_info.get("id")
                        )
                    except Exception as exc:
                        self.logger.warning(
                            "Auto-link: failed to resolve owner for waba %s: %s",
                            waba_id,
                            exc,
                        )

                    if not waba_owner_business_id:
                        self.logger.warning(
                            "Auto-link: skipping waba %s because owner business could not be resolved",
                            waba_id,
                        )
                        results["errors"].append(
                            {
                                "waba_id": waba_id,
                                "error": "missing_owner_business",
                            }
                        )
                        continue
#                     waba_owner_business_id = business_id

                    self.logger.info(
                        "Auto-link: processing waba %s (owner_business=%s)",
                        waba_id,
                        waba_owner_business_id,
                    )
                    try:
                        phone_numbers = get_phone_numbers(waba_id, token)
                    except Exception as exc:
                        self.logger.exception(
                            "Auto-link: failed to fetch phone numbers for WABA %s", waba_id
                        )
                        results["errors"].append(
                            {
                                "business_id": business_id,
                                "waba_id": waba_id,
                                "error": f"failed_to_fetch_numbers: {exc}",
                            }
                        )
                        continue

                    entries: List[Dict[str, Any]] = []
                    if isinstance(phone_numbers, dict):
                        entries = phone_numbers.get("data", []) or []
                    elif isinstance(phone_numbers, list):
                        entries = phone_numbers

                    self.logger.info(
                        "Auto-link: fetched %s phone numbers for WABA %s (business=%s)",
                        len(entries),
                        waba_id,
                        business_id,
                    )

                    for phone_entry in entries:
                        wa_number_id = phone_entry.get("id")
                        display_phone = phone_entry.get("display_phone_number")
                        self.logger.debug(
                            "Auto-link: evaluating number %s (wa_id=%s)",
                            display_phone,
                            wa_number_id,
                        )
                        candidates = self.companies_repository.find_candidates_by_whatsapp(
                            wa_number_id=wa_number_id,
                        )
                        self.logger.info(
                            "Auto-link: candidate search -> wa_number_id=%s, candidates=%s",
                            wa_number_id,
                            [candidate["company_id"] for candidate in candidates],
                        )

                        if not candidates:
                            self.logger.info(
                                "Auto-link: no company match for number %s (wa_id=%s)",
                                display_phone,
                                wa_number_id,
                            )
                            results["skipped"].append(
                                {
                                    "waba_id": waba_id,
                                    "wa_number_id": wa_number_id,
                                    "phone": display_phone,
                                    "reason": "no_company_match",
                                }
                            )
                            continue

                        if len(candidates) > 1:
                            self.logger.warning(
                                "Auto-link: multiple company matches for %s (wa_id=%s): %s",
                                display_phone,
                                wa_number_id,
                                [candidate["company_id"] for candidate in candidates],
                            )
                            results["skipped"].append(
                                {
                                    "waba_id": waba_id,
                                    "wa_number_id": wa_number_id,
                                    "phone": display_phone,
                                    "reason": "multiple_company_matches",
                                    "company_ids": [candidate["company_id"] for candidate in candidates],
                                }
                            )
                            continue

                        company_candidate = candidates[0]
                        company_id = company_candidate["company_id"]
                        if company_candidate.get("has_meta_link") or company_id in processed_companies:
                            self.logger.info(
                                "Auto-link: company %s already linked or processed",
                                company_id,
                            )
                            results["skipped"].append(
                                {
                                    "waba_id": waba_id,
                                    "company_id": company_id,
                                    "wa_number_id": wa_number_id,
                                    "phone": display_phone,
                                    "reason": "already_linked",
                                }
                            )
                            continue

                        ad_account = _resolve_ad_account(
                            company_candidate.get("name"), waba_owner_business_id
                        )
                        if not ad_account:
                            self.logger.error(
                                "Auto-link: missing ad account match for company %s within business %s",
                                company_id,
                                business_id,
                            )
                            results["errors"].append(
                                {
                                    "company_id": company_id,
                                    "waba_id": waba_id,
                                    "wa_number_id": wa_number_id,
                                    "error": "no_ad_account_match",
                                }
                            )
                            continue

                        payload = {
                            "business_id": waba_owner_business_id,
                            "ad_account_id": ad_account["account_id"],
                            "page_id": None,
                            "wa_number_id": wa_number_id,
                            "system_user_token": None,
                            "defaults": {},
                        }

                        try:
                            link = self.link_repository.link_company_ad_account(company_id, payload)
                        except Exception as exc:
                            self.logger.exception(
                                "Auto-link: failed to link company %s", company_id
                            )
                            results["errors"].append(
                                {
                                    "company_id": company_id,
                                    "wa_number_id": wa_number_id,
                                    "error": str(exc),
                                }
                            )
                            continue

                        processed_companies.add(company_id)
                        self.logger.info(
                            "Auto-link: linked company %s with ad account %s",
                            company_id,
                            ad_account["account_id"],
                        )
                        results["linked"].append(
                            {
                                "company_id": company_id,
                                "company_name": company_candidate.get("name"),
                                "wa_number_id": wa_number_id,
                                "phone": display_phone,
                                "business_id": business_id,
                                "ad_account_id": ad_account["account_id"],
                                "link": link,
                            }
                        )

            if not has_wabas:
                results["skipped"].append(
                    {
                        "business_id": business_id,
                        "waba_id": None,
                        "reason": "no_wabas",
                    }
                )

        return results

    def get_companies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        raw_limit = params.get("limit")
        raw_offset = params.get("offset")
        search = params.get("search")
        raw_company_ids = params.get("company_ids") or params.get("company_ids[]")

        try:
            limit = int(raw_limit) if raw_limit is not None else 50
        except (TypeError, ValueError) as exc:
            raise ValueError("limit must be an integer") from exc

        try:
            offset = int(raw_offset) if raw_offset is not None else 0
        except (TypeError, ValueError) as exc:
            raise ValueError("offset must be an integer") from exc

        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        company_ids: Optional[List[int]] = None
        if raw_company_ids:
            if isinstance(raw_company_ids, (list, tuple)):
                raw_values = raw_company_ids
            else:
                raw_values = str(raw_company_ids).split(",")
            try:
                company_ids = [int(value) for value in raw_values if str(value).strip()]
            except (TypeError, ValueError) as exc:
                raise ValueError("company_ids must contain integers") from exc

        companies, total = self.companies_repository.list_companies(
            search=search,
            limit=limit,
            offset=offset,
            company_ids=company_ids,
        )

        return {
            "data": companies,
            "meta": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "returned": len(companies),
            },
        }

    def get_whatsapp_numbers(self, company_id: Optional[int] = None) -> Dict[str, Any]:
        context: Optional[Dict[str, Any]] = None
        token: Optional[str] = None

        if company_id is not None:
            try:
                context = self._get_context(company_id)
            except ValueError:
                return {
                    "data": [],
                    "meta": {
                        "needs_link": True,
                        "message": "La compañía necesita vincular una cuenta publicitaria para listar números de WhatsApp.",
                    },
                }

        token = self._get_token(context)

        businesses = self.meta_ads_api.get_user_businesses(token)
        all_phone_numbers = []

        for business in businesses.get("data", []):
            business_id = business.get("id")
            wabas = self.meta_ads_api.get_owned_whatsapp_business_accounts(business_id, token)

            for waba in wabas.get("data", []):
                waba_id = waba.get("id")
                phone_numbers = self.meta_ads_api.get_phone_numbers(waba_id, token)
                all_phone_numbers.extend(phone_numbers.get("data", []))

        return {"data": all_phone_numbers}

    def create_campaign_draft(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.meta_ads_api.create_campaign_draft(payload)
