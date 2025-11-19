from typing import Dict, Any, Optional
from baltra_sdk.domain.users.user_repository import UserRepository

class GetUsersService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def execute(
        self,
        email_suffix: Optional[str],
        limit: int,
        page_token: Optional[str],
    ) -> Dict[str, Any]:
        users, next_token = self._repo.list_users(
            email_suffix=email_suffix,
            limit=limit,
            pagination_token=page_token
        )

        return {
            "items": [
                {
                    "username": u.username,
                    "email": u.email,
                    "status": u.status,
                    "enabled": u.enabled,
                    "attributes": u.attributes,
                }
                for u in users
            ],
            "next_token": next_token,
        }
