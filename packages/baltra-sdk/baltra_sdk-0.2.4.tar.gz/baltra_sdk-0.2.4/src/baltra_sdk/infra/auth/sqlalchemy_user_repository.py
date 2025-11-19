from typing import Iterable, Dict, Optional

from baltra_sdk.domain.auth.ports import UserRepository
from baltra_sdk.domain.auth.entities import User as UserEntity
from baltra_sdk.legacy.dashboards_folder.models import db, Users as UserModel
from sqlalchemy.exc import IntegrityError

class SQLAlchemyUserRepository(UserRepository):

    def get_by_cognito_sub(self, cognito_sub: str) -> UserEntity | None:
        user_model = UserModel.query.filter_by(cognito_sub=cognito_sub).first()
        if not user_model:
            return None
        
        return self._to_entity(user_model)

    def create_user(self, user_data: dict) -> UserEntity:
        # Check for required fields from the Cognito webhook data
        cognito_sub = user_data.get("cognito_sub")
        email = user_data.get("email")
        if not cognito_sub or not email:
            raise ValueError("Missing cognito_sub or email in user_data")

        new_user = UserModel(
            cognito_sub=cognito_sub,
            email=email,
            # Roles can be assigned here, defaulting to ['user']
            roles=user_data.get("roles", ["user"])
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            return self._to_entity(new_user)
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"User with email '{email}' or sub '{cognito_sub}' already exists.")

    def _to_entity(self, user_model: UserModel) -> UserEntity:
        """Converts a SQLAlchemy UserModel to a domain UserEntity."""
        return UserEntity(
            id=user_model.id,
            cognito_sub=user_model.cognito_sub,
            email=user_model.email,
            roles=user_model.roles
        )

    def get_latest_non_admin_by_company(self, company_id: str) -> UserEntity | None:
        raise NotImplementedError("SQLAlchemyUserRepository does not support Cognito last login lookups.")

    def get_latest_non_admin_by_companies(self, company_ids: Iterable[str]) -> Dict[str, Optional[UserEntity]]:
        raise NotImplementedError("SQLAlchemyUserRepository does not support Cognito last login lookups.")
