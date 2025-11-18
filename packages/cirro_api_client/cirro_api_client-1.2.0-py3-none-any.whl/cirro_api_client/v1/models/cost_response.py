from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_cost import GroupCost
    from ..models.task_cost import TaskCost


T = TypeVar("T", bound="CostResponse")


@_attrs_define
class CostResponse:
    """
    Attributes:
        total_cost (Union[Unset, float]): Total cost
        groups (Union[Unset, List['GroupCost']]): Costs grouped by the task status
        tasks (Union[Unset, List['TaskCost']]): Costs for each workflow task
        is_estimate (Union[Unset, bool]): Whether this is an estimated cost
    """

    total_cost: Union[Unset, float] = UNSET
    groups: Union[Unset, List["GroupCost"]] = UNSET
    tasks: Union[Unset, List["TaskCost"]] = UNSET
    is_estimate: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total_cost = self.total_cost

        groups: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)

        tasks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tasks, Unset):
            tasks = []
            for tasks_item_data in self.tasks:
                tasks_item = tasks_item_data.to_dict()
                tasks.append(tasks_item)

        is_estimate = self.is_estimate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_cost is not UNSET:
            field_dict["totalCost"] = total_cost
        if groups is not UNSET:
            field_dict["groups"] = groups
        if tasks is not UNSET:
            field_dict["tasks"] = tasks
        if is_estimate is not UNSET:
            field_dict["isEstimate"] = is_estimate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.group_cost import GroupCost
        from ..models.task_cost import TaskCost

        d = src_dict.copy()
        total_cost = d.pop("totalCost", UNSET)

        groups = []
        _groups = d.pop("groups", UNSET)
        for groups_item_data in _groups or []:
            groups_item = GroupCost.from_dict(groups_item_data)

            groups.append(groups_item)

        tasks = []
        _tasks = d.pop("tasks", UNSET)
        for tasks_item_data in _tasks or []:
            tasks_item = TaskCost.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        is_estimate = d.pop("isEstimate", UNSET)

        cost_response = cls(
            total_cost=total_cost,
            groups=groups,
            tasks=tasks,
            is_estimate=is_estimate,
        )

        cost_response.additional_properties = d
        return cost_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
