"""Authentication ports."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from .entities import User


class AuthRepository(ABC):
    @abstractmethod
    def get_user_from_token(self, token: str) -> Optional[dict]:
        """Validate a token and return decoded payload if valid."""
        raise NotImplementedError


class UserRepository(ABC):
    @abstractmethod
    def get_by_cognito_sub(self, cognito_sub: str) -> Optional[User]:
        """Retrieve a user by Cognito subject."""
        raise NotImplementedError

    @abstractmethod
    def create_user(self, user_data: dict) -> User:
        """Persist a user using data provided by external identity provider."""
        raise NotImplementedError
