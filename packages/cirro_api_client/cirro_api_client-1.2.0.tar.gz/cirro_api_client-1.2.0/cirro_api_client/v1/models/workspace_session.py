import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="WorkspaceSession")


@_attrs_define
class WorkspaceSession:
    """
    Attributes:
        id (str):
        user (str):
        created_at (datetime.datetime):
    """

    id: str
    user: str
    created_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        user = self.user

        created_at = self.created_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user": user,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        user = d.pop("user")

        created_at = isoparse(d.pop("createdAt"))

        workspace_session = cls(
            id=id,
            user=user,
            created_at=created_at,
        )

        workspace_session.additional_properties = d
        return workspace_session

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
