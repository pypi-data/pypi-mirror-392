from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupCost")


@_attrs_define
class GroupCost:
    """
    Attributes:
        name (Union[Unset, str]): Task status group Example: CACHED.
        cost (Union[Unset, float]): Cost
    """

    name: Union[Unset, str] = UNSET
    cost: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        cost = self.cost

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if cost is not UNSET:
            field_dict["cost"] = cost

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        cost = d.pop("cost", UNSET)

        group_cost = cls(
            name=name,
            cost=cost,
        )

        group_cost.additional_properties = d
        return group_cost

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
