from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostPublicTemplateListResponse200TemplatesItemDocumentsItem")


@_attrs_define
class PostPublicTemplateListResponse200TemplatesItemDocumentsItem:
    """
    Attributes:
        uuid (str): The unique identifier of the document.
        title (str): The title of the document.
    """

    uuid: str
    title: str

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        title = self.title

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "uuid": uuid,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = d.pop("uuid")

        title = d.pop("title")

        post_public_template_list_response_200_templates_item_documents_item = cls(
            uuid=uuid,
            title=title,
        )

        return post_public_template_list_response_200_templates_item_documents_item
