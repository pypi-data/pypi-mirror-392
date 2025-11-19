"""Flash function for tinycontrol devices.

Handles HTTP and TFTP methods.
- HTTP method is for LK4, tcPDU
- TFTP method is for LK3.5, LK3.0, LK2.5, LK2.0
For details you can see .models.py as FW update method is part of device description.
"""

import logging
import os
import socket
import time
from functools import wraps
from math import ceil
from typing import Any, Callable, Dict, Tuple, Union

import requests
from tftpy import SOCK_TIMEOUT, TftpClient, TftpTimeout

from tinytoolslib.constants import LK_UDP_BOOTLOADER_MSG, LK_UDP_PORT, FWUpdateMethod
from tinytoolslib.exceptions import TinyToolsFlashError, TinyToolsRequestError
from tinytoolslib.models import (
    LK_HW_20,
    LK_HW_20_PS,
    LK_HW_25,
    LK_HW_25_PS,
    get_version,
)
from tinytoolslib.requests import get, post


class Flasher:
    """Class with all flash related functions.

    Generally use as:
    flasher = Flasher()
    flasher.run(...)
    """

    def __init__(self):
        """Initialize Flasher."""
        self.callback_progress: Callable[[int, int, float, str], None] = None
        """Function called during flashing with progress info.

        Parameters are current, total, percent, unit(packet/B).
        """
        self.callback_cancel: Callable[[], bool] = None
        """Function called before actual flashing has started.

        If it returns True then flashing will be canceled.
        """
        self.context = {}
        self._session = requests.Session()

    # region TFTP flashing
    @staticmethod
    def get_optimal_number_of_attempts(version_info: Dict[str, Any]) -> int:
        """Return number of attempts, so for HW2.X it quits earlier.

        version_info is expected to be return value of get_version().
        Each attempt takes SOCK_TIMEOUT*TIMEOUT_RETRIES
        """
        logging.debug("Getting optimal number of flash attempts (less for LK2.X)")
        lk_2X_models = [
            LK_HW_20_PS.info.model,
            LK_HW_20.info.model,
            LK_HW_25.info.model,
            LK_HW_25_PS.info.model,
        ]
        if version_info is not None and version_info["model"] in lk_2X_models:
            return 1
        return 4

    def start_bootloader(
        self, host: str, username: str, password: str, schema: str, port: int
    ) -> bool:
        """Start bootloader mode on device (LK2.X, LK3.X)."""
        success = False
        # First try http method.
        try:
            # First check if upgrade is enabled else enable it
            resp = get(
                host,
                "/xml/st.xml",
                schema,
                port,
                username,
                password,
                session=self._session,
            )["parsed"]
            if resp.get("upgr") == "0":
                logging.info("Upgrade is disabled on device - trying to enable it.")
                cmd = "/stm.cgi?auth={}{}{}".format(resp["auth"], 1, resp["userpass"])
                get(host, cmd, schema, port, username, password, session=self._session)[
                    "parsed"
                ]
            logging.info("Starting bootloader mode via HTTP...")
            get(
                host,
                "/stm.cgi?upgrade=lkstart3",
                schema,
                port,
                username,
                password,
                session=self._session,
            )
            success = True
        except (KeyError, ValueError, TinyToolsRequestError) as exc:
            logging.error("Failed to enable bootloader via HTTP: %s", str(exc))
        if not success:
            # Try UDP method.
            logging.info("Starting bootloader mode via UDP...")
            with socket.socket(
                type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP
            ) as sock:
                sock.connect((host, LK_UDP_PORT))
                sock.sendall(LK_UDP_BOOTLOADER_MSG)
            success = True
        return success

    def flash_hook(self, packet):
        """Display flashing progress."""
        # Cancel only while waiting for transfer
        if (
            packet.opcode == 2
            and callable(self.callback_cancel)
            and self.callback_cancel()
        ):
            raise TinyToolsFlashError("Flash canceled by user")
        if packet.opcode == 3:
            logging.debug("Packet %d/%d", packet.blocknumber, self.context["packets"])
            if callable(self.callback_progress):
                # Call with <packet no>, <total packets>, <progress %>
                self.callback_progress(
                    packet.blocknumber,
                    self.context["packets"],
                    packet.blocknumber / self.context["packets"] * 100,
                    "packet",
                )

    def flash_firmware_via_tftp(
        self, host: str, firmware_path: str, attempts_limit: int
    ) -> bool:
        """Try to flash firmware and display progress."""
        firmware_name = os.path.basename(firmware_path)
        bytes_size = os.stat(firmware_path).st_size
        self.context.update(
            {
                "size": bytes_size,
                "packets": ceil(bytes_size / 512),
            }
        )
        logging.info(
            "Uploading firmware %s with size of %dB in %d packets",
            firmware_name,
            self.context["size"],
            self.context["packets"],
        )
        client = TftpClient(host)
        attempt = 0
        flashed = False
        canceled = False
        while attempt < attempts_limit and not flashed:
            try:
                if callable(self.callback_cancel) and self.callback_cancel():
                    # Stop before starting flash.
                    raise TinyToolsFlashError("Flash canceled by user")
                client.upload(firmware_name, firmware_path, self.flash_hook)
            except TftpTimeout:
                attempt += 1
            except (ConnectionError, socket.gaierror):
                attempt += 1
                time.sleep(SOCK_TIMEOUT)
            except TinyToolsFlashError:
                canceled = True
                break
            else:
                flashed = True
        if canceled:
            logging.info("Canceled flashing")
            return False
        elif not flashed:
            logging.warning("Unable to connect with device. Try again.")
            return False
        else:
            logging.info(
                "Uploaded firmware in %.1fs with avg speed of %.0f kbps.",
                client.context.metrics.duration,
                client.context.metrics.kbps,
            )
            return True

    # endregion

    def update_firmware_via_http(
        self,
        firmware_path: str,
        host: str,
        username: str,
        password: str,
        schema: str,
        port: int,
    ) -> bool:
        """Update firmware via HTTP for LK4/tcPDU."""
        try:
            with open(firmware_path, "rb") as fread:
                bytes_size = os.stat(firmware_path).st_size
                self.context.update(
                    {
                        "size": bytes_size,
                        "uploaded": 0,
                    }
                )
                # Modify stream object to update progress
                func = getattr(fread, "read")

                @wraps(func)
                def read(data, *args, **kwargs):
                    res = func(data, *args, **kwargs)
                    self.context["uploaded"] += data
                    if self.context["uploaded"] > self.context["size"]:
                        self.context["uploaded"] = self.context["size"]
                    logging.debug(
                        "Uploaded %.0f/%.0f kB (%.1f %%)",
                        self.context["uploaded"] / 1024,
                        self.context["size"] / 1024,
                        self.context["uploaded"] / self.context["size"] * 100,
                    )
                    if callable(self.callback_progress):
                        # Call with <uploaded B>, <total B>, <progress %>
                        self.callback_progress(
                            self.context["uploaded"],
                            self.context["size"],
                            self.context["uploaded"] / self.context["size"] * 100,
                            "B",
                        )
                    return res

                setattr(fread, "read", read)
                # Upload file
                if callable(self.callback_progress):
                    # Call with <0 B>, <total B>, <0 %>
                    self.callback_progress(0, self.context["size"], 0, "B")
                resp = post(
                    host,
                    "/api/v1/upload_firmware/new_firmware",
                    schema,
                    port,
                    username,
                    password,
                    data=fread,
                    session=self._session,
                )
                # Restart device
                get(
                    host,
                    "/api/v1/save/?restart=1",
                    schema,
                    port,
                    username,
                    password,
                    session=self._session,
                )
        except Exception as exc:
            logging.warning("Error occurred: %s. Try again.", str(exc))
            return False
        else:
            logging.info(
                "Uploaded firmware in %.1fs with avg speed of %.0f kbps.",
                resp.get("elapsed", 1),
                self.context["size"] / 1024 * 8 / resp.get("elapsed", 1),
            )
            return True

    def run(
        self,
        firmware_path: str,
        host: str,
        port: int = 80,
        schema: str = "http",
        username: str = "",
        password: str = "",
        callback_progress: Union[Callable[[int, int, float, str], None], None] = None,
        callback_cancel: Union[Callable[[], bool], None] = None,
    ) -> bool:
        """Flash given firmware to given address.

        It automatically uses HTTP or TFTP method (latter one is used if device does not respond).
        """
        self.callback_progress = callback_progress
        self.callback_cancel = callback_cancel
        self.context = {}
        if (
            isinstance(firmware_path, str)
            and firmware_path
            and os.path.isfile(firmware_path)
        ):
            with self._session:
                # Try to get device version. Note that get_version may return
                # different port and schema than given ones, eg. for http:80,
                # may return http:80 or https:443.
                # It also assumes that lk4/tcpdu always respond via HTTP.
                version_info = get_version(host, port, schema, username, password)
                if version_info and "network_info" in version_info:
                    schema = version_info["network_info"]["schema"]
                    port = version_info["network_info"]["port"]
                if (
                    version_info
                    and version_info.get("fw_update_method") == FWUpdateMethod.HTTP
                ):
                    return self.update_firmware_via_http(
                        firmware_path, host, username, password, schema, port
                    )
                else:
                    attempts = self.get_optimal_number_of_attempts(version_info)
                    logging.info("Preparing device for flashing...")
                    self.start_bootloader(host, username, password, schema, port)
                    return self.flash_firmware_via_tftp(host, firmware_path, attempts)
        else:
            logging.warning("Invalid file for flashing.")
            return False


