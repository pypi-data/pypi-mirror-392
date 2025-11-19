"""Domain contracts for authentication."""

from .entities import User
from .ports import AuthRepository, UserRepository

__all__ = ["User", "AuthRepository", "UserRepository"]
