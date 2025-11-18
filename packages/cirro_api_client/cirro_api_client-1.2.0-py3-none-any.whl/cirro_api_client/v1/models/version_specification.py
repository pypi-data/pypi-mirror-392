from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VersionSpecification")


@_attrs_define
class VersionSpecification:
    """
    Attributes:
        version (str):
        is_default (bool):
        is_latest (bool):
    """

    version: str
    is_default: bool
    is_latest: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        version = self.version

        is_default = self.is_default

        is_latest = self.is_latest

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "isDefault": is_default,
                "isLatest": is_latest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        version = d.pop("version")

        is_default = d.pop("isDefault")

        is_latest = d.pop("isLatest")

        version_specification = cls(
            version=version,
            is_default=is_default,
            is_latest=is_latest,
        )

        version_specification.additional_properties = d
        return version_specification

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
