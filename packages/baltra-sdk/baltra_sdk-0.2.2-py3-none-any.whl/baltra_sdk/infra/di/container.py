# Python
from __future__ import annotations
from flask import current_app
from baltra_sdk.domain.storage.storage_repository import StorageRepository
from baltra_sdk.infra.aws.s3_repository import S3Repository
from baltra_sdk.domain.onboarding.ports import OnboardingRepository
from baltra_sdk.infra.onboarding.sqlalchemy_repository import SqlAlchemyOnboardingRepository
from baltra_sdk.domain.auth.ports import AuthRepository
from baltra_sdk.infra.auth.cognito_repository import CognitoAuthRepository

def get_storage_repository() -> StorageRepository:
    """
    Factory to provide the default StorageRepository implementation.
    """
    try:
        region = current_app.config.get("AWS_REGION")
    except Exception:
        region = None
    return S3Repository(region_name=region)

def get_screening_bucket() -> str:
    try:
        return current_app.config.get("S3_BUCKET_SCREENING", "screeningbucket")
    except Exception:
        return "screeningbucket"


def get_onboarding_repository() -> OnboardingRepository:
    """Factory to provide default OnboardingRepository implementation (SQLAlchemy)."""
    return SqlAlchemyOnboardingRepository()


def get_auth_repository() -> AuthRepository:
    """Factory to provide the default AuthRepository implementation."""
    return CognitoAuthRepository()
