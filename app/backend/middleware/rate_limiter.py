"""SlowAPI rate limiter — 20 requests/minute per IP on /query."""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit],
)
