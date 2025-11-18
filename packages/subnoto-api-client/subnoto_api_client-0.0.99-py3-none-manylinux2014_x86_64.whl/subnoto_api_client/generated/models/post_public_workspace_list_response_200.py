from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_public_workspace_list_response_200_workspaces_item import (
        PostPublicWorkspaceListResponse200WorkspacesItem,
    )


T = TypeVar("T", bound="PostPublicWorkspaceListResponse200")


@_attrs_define
class PostPublicWorkspaceListResponse200:
    """
    Attributes:
        workspaces (list[PostPublicWorkspaceListResponse200WorkspacesItem]):
    """

    workspaces: list[PostPublicWorkspaceListResponse200WorkspacesItem]

    def to_dict(self) -> dict[str, Any]:
        workspaces = []
        for workspaces_item_data in self.workspaces:
            workspaces_item = workspaces_item_data.to_dict()
            workspaces.append(workspaces_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "workspaces": workspaces,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_public_workspace_list_response_200_workspaces_item import (
            PostPublicWorkspaceListResponse200WorkspacesItem,
        )

        d = dict(src_dict)
        workspaces = []
        _workspaces = d.pop("workspaces")
        for workspaces_item_data in _workspaces:
            workspaces_item = (
                PostPublicWorkspaceListResponse200WorkspacesItem.from_dict(
                    workspaces_item_data
                )
            )

            workspaces.append(workspaces_item)

        post_public_workspace_list_response_200 = cls(
            workspaces=workspaces,
        )

        return post_public_workspace_list_response_200
