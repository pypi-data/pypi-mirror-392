from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_public_envelope_add_recipients_body_recipients_item_type_0_type import (
    PostPublicEnvelopeAddRecipientsBodyRecipientsItemType0Type,
)

T = TypeVar("T", bound="PostPublicEnvelopeAddRecipientsBodyRecipientsItemType0")


@_attrs_define
class PostPublicEnvelopeAddRecipientsBodyRecipientsItemType0:
    """
    Attributes:
        type_ (PostPublicEnvelopeAddRecipientsBodyRecipientsItemType0Type):
        email (str): The recipient's email address.
        firstname (str): The recipient's first name.
        lastname (str): The recipient's last name.
    """

    type_: PostPublicEnvelopeAddRecipientsBodyRecipientsItemType0Type
    email: str
    firstname: str
    lastname: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        email = self.email

        firstname = self.firstname

        lastname = self.lastname

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = PostPublicEnvelopeAddRecipientsBodyRecipientsItemType0Type(
            d.pop("type")
        )

        email = d.pop("email")

        firstname = d.pop("firstname")

        lastname = d.pop("lastname")

        post_public_envelope_add_recipients_body_recipients_item_type_0 = cls(
            type_=type_,
            email=email,
            firstname=firstname,
            lastname=lastname,
        )

        post_public_envelope_add_recipients_body_recipients_item_type_0.additional_properties = d
        return post_public_envelope_add_recipients_body_recipients_item_type_0

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
