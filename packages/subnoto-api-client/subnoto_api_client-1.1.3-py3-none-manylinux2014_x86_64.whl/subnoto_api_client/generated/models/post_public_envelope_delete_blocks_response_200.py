from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostPublicEnvelopeDeleteBlocksResponse200")


@_attrs_define
class PostPublicEnvelopeDeleteBlocksResponse200:
    """
    Attributes:
        snapshot_date (float): The date and time the snapshot was created (unix timestamp).
    """

    snapshot_date: float

    def to_dict(self) -> dict[str, Any]:
        snapshot_date = self.snapshot_date

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "snapshotDate": snapshot_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        snapshot_date = d.pop("snapshotDate")

        post_public_envelope_delete_blocks_response_200 = cls(
            snapshot_date=snapshot_date,
        )

        return post_public_envelope_delete_blocks_response_200
