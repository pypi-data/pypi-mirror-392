"""Discovery function for finding tinycontrol devices in the network.

Works with LK4, tcPPDU, LK3.5 SW 1.26+, LK2.5, LK2.0.
"""

import concurrent.futures
import logging
import socket
import socketserver
import time
from typing import Any, Dict, List, Set, Union
import netifaces

from tinytoolslib.constants import LK_UDP_DISCOVERY_MSG, LK_UDP_PORT
from tinytoolslib.models import detect_version, get_device_info


class DiscoveryHandler(socketserver.BaseRequestHandler):
    """Handler for LK discovery server."""

    def handle(self):
        data = self.request[0].strip()
        if self.server.server_address[0] != self.client_address[0]:
            try:
                device_response = data.decode(errors="ignore").splitlines()
                device_data = {
                    "ip_address": self.client_address[0],
                    "name": device_response[0],
                    "mac_address": device_response[1].replace("-", ":"),
                    "software_version": None,
                    "hardware_version": None,
                }
                if len(device_response) == 4:
                    device_data["software_version"] = device_response[2]
                    device_data["hardware_version"] = device_response[3]
                else:
                    # LK2.0/2.5 response do not include hardware_version, so detect it.
                    device_data["software_version"] = device_response[2][:-1]
                    device_data["hardware_version"] = detect_version(
                        device_data["software_version"]
                    )
                device_data.update(
                    get_device_info(
                        device_data["hardware_version"],
                        device_data["software_version"],
                        asdict_=True,
                    )
                )
                self.server.devices.append(device_data)
            except (UnicodeDecodeError, IndexError):
                pass


class DiscoveryServer(socketserver.UDPServer):
    """Server for finding LKs in networks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices = []

    def server_activate(self):
        """Send discovery message after activation."""
        super().server_activate()
        dst_ip = ".".join(self.server_address[0].split(".")[:3]) + ".255"
        dst_port = self.server_address[1]
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.sendto(LK_UDP_DISCOVERY_MSG, (dst_ip, dst_port))


class DiscoveryServerAuto(DiscoveryServer):
    """DiscoveryServer that automatically shuts down."""

    def __init__(self, *args, **kwargs):
        self.started_at: float = time.time()
        """float: Timestamp of when discovery server started"""
        self.time_limit: float = kwargs.pop("time_limit", 3)
        """float: Limit of time for how long should discovery server run"""
        super().__init__(*args, **kwargs)

    def service_actions(self):
        """Checks if should stop the server due to time_limit."""
        super().service_actions()
        now = time.time()
        if now - self.started_at >= self.time_limit:
            if not getattr(self, "_BaseServer__shutdown_request"):
                setattr(self, "_BaseServer__shutdown_request", True)

    def serve_forever(self, *args, **kwargs):
        """Return devices list after auto shutdown."""
        super().serve_forever(*args, **kwargs)
        return self.devices


def get_ips() -> Set[str]:
    """Return list of IPs to check."""
    try:
        gateways = netifaces.gateways()
        interfaces = []
        for key, value in gateways.items():
            if key != "default":
                for item in value:
                    interfaces.append(item[1])
        addresses = set()
        for interface in interfaces:
            addresses_tmp = netifaces.ifaddresses(interface).get(2)
            if addresses_tmp:
                for addr in addresses_tmp:
                    addresses.add(addr["addr"])
    except ValueError:
        addresses = socket.gethostbyname_ex(socket.gethostname())[2]
    return addresses


def run_discovery(
    time_limit: int = 3,
    port: int = LK_UDP_PORT,
    addresses: Union[List[str], None] = None,
) -> List[Dict[str, Any]]:
    """Run discovery on all available addresses or given one."""
    if addresses is None:
        addresses = [ip for ip in get_ips() if not ip.startswith("169.254")]
    devices = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        servers = [
            DiscoveryServerAuto(
                (address, port), DiscoveryHandler, time_limit=time_limit
            )
            for address in addresses
        ]
        futures = {executor.submit(server.serve_forever): server for server in servers}
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
            except Exception as exc:
                logging.warning("discovery error: %s", str(exc))
            else:
                devices.extend(data)
    return devices
