from collections.abc import Callable
from functools import wraps
from typing import Any

from sqlalchemy.exc import IntegrityError, ProgrammingError

from src.domain.common.exceptions.repo import DataEmptyError, UniqueError


def exception_mapper(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def wrapped(*args: Any, **kwargs: Any):
        try:
            return await func(*args, **kwargs)
        except IntegrityError:
            raise UniqueError
        except ProgrammingError:
            raise DataEmptyError

    return wrapped
