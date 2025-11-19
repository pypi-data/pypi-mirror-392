from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Dict
from baltra_sdk.domain.users.user import User

class UserRepository(ABC):
    @abstractmethod
    def list_users(
        self,
        email_suffix: Optional[str] = None,
        limit: int = 50,
        pagination_token: Optional[str] = None,
    ) -> Tuple[Iterable[User], Optional[str]]:
        """Retrieves a list of users with optional email suffix filtering and pagination."""
        raise NotImplementedError

    @abstractmethod
    def get_latest_non_admin_by_company(self, company_id: str) -> Optional[User]:
        """Returns the most recent non-admin user for the given company."""
        raise NotImplementedError

    @abstractmethod
    def get_latest_non_admin_by_companies(self, company_ids: Iterable[str]) -> Dict[str, Optional[User]]:
        """Returns the most recent non-admin user per company for the provided company IDs."""
        raise NotImplementedError
