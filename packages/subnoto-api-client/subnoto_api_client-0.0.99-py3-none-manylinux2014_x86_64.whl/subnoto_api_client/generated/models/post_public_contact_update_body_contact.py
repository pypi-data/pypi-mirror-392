from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostPublicContactUpdateBodyContact")


@_attrs_define
class PostPublicContactUpdateBodyContact:
    """
    Attributes:
        email (str): The email of the contact.
        firstname (str): The first name of the contact.
        lastname (str): The last name of the contact.
        phone (None | str): The phone number of the contact.
    """

    email: str
    firstname: str
    lastname: str
    phone: None | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        firstname = self.firstname

        lastname = self.lastname

        phone: None | str
        phone = self.phone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "phone": phone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        firstname = d.pop("firstname")

        lastname = d.pop("lastname")

        def _parse_phone(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        phone = _parse_phone(d.pop("phone"))

        post_public_contact_update_body_contact = cls(
            email=email,
            firstname=firstname,
            lastname=lastname,
            phone=phone,
        )

        post_public_contact_update_body_contact.additional_properties = d
        return post_public_contact_update_body_contact

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
