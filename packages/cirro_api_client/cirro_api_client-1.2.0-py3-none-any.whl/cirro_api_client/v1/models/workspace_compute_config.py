from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.workspace_compute_config_environment_variables import WorkspaceComputeConfigEnvironmentVariables


T = TypeVar("T", bound="WorkspaceComputeConfig")


@_attrs_define
class WorkspaceComputeConfig:
    """Configuration parameters for a containerized workspace compute environment.

    Attributes:
        container_image_uri (str): Fully qualified container image URI (including registry, repository, and tag).
        cpu (Union[Unset, int]): Number of vCPU cores allocated to the workspace. Example: 4.
        memory_gi_b (Union[Unset, int]): Memory allocated to the workspace container in GiB. Example: 8.
        volume_size_gi_b (Union[Unset, int]): Persistent storage volume size allocated to the workspace in GiB. Example:
            50.
        environment_variables (Union['WorkspaceComputeConfigEnvironmentVariables', None, Unset]): Map of environment
            variables injected into the container at runtime. Keys must be non-blank. Example: {'ENV_MODE': 'production',
            'LOG_LEVEL': 'debug'}.
        local_port (Union[Unset, int]): User-facing web server port (http). Example: 8080.
    """

    container_image_uri: str
    cpu: Union[Unset, int] = UNSET
    memory_gi_b: Union[Unset, int] = UNSET
    volume_size_gi_b: Union[Unset, int] = UNSET
    environment_variables: Union["WorkspaceComputeConfigEnvironmentVariables", None, Unset] = UNSET
    local_port: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.workspace_compute_config_environment_variables import WorkspaceComputeConfigEnvironmentVariables

        container_image_uri = self.container_image_uri

        cpu = self.cpu

        memory_gi_b = self.memory_gi_b

        volume_size_gi_b = self.volume_size_gi_b

        environment_variables: Union[Dict[str, Any], None, Unset]
        if isinstance(self.environment_variables, Unset):
            environment_variables = UNSET
        elif isinstance(self.environment_variables, WorkspaceComputeConfigEnvironmentVariables):
            environment_variables = self.environment_variables.to_dict()
        else:
            environment_variables = self.environment_variables

        local_port = self.local_port

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "containerImageUri": container_image_uri,
            }
        )
        if cpu is not UNSET:
            field_dict["cpu"] = cpu
        if memory_gi_b is not UNSET:
            field_dict["memoryGiB"] = memory_gi_b
        if volume_size_gi_b is not UNSET:
            field_dict["volumeSizeGiB"] = volume_size_gi_b
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if local_port is not UNSET:
            field_dict["localPort"] = local_port

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.workspace_compute_config_environment_variables import WorkspaceComputeConfigEnvironmentVariables

        d = src_dict.copy()
        container_image_uri = d.pop("containerImageUri")

        cpu = d.pop("cpu", UNSET)

        memory_gi_b = d.pop("memoryGiB", UNSET)

        volume_size_gi_b = d.pop("volumeSizeGiB", UNSET)

        def _parse_environment_variables(
            data: object,
        ) -> Union["WorkspaceComputeConfigEnvironmentVariables", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                environment_variables_type_0 = WorkspaceComputeConfigEnvironmentVariables.from_dict(data)

                return environment_variables_type_0
            except:  # noqa: E722
                pass
            return cast(Union["WorkspaceComputeConfigEnvironmentVariables", None, Unset], data)

        environment_variables = _parse_environment_variables(d.pop("environmentVariables", UNSET))

        local_port = d.pop("localPort", UNSET)

        workspace_compute_config = cls(
            container_image_uri=container_image_uri,
            cpu=cpu,
            memory_gi_b=memory_gi_b,
            volume_size_gi_b=volume_size_gi_b,
            environment_variables=environment_variables,
            local_port=local_port,
        )

        workspace_compute_config.additional_properties = d
        return workspace_compute_config

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
