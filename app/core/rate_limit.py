from collections import defaultdict
from time import monotonic

from fastapi import HTTPException, status


_login_attempts: dict[str, list[float]] = defaultdict(list)

register_attempts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(
    storage: dict[str, list[float]],
    key: str,
    max_attempts: int,
    window_seconds: int = 60,
) -> None:
    now = monotonic()

    attempts = storage[key]

    attempts[:] = [
        timestamp
        for timestamp in attempts
        if now - timestamp < window_seconds
    ]

    if len(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    attempts.append(now)


def check_login_rate_limit(
    key: str,
    max_attempts: int,
) -> None:
    check_rate_limit(
        storage=_login_attempts,
        key=key,
        max_attempts=max_attempts,
    )


def check_register_rate_limit(
    key: str,
    max_attempts: int,
) -> None:
    check_rate_limit(
        storage=register_attempts,
        key=key,
        max_attempts=max_attempts,
    )