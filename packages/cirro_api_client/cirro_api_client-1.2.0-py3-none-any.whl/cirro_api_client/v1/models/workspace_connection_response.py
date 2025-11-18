import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="WorkspaceConnectionResponse")


@_attrs_define
class WorkspaceConnectionResponse:
    """
    Attributes:
        connection_url (str):
        expires_at (datetime.datetime):
        message (str):
    """

    connection_url: str
    expires_at: datetime.datetime
    message: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        connection_url = self.connection_url

        expires_at = self.expires_at.isoformat()

        message = self.message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connectionUrl": connection_url,
                "expiresAt": expires_at,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        connection_url = d.pop("connectionUrl")

        expires_at = isoparse(d.pop("expiresAt"))

        message = d.pop("message")

        workspace_connection_response = cls(
            connection_url=connection_url,
            expires_at=expires_at,
            message=message,
        )

        workspace_connection_response.additional_properties = d
        return workspace_connection_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
