import asyncio
import logging
import traceback
from functools import wraps
from typing import Any, Callable, Coroutine, List, Optional, Type, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    def __init__(
        self,
        max_retries: int = 5,
        exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
        on_retry: Optional[Callable] = None,
        delay: float = 0,
        exponential_backoff: bool = False,
    ):
        self.max_retries = max_retries
        self.exceptions = exceptions
        self.on_retry = on_retry
        self.delay = delay
        self.exponential_backoff = exponential_backoff

    def calculate_delay(self, attempt: int) -> float:
        pass

    async def call_callback(self, caller_instance: Any) -> None:
        pass

    async def handle_delay(self, attempt: int) -> None:
        """
        Wait for delay.

        Args:
            attempt (int): The current attempt number
        """
        pass

    def is_matching_exception(self, exc: Exception) -> bool:
        pass


def retry(
    max_retries: int = 5,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    on_retry: Optional[Callable] = None,
    delay: float = 0,
    exponential_backoff: bool = False,
    exception_to_raise: Optional[Exception] = None,
):
    """
    Decorator to try to execute a function again in case of exception.
    For greater control, it is a good practice to specify the exceptions that should be handled.

    Args:
        max_retries (int): Maximum number of attempts
        exceptions (Union[Type[Exception], List[Type[Exception]]]): Exception types that should be
            handled
        on_retry (Optional[Callable], optional): Function called after each failed attempt
        delay (float): Delay between attempts in seconds
        exponential_backoff (bool): If True, increase the delay exponentially

    Usage:
        @retry_on_exception(
            max_retries=3,
            exceptions=[ValueError, TypeError],
            delay=1
        )
        def my_function():
            ...
    """
    pass
