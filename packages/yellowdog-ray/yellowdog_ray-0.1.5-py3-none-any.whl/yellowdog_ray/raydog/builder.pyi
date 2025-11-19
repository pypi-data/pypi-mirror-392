from _typeshed import Incomplete
from dataclasses import dataclass
from datetime import timedelta
from yellowdog_client.model import ComputeRequirementTemplateUsage, Node as Node, ProvisionedWorkerPool as ProvisionedWorkerPool, ProvisionedWorkerPoolProperties, Task, TaskGroup
from yellowdog_ray.utils.utils import get_public_ip_from_node as get_public_ip_from_node

YD_DEFAULT_API_URL: str
HEAD_NODE_TASK_GROUP_NAME: str
WORKER_NODES_TASK_GROUP_NAME: str
OBSERVABILITY_NODE_TASK_GROUP_NAME: str
TASK_TYPE: str
HEAD_NODE_TASK_POLLING_INTERVAL: Incomplete
IDLE_NODE_AND_POOL_SHUTDOWN_TIMEOUT: Incomplete
CLUSTER_NAME_STR: str
CLUSTER_NAMESPACE_STR: str
CLUSTER_TAG_STR: str
WORK_REQUIREMENT_ID_STR: str
WORKER_POOL_IDS_STR: str

@dataclass
class WorkerNodeWorkerPool:
    compute_requirement_template_usage: ComputeRequirementTemplateUsage
    provisioned_worker_pool_properties: ProvisionedWorkerPoolProperties
    task_group: TaskGroup
    task_prototype: Task
    worker_pool_id: str | None = ...

class RayDogCluster:
    yd_client: Incomplete
    work_requirement_id: str | None
    head_node_worker_pool_id: str | None
    head_node_node_id: str | None
    head_node_private_ip: str | None
    head_node_public_ip: str | None
    head_node_task_id: str | None
    worker_node_worker_pools: dict[str, WorkerNodeWorkerPool]
    enable_observability: Incomplete
    observability_node_id: str | None
    observability_node_private_ip: str | None
    observability_node_worker_pool_id: str | None
    observability_node_task_id: str | None
    def __init__(self, yd_application_key_id: str, yd_application_key_secret: str, cluster_name: str, cluster_namespace: str, head_node_compute_requirement_template_id: str, head_node_ray_start_script: str, yd_platform_api_url: str = ..., cluster_tag: str | None = None, head_node_images_id: str | None = None, head_node_userdata: str | None = None, head_node_instance_tags: dict[str, str] | None = None, head_node_metrics_enabled: bool | None = None, head_node_capture_taskoutput: bool = False, enable_observability: bool = False, observability_node_compute_requirement_template_id: str | None = None, observability_node_instance_tags: dict[str, str] | None = None, observability_node_images_id: str | None = None, observability_node_userdata: str | None = None, observability_node_metrics_enabled: bool | None = None, observability_node_start_script: str | None = None, observability_node_capture_taskoutput: bool = False, cluster_lifetime: timedelta | None = None) -> None: ...
    def add_worker_pool(self, worker_node_compute_requirement_template_id: str, worker_node_task_script: str, worker_pool_node_count: int, worker_pool_internal_name: str | None = None, worker_node_images_id: str | None = None, worker_node_userdata: str | None = None, worker_node_instance_tags: dict[str, str] | None = None, worker_node_metrics_enabled: bool | None = None, worker_node_capture_taskoutput: bool = False) -> str | None: ...
    def build(self, head_node_build_timeout: timedelta | None = None) -> tuple[str, str | None]: ...
    def remove_worker_pool(self, worker_pool_id: str): ...
    def remove_worker_pool_by_internal_name(self, internal_name: str): ...
    def get_worker_pool_internal_name_by_id(self, worker_pool_id: str) -> str | None: ...
    @property
    def worker_pool_ids(self) -> list[str]: ...
    @property
    def worker_pool_internal_names(self) -> list[str]: ...
    def shut_down(self) -> None: ...
    def save_state_to_json(self) -> str: ...
    def save_state_to_json_file(self, file_name: str): ...

class RayDogClusterProxy:
    yd_client: Incomplete
    def __init__(self, yd_application_key_id: str, yd_application_key_secret: str, yd_platform_api_url: str = ...) -> None: ...
    def load_saved_state_from_json(self, cluster_state: str): ...
    def load_saved_state_from_json_file(self, file_name: str): ...
    def shut_down(self) -> None: ...
