import sys
import traceback
from typing import Optional


class AppException(Exception):
    """
    Exceção base reutilizável para aplicações Python e MLOps.

    Encapsula a exceção original e adiciona contexto mínimo
    (arquivo e linha) sem over-engineering.
    """

    def __init__(
        self,
        message: str,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        self.trace = self._extract_trace()

    def _extract_trace(self) -> str:
        _, _, tb = sys.exc_info()
        if tb is None:
            return "No traceback available"

        frame = tb.tb_frame
        return f"{frame.f_code.co_filename}:{tb.tb_lineno}"

    def __str__(self) -> str:
        base = f"{self.message} | Location: {self.trace}"
        if self.original_exception:
            return f"{base} | Caused by: {repr(self.original_exception)}"
        return base
