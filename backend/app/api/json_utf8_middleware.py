"""Ensure JSON responses explicitly advertise UTF-8 for legacy HTTP clients."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware


class JsonUtf8ContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        content_type = response.headers.get("content-type", "")
        if content_type.lower() == "application/json":
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response
