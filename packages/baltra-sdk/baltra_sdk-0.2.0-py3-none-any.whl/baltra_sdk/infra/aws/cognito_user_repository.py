import logging
from datetime import datetime

import boto3
from typing import Iterable, Optional, Tuple, List, Dict
from baltra_sdk.domain.users.user import User
from baltra_sdk.domain.users.user_repository import UserRepository
from baltra_sdk.infra.aws.cognito_config import load_cognito_config
from botocore.exceptions import ClientError

class CognitoUserRepository(UserRepository):
    def __init__(self):
        self._config = load_cognito_config()
        session = boto3.Session(**self._config.boto_session_kwargs())
        self.client = session.client("cognito-idp")
        self.user_pool_id = self._config.user_pool_id
        self.email_domain_suffix = (self._config.email_domain_suffix or "").lower().strip()
        self.user_filter_expression = self._config.user_filter_expression

    def _map_user(self, raw: dict) -> User:
        attr_map = {a["Name"]: a["Value"] for a in raw.get("Attributes", [])}
        # Normaliza claves típicas
        email = attr_map.get("email")
        status = raw.get("UserStatus")
        enabled = raw.get("Enabled", False)

        return User(
            username=raw.get("Username"),
            email=email,
            status=status,
            enabled=enabled,
            attributes=attr_map,
        )

    def _has_suffix(self, email: Optional[str], suffix: str) -> bool:
        if not email:
            return False
        suffix = suffix.lower().lstrip("@")
        return email.lower().endswith(suffix)

    def _parse_last_login(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            logging.debug(f"No se pudo parsear custom:last_login='{value}' como ISO8601.")
            return None

    def _is_admin(self, value: Optional[str]) -> bool:
        if value is None:
            return False
        normalized = value.strip().lower()
        return normalized in {"true", "1", "yes"}

    def _iterate_users(
        self,
        filter_expression: Optional[str],
        page_limit: int = 60,
    ) -> Iterable[dict]:
        pagination_token: Optional[str] = None
        active_filter = filter_expression if filter_expression is not None else self.user_filter_expression
        while True:
            params = {
                "UserPoolId": self.user_pool_id,
                "Limit": min(max(page_limit, 1), 60),
            }
            if active_filter:
                params["Filter"] = active_filter
            if pagination_token:
                params["PaginationToken"] = pagination_token

            resp = self.client.list_users(**params)
            raw_users: List[dict] = resp.get("Users", [])
            for raw in raw_users:
                yield raw

            pagination_token = resp.get("PaginationToken")
            if not pagination_token:
                break

    def list_users(
        self,
        email_suffix: Optional[str] = None,
        limit: int = 50,
        pagination_token: Optional[str] = None,
    ) -> Tuple[Iterable[User], Optional[str]]:
        params = {
            "UserPoolId": self.user_pool_id,
            "Limit": min(max(limit, 1), 60),
        }
        if pagination_token:
            params["PaginationToken"] = pagination_token

        resp = self.client.list_users(**params)
        raw_users: List[dict] = resp.get("Users", [])
        next_token: Optional[str] = resp.get("PaginationToken")

        mapped = [self._map_user(u) for u in raw_users]
        if email_suffix:
            mapped = [u for u in mapped if self._has_suffix(u.email, email_suffix)]

        return mapped, next_token

    def get_latest_non_admin_by_companies(self, company_ids: Iterable[str]) -> Dict[str, Optional[User]]:
        normalized_ids = {str(cid) for cid in company_ids if cid is not None and str(cid).strip()}
        if not normalized_ids:
            return {}

        latest_by_company: Dict[str, Tuple[Optional[User], Optional[datetime]]] = {
            cid: (None, None) for cid in normalized_ids
        }

        domain_suffix = self.email_domain_suffix
        filter_expression = self.user_filter_expression or ""

        def process_candidates(candidate_iterable: Iterable[dict]) -> None:
            for raw in candidate_iterable:
                attr_map = {a["Name"]: a["Value"] for a in raw.get("Attributes", [])}
                company_attr = attr_map.get("custom:company_id")
                if company_attr not in normalized_ids:
                    continue

                email_value = (attr_map.get("email") or "").lower()
                if domain_suffix and not email_value.endswith(domain_suffix):
                    continue

                if self._is_admin(attr_map.get("custom:is_admin")):
                    continue

                last_login = self._parse_last_login(attr_map.get("custom:last_login"))
                if last_login is None:
                    continue

                _, stored_ts = latest_by_company.get(company_attr, (None, None))
                if stored_ts is None or last_login > stored_ts:
                    latest_by_company[company_attr] = (self._map_user(raw), last_login)

        try:
            iterator = self._iterate_users(filter_expression if filter_expression else None)
            process_candidates(iterator)
        except ClientError as err:
            code = err.response.get("Error", {}).get("Code")
            if code == "InvalidParameterException" and filter_expression:
                logging.warning(
                    "CognitoUserRepository: el filtro '%s' no es aceptado por Cognito (InvalidParameter). "
                    "Se realizará filtrado local sin filtro remoto.",
                    filter_expression,
                )
                process_candidates(self._iterate_users(filter_expression=""))
            else:
                raise

        if filter_expression and not any(user for user, _ in latest_by_company.values()):
            logging.info(
                "CognitoUserRepository: sin resultados usando el filtro '%s'. Reintentando sin filtro remoto.",
                filter_expression,
            )
            process_candidates(self._iterate_users(filter_expression=""))

        result: Dict[str, Optional[User]] = {}
        for cid, (user, _) in latest_by_company.items():
            if user:
                logging.info(
                    "CognitoUserRepository: usuario encontrado (company_id=%s, usuario=%s, last_login=%s)",
                    cid,
                    user.username,
                    user.attributes.get("custom:last_login"),
                )
            else:
                logging.info(
                    "CognitoUserRepository: sin usuarios no-admin con last_login para company_id=%s",
                    cid,
                )
            result[cid] = user
        return result

    def get_latest_non_admin_by_company(self, company_id: str) -> Optional[User]:
        mapping = self.get_latest_non_admin_by_companies([company_id])
        return mapping.get(str(company_id))
