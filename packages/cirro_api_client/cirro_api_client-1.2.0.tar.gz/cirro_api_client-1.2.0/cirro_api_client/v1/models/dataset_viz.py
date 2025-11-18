from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_viz_config import DatasetVizConfig


T = TypeVar("T", bound="DatasetViz")


@_attrs_define
class DatasetViz:
    """
    Attributes:
        path (Union[Unset, str]): Path to viz configuration, if applicable
        name (Union[Unset, str]): Name of viz
        desc (Union[Unset, str]): Description of viz
        type (Union[Unset, str]): Type of viz Example: vitescce.
        config (Union[Unset, DatasetVizConfig]): Config or path to config used to render viz
    """

    path: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    desc: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    config: Union[Unset, "DatasetVizConfig"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path

        name = self.name

        desc = self.desc

        type = self.type

        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if path is not UNSET:
            field_dict["path"] = path
        if name is not UNSET:
            field_dict["name"] = name
        if desc is not UNSET:
            field_dict["desc"] = desc
        if type is not UNSET:
            field_dict["type"] = type
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.dataset_viz_config import DatasetVizConfig

        d = src_dict.copy()
        path = d.pop("path", UNSET)

        name = d.pop("name", UNSET)

        desc = d.pop("desc", UNSET)

        type = d.pop("type", UNSET)

        _config = d.pop("config", UNSET)
        config: Union[Unset, DatasetVizConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = DatasetVizConfig.from_dict(_config)

        dataset_viz = cls(
            path=path,
            name=name,
            desc=desc,
            type=type,
            config=config,
        )

        dataset_viz.additional_properties = d
        return dataset_viz

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
