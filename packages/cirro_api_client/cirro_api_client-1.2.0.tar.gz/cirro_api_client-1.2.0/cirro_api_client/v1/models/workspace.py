import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.sharing_type import SharingType
from ..models.status import Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mounted_dataset import MountedDataset
    from ..models.workspace_compute_config import WorkspaceComputeConfig
    from ..models.workspace_session import WorkspaceSession


T = TypeVar("T", bound="Workspace")


@_attrs_define
class Workspace:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        status (Status):
        status_message (str):
        environment_id (str):
        mounted_datasets (List['MountedDataset']):
        compute_config (WorkspaceComputeConfig): Configuration parameters for a containerized workspace compute
            environment.
        sharing_type (SharingType):
        created_by (str):
        created_at (datetime.datetime):
        started_at (datetime.datetime):
        updated_at (datetime.datetime):
        sessions (Union[List['WorkspaceSession'], None, Unset]):
    """

    id: str
    name: str
    description: str
    status: Status
    status_message: str
    environment_id: str
    mounted_datasets: List["MountedDataset"]
    compute_config: "WorkspaceComputeConfig"
    sharing_type: SharingType
    created_by: str
    created_at: datetime.datetime
    started_at: datetime.datetime
    updated_at: datetime.datetime
    sessions: Union[List["WorkspaceSession"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        status = self.status.value

        status_message = self.status_message

        environment_id = self.environment_id

        mounted_datasets = []
        for mounted_datasets_item_data in self.mounted_datasets:
            mounted_datasets_item = mounted_datasets_item_data.to_dict()
            mounted_datasets.append(mounted_datasets_item)

        compute_config = self.compute_config.to_dict()

        sharing_type = self.sharing_type.value

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        started_at = self.started_at.isoformat()

        updated_at = self.updated_at.isoformat()

        sessions: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.sessions, Unset):
            sessions = UNSET
        elif isinstance(self.sessions, list):
            sessions = []
            for sessions_type_0_item_data in self.sessions:
                sessions_type_0_item = sessions_type_0_item_data.to_dict()
                sessions.append(sessions_type_0_item)

        else:
            sessions = self.sessions

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "status": status,
                "statusMessage": status_message,
                "environmentId": environment_id,
                "mountedDatasets": mounted_datasets,
                "computeConfig": compute_config,
                "sharingType": sharing_type,
                "createdBy": created_by,
                "createdAt": created_at,
                "startedAt": started_at,
                "updatedAt": updated_at,
            }
        )
        if sessions is not UNSET:
            field_dict["sessions"] = sessions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.mounted_dataset import MountedDataset
        from ..models.workspace_compute_config import WorkspaceComputeConfig
        from ..models.workspace_session import WorkspaceSession

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        status = Status(d.pop("status"))

        status_message = d.pop("statusMessage")

        environment_id = d.pop("environmentId")

        mounted_datasets = []
        _mounted_datasets = d.pop("mountedDatasets")
        for mounted_datasets_item_data in _mounted_datasets:
            mounted_datasets_item = MountedDataset.from_dict(mounted_datasets_item_data)

            mounted_datasets.append(mounted_datasets_item)

        compute_config = WorkspaceComputeConfig.from_dict(d.pop("computeConfig"))

        sharing_type = SharingType(d.pop("sharingType"))

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        started_at = isoparse(d.pop("startedAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        def _parse_sessions(data: object) -> Union[List["WorkspaceSession"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sessions_type_0 = []
                _sessions_type_0 = data
                for sessions_type_0_item_data in _sessions_type_0:
                    sessions_type_0_item = WorkspaceSession.from_dict(sessions_type_0_item_data)

                    sessions_type_0.append(sessions_type_0_item)

                return sessions_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["WorkspaceSession"], None, Unset], data)

        sessions = _parse_sessions(d.pop("sessions", UNSET))

        workspace = cls(
            id=id,
            name=name,
            description=description,
            status=status,
            status_message=status_message,
            environment_id=environment_id,
            mounted_datasets=mounted_datasets,
            compute_config=compute_config,
            sharing_type=sharing_type,
            created_by=created_by,
            created_at=created_at,
            started_at=started_at,
            updated_at=updated_at,
            sessions=sessions,
        )

        workspace.additional_properties = d
        return workspace

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
