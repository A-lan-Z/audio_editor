from __future__ import annotations

import os

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

DEFAULT_MAX_BODY_BYTES = 100 * 1024 * 1024


def max_body_bytes() -> int:
    configured = os.environ.get("TEXTAUDIO_MAX_BODY_BYTES")
    if configured is None:
        return DEFAULT_MAX_BODY_BYTES
    try:
        return int(configured)
    except ValueError:
        return DEFAULT_MAX_BODY_BYTES


class MaxBodySizeMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        content_length = headers.get("content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                length = 0
            limit = max_body_bytes()
            if length > limit:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "detail": (
                            f"Request too large ({length} bytes). Max {limit} bytes."
                        ),
                    },
                )
                await response(scope, receive, send)
                return

        await self._app(scope, receive, send)