# region getting new firmware file
def check_for_latest_firmware(fw_url: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """Check latest available version of firmware.

    Returns:
        (True, {name: str, description: {en: str, pl: str}, url: str, date: str})
        (False, str) - str is an error message
    """
    if fw_url is None:
        return (
            False,
            "Cannot get firmware files for this device directly. "
            "You can look for it at https://tinycontrol.pl.",
        )
    try:
        resp = get(fw_url, None, timeout=5)
    except TinyToolsRequestError as exc:
        return False, str(exc)
    else:
        result = resp["parsed"]
        return True, result


def get_latest_firmware(
    host: str,
    port: int,
    schema: str,
    username: str,
    password: str,
    firmware_directory: str,
) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """Get latest firmware for device.

    Returns:
        (True, {**get_version(), path: str, new_sw: str})
        (False, str) - str is an error message
    """
    version_info = get_version(host, port, schema, username=username, password=password)
    if version_info:
        latest_version = check_for_latest_firmware(version_info.get("fw_url"))
        if latest_version[0]:
            # Check if it's already downloaded else download
            firmware_name = latest_version[1]["url"].split("/")[-1]
            firmware_path = os.path.join(firmware_directory, firmware_name)
            if os.path.isfile(firmware_path) or download_firmware(
                latest_version[1]["url"], firmware_path
            ):
                version_info.update(
                    {
                        "path": firmware_path,
                        "new_sw": latest_version[1]["name"],
                    }
                )
                return True, version_info
            else:
                return False, "Failed to download file"
        else:
            return False, latest_version[1]
    return False, "Cannot get information about latest firmware"


def download_firmware(download_url: str, save_location: str) -> bool:
    """Download firmware from given url."""
    try:
        resp = get(download_url, None, timeout=5)
    except TinyToolsRequestError:
        return False
    else:
        os.makedirs(os.path.dirname(save_location), exist_ok=True)
        with open(save_location, "wb") as f:
            f.write(resp["_response"].content)
        return True


# endregion


def run_flash(
    firmware_path: str,
    host: str,
    port: int = 80,
    schema: str = "http",
    username: str = "",
    password: str = "",
    callback_progress: Union[Callable[[int, int, float, str], None], None] = None,
    callback_cancel: Union[Callable[[], bool], None] = None,
) -> bool:
    """Run flashing firmware to given address."""
    flasher = Flasher()
    return flasher.run(
        firmware_path,
        host,
        port,
        schema,
        username,
        password,
        callback_progress,
        callback_cancel,
    )
