from enum import Enum


class PostPublicEnvelopeGetResponse200DocumentsItemBlocksAdditionalPropertyItemType0TemplatedText(
    str, Enum
):
    EMAIL = "email"
    FULLNAME = "fullname"
    PHONE = "phone"

    def __str__(self) -> str:
        return str(self.value)
