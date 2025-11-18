from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostPublicContactCreateResponse200ContactsItem")


@_attrs_define
class PostPublicContactCreateResponse200ContactsItem:
    """
    Attributes:
        uuid (str): The UUID of the contact.
        email (str): The email of the contact.
        firstname (str): The first name of the contact.
        lastname (str): The last name of the contact.
        phone (None | str): The phone number of the contact.
    """

    uuid: str
    email: str
    firstname: str
    lastname: str
    phone: None | str

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        email = self.email

        firstname = self.firstname

        lastname = self.lastname

        phone: None | str
        phone = self.phone

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "uuid": uuid,
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
        uuid = d.pop("uuid")

        email = d.pop("email")

        firstname = d.pop("firstname")

        lastname = d.pop("lastname")

        def _parse_phone(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        phone = _parse_phone(d.pop("phone"))

        post_public_contact_create_response_200_contacts_item = cls(
            uuid=uuid,
            email=email,
            firstname=firstname,
            lastname=lastname,
            phone=phone,
        )

        return post_public_contact_create_response_200_contacts_item
