from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class AuthContext:
    user_id: str
    tenant_id: str | None
    claims: dict[str, Any]
    auth_provider: str


@dataclass
class UserProfile:
    user_id: str
    name: str
    email: str
    photo_url: Optional[str]


class AuthProvider(ABC):
    @abstractmethod
    def verify_token(self, token: str) -> AuthContext:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> UserProfile:
        pass

    @abstractmethod
    def get_users(self, user_ids: List[str]) -> List[UserProfile]:
        pass
