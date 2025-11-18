from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostPublicEnvelopeGetResponse200Sender")


@_attrs_define
class PostPublicEnvelopeGetResponse200Sender:
    """Information about the sender of the envelope.

    Attributes:
        email (str): The email address of the sender.
        name (str): The display name of the sender.
    """

    email: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "email": email,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        post_public_envelope_get_response_200_sender = cls(
            email=email,
            name=name,
        )

        return post_public_envelope_get_response_200_sender
