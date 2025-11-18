from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_public_envelope_add_recipients_body_recipients_item_type_1_type import (
    PostPublicEnvelopeAddRecipientsBodyRecipientsItemType1Type,
)

T = TypeVar("T", bound="PostPublicEnvelopeAddRecipientsBodyRecipientsItemType1")


@_attrs_define
class PostPublicEnvelopeAddRecipientsBodyRecipientsItemType1:
    """
    Attributes:
        type_ (PostPublicEnvelopeAddRecipientsBodyRecipientsItemType1Type):
        contact_uuid (str): The UUID of the contact to use.
    """

    type_: PostPublicEnvelopeAddRecipientsBodyRecipientsItemType1Type
    contact_uuid: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        contact_uuid = self.contact_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "contactUuid": contact_uuid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = PostPublicEnvelopeAddRecipientsBodyRecipientsItemType1Type(
            d.pop("type")
        )

        contact_uuid = d.pop("contactUuid")

        post_public_envelope_add_recipients_body_recipients_item_type_1 = cls(
            type_=type_,
            contact_uuid=contact_uuid,
        )

        post_public_envelope_add_recipients_body_recipients_item_type_1.additional_properties = d
        return post_public_envelope_add_recipients_body_recipients_item_type_1

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
