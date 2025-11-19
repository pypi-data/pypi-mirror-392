from typing import Dict, List, Optional

from .base import AuthContext, AuthProvider, UserProfile


class DummyAuthProvider(AuthProvider):
    """Dummy provider for local dev and testing.

    Authorization header format: "Bearer <tenant_id>:<user_id>"

    """

    def __init__(self, users: Optional[Dict[str, Dict]] = None):
        self._users = users or {}

    def verify_token(self, token: str) -> AuthContext:
        if not token or ":" not in token:
            raise ValueError("Invalid dummy token. Expected '<tenant>:<user>' format.")

        tenant_id, user_id = token.split(":", 1)

        return AuthContext(
            user_id=user_id, tenant_id=tenant_id, auth_provider="dummy", claims={}
        )

    def get_user(self, user_id: str) -> UserProfile:
        if user_id in self._users:
            record = self._users[user_id]

            return UserProfile(
                user_id=user_id,
                name=record.get("name", user_id.capitalize()),
                email=record.get("email", f"{user_id}@example.com"),
                photo_url=record.get("photo_url", None),
            )

        return UserProfile(
            user_id=user_id,
            name=user_id.capitalize(),
            email=f"{user_id}@example.com",
            photo_url=f"https://picsum.photos/id/64/500/500",
        )

    def get_users(self, user_ids: List[str]) -> List[UserProfile]:
        return [self.get_user(uid) for uid in user_ids]
