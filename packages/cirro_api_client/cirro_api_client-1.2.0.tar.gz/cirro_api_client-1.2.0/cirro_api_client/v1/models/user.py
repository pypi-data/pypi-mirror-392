from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        name (str):
        username (str):
        organization (str):
        department (str):
        job_title (str):
    """

    name: str
    username: str
    organization: str
    department: str
    job_title: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        username = self.username

        organization = self.organization

        department = self.department

        job_title = self.job_title

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "username": username,
                "organization": organization,
                "department": department,
                "jobTitle": job_title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        username = d.pop("username")

        organization = d.pop("organization")

        department = d.pop("department")

        job_title = d.pop("jobTitle")

        user = cls(
            name=name,
            username=username,
            organization=organization,
            department=department,
            job_title=job_title,
        )

        user.additional_properties = d
        return user

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
