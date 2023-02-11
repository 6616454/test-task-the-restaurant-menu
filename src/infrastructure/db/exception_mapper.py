from functools import wraps
from typing import Callable, Any

from sqlalchemy.exc import IntegrityError

from src.domain.common.exceptions.repo import UniqueError


def exception_mapper(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any):
        try:
            return await func(*args, **kwargs)
        except IntegrityError:
            raise UniqueError

    return wrapped
