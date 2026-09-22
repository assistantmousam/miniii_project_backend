from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, status


# ============================================================
# IN-MEMORY RATE LIMIT STORAGE
# ============================================================

_login_attempts: dict[str, deque[float]] = defaultdict(deque)
_register_attempts: dict[str, deque[float]] = defaultdict(deque)

_last_cleanup = monotonic()


# ============================================================
# CLEANUP
# ============================================================

def _cleanup() -> None:
    global _last_cleanup

    now = monotonic()

    # Cleanup once every 60 seconds
    if now - _last_cleanup < 60:
        return

    cutoff = now - 3600

    for storage in (
        _login_attempts,
        _register_attempts,
    ):
        for key in list(storage.keys()):
            attempts = storage[key]

            while attempts and attempts[0] < cutoff:
                attempts.popleft()

            if not attempts:
                del storage[key]

    _last_cleanup = now


# ============================================================
# GENERIC RATE LIMIT CHECK
# ============================================================

def check_rate_limit(
    storage: dict[str, deque[float]],
    key: str,
    max_attempts: int,
    window_seconds: int = 60,
) -> None:

    _cleanup()

    now = monotonic()
    attempts = storage[key]

    # Remove attempts outside the current window
    cutoff = now - window_seconds

    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    # Rate limit exceeded
    if len(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    # Record this request
    attempts.append(now)


# ============================================================
# LOGIN RATE LIMIT
# ============================================================

def check_login_rate_limit(
    key: str,
    max_attempts: int = 5,
    window_seconds: int = 60,
) -> None:

    check_rate_limit(
        storage=_login_attempts,
        key=key,
        max_attempts=max_attempts,
        window_seconds=window_seconds,
    )


# ============================================================
# REGISTER RATE LIMIT
# ============================================================

def check_register_rate_limit(
    key: str,
    max_attempts: int = 3,
    window_seconds: int = 60,
) -> None:

    check_rate_limit(
        storage=_register_attempts,
        key=key,
        max_attempts=max_attempts,
        window_seconds=window_seconds,
    )


# ============================================================
# GENERIC BOOLEAN RATE LIMIT
# ============================================================

_requests: dict[str, deque[float]] = defaultdict(deque)


def is_rate_limited(
    key: str,
    limit: int = 60,
    window: int = 60,
) -> bool:

    _cleanup()

    now = monotonic()
    attempts = _requests[key]

    cutoff = now - window

    while attempts and attempts[0] < cutoff:
        attempts.popleft()

    if len(attempts) >= limit:
        return True

    attempts.append(now)

    return False


