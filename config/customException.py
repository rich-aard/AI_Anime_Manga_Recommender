import sys
import traceback
from types import TracebackType


class CustomException(Exception):
    """
    Structured exception for AI based Anime and Manga Recommendation system. Captures the error message, originating file, line number, and full traceback at the point of raising. Works correctly both inside and outside except blocks.
    """

    def __init__(
        self,
        message: str,
        original_error: Exception | None = None,
    ) -> None:
        _, _, exc_tb = sys.exc_info()
        self.original_error = original_error
        self.error_message = self._format_message(message, original_error, exc_tb)
        self.traceback_str: str = (
            traceback.format_exc() if original_error else "No traceback available."
        )
        super().__init__(self.error_message)

    @staticmethod
    def _format_message(
        message: str,
        original_error: Exception | None,
        exc_tb: TracebackType | None,
    ) -> str:
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "unknown file"
        line_number = str(exc_tb.tb_lineno) if exc_tb else "unknown line"
        error_detail = (
            f" | Caused by: {type(original_error).__name__}: {original_error}"
            if original_error
            else ""
        )

        return f"{message}{error_detail} | File: {file_name} | Line: {line_number}"

    def log(self, logger) -> None:
        logger.error(
            self.error_message,
            extra={
                "error_message": self.error_message,
                "traceback": self.traceback_str,
            },
        )

    def __str__(self) -> str:
        return self.error_message

    def __repr__(self) -> str:
        return f"CustomException(message={self.error_message!r})"
