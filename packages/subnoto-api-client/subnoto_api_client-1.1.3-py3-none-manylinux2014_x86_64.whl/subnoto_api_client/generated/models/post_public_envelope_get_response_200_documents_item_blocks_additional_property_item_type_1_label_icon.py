from enum import Enum


class PostPublicEnvelopeGetResponse200DocumentsItemBlocksAdditionalPropertyItemType1LabelIcon(
    str, Enum
):
    AT = "at"
    IMAGE = "image"
    SIGNATURE = "signature"
    TEXT_T = "text-t"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
