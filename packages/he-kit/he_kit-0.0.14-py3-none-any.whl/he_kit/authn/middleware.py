from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth_provider = request.app.state.auth_provider

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Missing token"}, status_code=401)

        token = auth_header[len("Bearer ") :].strip()

        try:
            auth_context = auth_provider.verify_token(token)
        except Exception as exc:
            return JSONResponse({"detail": str(exc)}, status_code=401)

        request.state.auth = auth_context
        return await call_next(request)
