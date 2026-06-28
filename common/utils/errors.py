from typing import Any


class ErrorService:
    @classmethod
    def error_400(cls, details: Any = "general problem") -> None:
        raise Exception(str(details)[:500])
