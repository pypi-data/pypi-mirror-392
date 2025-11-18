from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_public_contact_update_response_200_contact import (
        PostPublicContactUpdateResponse200Contact,
    )


T = TypeVar("T", bound="PostPublicContactUpdateResponse200")


@_attrs_define
class PostPublicContactUpdateResponse200:
    """
    Attributes:
        contact (PostPublicContactUpdateResponse200Contact):
    """

    contact: PostPublicContactUpdateResponse200Contact

    def to_dict(self) -> dict[str, Any]:
        contact = self.contact.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "contact": contact,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_public_contact_update_response_200_contact import (
            PostPublicContactUpdateResponse200Contact,
        )

        d = dict(src_dict)
        contact = PostPublicContactUpdateResponse200Contact.from_dict(d.pop("contact"))

        post_public_contact_update_response_200 = cls(
            contact=contact,
        )

        return post_public_contact_update_response_200
