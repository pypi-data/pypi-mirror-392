from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sharing_type import SharingType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mounted_dataset import MountedDataset
    from ..models.workspace_compute_config import WorkspaceComputeConfig


T = TypeVar("T", bound="WorkspaceInput")


@_attrs_define
class WorkspaceInput:
    """
    Attributes:
        name (str): Name of the workspace. Example: my-workspace.
        mounted_datasets (List['MountedDataset']): List of datasets to mount into the workspace.
        compute_config (WorkspaceComputeConfig): Configuration parameters for a containerized workspace compute
            environment.
        sharing_type (SharingType):
        description (Union[Unset, str]): Description of the workspace.
        environment_id (Union[None, Unset, str]): ID of the predefined workspace environment to use.
    """

    name: str
    mounted_datasets: List["MountedDataset"]
    compute_config: "WorkspaceComputeConfig"
    sharing_type: SharingType
    description: Union[Unset, str] = UNSET
    environment_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        mounted_datasets = []
        for mounted_datasets_item_data in self.mounted_datasets:
            mounted_datasets_item = mounted_datasets_item_data.to_dict()
            mounted_datasets.append(mounted_datasets_item)

        compute_config = self.compute_config.to_dict()

        sharing_type = self.sharing_type.value

        description = self.description

        environment_id: Union[None, Unset, str]
        if isinstance(self.environment_id, Unset):
            environment_id = UNSET
        else:
            environment_id = self.environment_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "mountedDatasets": mounted_datasets,
                "computeConfig": compute_config,
                "sharingType": sharing_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if environment_id is not UNSET:
            field_dict["environmentId"] = environment_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.mounted_dataset import MountedDataset
        from ..models.workspace_compute_config import WorkspaceComputeConfig

        d = src_dict.copy()
        name = d.pop("name")

        mounted_datasets = []
        _mounted_datasets = d.pop("mountedDatasets")
        for mounted_datasets_item_data in _mounted_datasets:
            mounted_datasets_item = MountedDataset.from_dict(mounted_datasets_item_data)

            mounted_datasets.append(mounted_datasets_item)

        compute_config = WorkspaceComputeConfig.from_dict(d.pop("computeConfig"))

        sharing_type = SharingType(d.pop("sharingType"))

        description = d.pop("description", UNSET)

        def _parse_environment_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        environment_id = _parse_environment_id(d.pop("environmentId", UNSET))

        workspace_input = cls(
            name=name,
            mounted_datasets=mounted_datasets,
            compute_config=compute_config,
            sharing_type=sharing_type,
            description=description,
            environment_id=environment_id,
        )

        workspace_input.additional_properties = d
        return workspace_input

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
