from yellowdog_client import PlatformClient as PlatformClient
from yellowdog_client.model import Node as Node, WorkerPool as WorkerPool

def get_public_ip_from_node(client: PlatformClient, node: Node) -> str | None: ...
