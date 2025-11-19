from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Dict

from flask import current_app


def _get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Resolve configuration values by checking Flask's config first and falling back to environment variables.
    """
    value = None
    try:
        value = current_app.config.get(key)
    except Exception:
        value = None

    if value is None:
        value = os.getenv(key, default)

    return value


@dataclass(frozen=True)
class CognitoConfig:
    region: str
    user_pool_id: str
    app_client_id: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    email_domain_suffix: Optional[str] = None
    user_filter_expression: Optional[str] = None

    @property
    def issuer(self) -> str:
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/.well-known/jwks.json"

    def boto_session_kwargs(self) -> Dict[str, str]:
        """
        Build the keyword arguments required to initialize a boto3 session for Cognito.
        """
        kwargs: Dict[str, str] = {"region_name": self.region}
        if self.access_key_id and self.secret_access_key:
            kwargs.update(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
            )
        return kwargs


def load_cognito_config(require_app_client_id: bool = False) -> CognitoConfig:
    """
    Load a unified Cognito configuration, ensuring consistent access across infrastructure adapters.
    """
    region = _get_config_value("COGNITO_REGION") or _get_config_value("AWS_REGION")
    if not region:
        raise ValueError("Cognito region is not configured. Set COGNITO_REGION or AWS_REGION.")

    user_pool_id = _get_config_value("COGNITO_USER_POOL_ID")
    if not user_pool_id:
        raise ValueError("COGNITO_USER_POOL_ID is not configured.")

    app_client_id = _get_config_value("COGNITO_APP_CLIENT_IDCOGNITO_EMAIL_DOMAIN_SUFFIX")
    if require_app_client_id and not app_client_id:
        raise ValueError("COGNITO_APP_CLIENT_ID is required but not configured.")

    access_key_id = _get_config_value("AWS_ACCESS_KEY_ID")
    secret_access_key = _get_config_value("AWS_SECRET_ACCESS_KEY")
    email_domain_suffix = _get_config_value("COGNITO_EMAIL_DOMAIN_SUFFIX")
    user_filter_expression = _get_config_value("COGNITO_USER_FILTER_EXPRESSION")

    return CognitoConfig(
        region=region,
        user_pool_id=user_pool_id,
        app_client_id=app_client_id,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        email_domain_suffix=email_domain_suffix,
        user_filter_expression=user_filter_expression,
    )
