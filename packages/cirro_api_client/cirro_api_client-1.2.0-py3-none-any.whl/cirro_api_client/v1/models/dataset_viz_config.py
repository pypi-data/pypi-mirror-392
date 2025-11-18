from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DatasetVizConfig")


@_attrs_define
class DatasetVizConfig:
    """Config or path to config used to render viz"""

    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_viz_config = cls()

        dataset_viz_config.additional_properties = d
        return dataset_viz_config

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
