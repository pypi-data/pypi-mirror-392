from enum import Enum


class PostPublicContactGetResponse403ErrorCode(str, Enum):
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INVALID_REQUEST_FORMAT = "INVALID_REQUEST_FORMAT"

    def __str__(self) -> str:
        return str(self.value)
