from dataclasses import dataclass

@dataclass
class SSHTunnelSpec:
    local_bind_hostname: str
    local_bind_ip_address: int
    remote_bind_hostname: str
    remote_bind_ip_address: int

class RayTunnels:
    def __init__(self, ray_head_ip_address: str, ssh_user: str, password: str | None = None, private_key_file: str | None = None, private_key_password: str | None = None, ray_tunnel_specs: list[SSHTunnelSpec] | None = None) -> None: ...
    @staticmethod
    def basic_port_forward(port: int) -> SSHTunnelSpec: ...
    def start_tunnels(self) -> None: ...
    def stop_tunnels(self, ignore_errors: bool = True): ...
