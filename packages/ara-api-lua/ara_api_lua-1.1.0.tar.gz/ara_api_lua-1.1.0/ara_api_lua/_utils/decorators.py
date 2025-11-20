import functools
import inspect
from typing import Any, Callable, Optional, TypeVar

import grpc

from ara_api_lua._utils.logger import Logger

T = TypeVar("T")


def grpc_error_handler(
    return_on_error: Optional[Any] = None,
    log_errors: bool = True,
    error_message: Optional[str] = None,
    raise_on_error: bool = False,
    logger: Optional[Logger] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            _logger = logger
            if _logger is None and len(args) > 0:
                if hasattr(args[0], "_logger"):
                    _logger = args[0]._logger

            if _logger is None:
                _logger = Logger(name=func.__module__)

            try:
                return func(*args, **kwargs)
            except grpc.RpcError as e:
                if log_errors:
                    msg = error_message or f"gRPC error in {func.__name__}: {e}"
                    _logger.error(msg)

                if raise_on_error:
                    raise

                sig = inspect.signature(func)
                return_annotation = sig.return_annotation

                if (
                    return_annotation is inspect.Signature.empty
                    or return_annotation is None
                ):
                    return None

                return return_on_error

        return wrapper

    return decorator
