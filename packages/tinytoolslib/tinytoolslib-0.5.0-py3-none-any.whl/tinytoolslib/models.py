"""Device definitions along with methods for communicating with them."""

import operator
import re
import warnings
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, ClassVar, Dict, List, Tuple, Union

from aiohttp import ClientSession

from tinytoolslib.constants import (FW_URL_TEMPLATE, DeviceFamily,
                                    FWUpdateMethod)
from tinytoolslib.exceptions import (TinyToolsRequestConnectionError,
                                     TinyToolsRequestError,
                                     TinyToolsRequestInternalServerError,
                                     TinyToolsRequestNotFound,
                                     TinyToolsRequestSSLError,
                                     TinyToolsRequestTimeout,
                                     TinyToolsUnsupported)
from tinytoolslib.parsers import (float_div10, float_div100, float_div1000,
                                  int_inverted, list_map, name_list,
                                  parse_version, strint_to_int_list, up_to_int)
from tinytoolslib.requests import async_get, get


@dataclass
class DeviceInfo:
    """General information about Device."""

    model: str
    family: DeviceFamily
    fw_tag: Union[str, None] = None
    fw_url: Union[str, None] = field(init=False, default=None)
    fw_changelog: Union[str, None] = None
    fw_update_method: Union[str, None] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.fw_tag:
            self.fw_url = FW_URL_TEMPLATE.format(self.fw_tag)


@dataclass
class DeviceModel(ABC):
    """Base class for tinycontrol devices with common methods."""

    info: ClassVar[Union[DeviceInfo, None]] = None
    mapping: ClassVar[Dict[str, Dict]] = {}
    parsers: ClassVar[List[str]] = []

    host: str
    schema: str = "http"
    port: int = 80
    username: str = ""
    password: str = ""
    hardware_version: str = ""
    software_version: str = ""
    session: Union[ClientSession, None] = None

    _context: Dict[str, Dict] = field(init=False, default_factory=dict)
    _close_session: bool = False

    def __post_init__(self):
        if self.schema == "https" and self.port != 443:
            warnings.warn(
                "Devices (LK3.X, LK4.X, tcPDU) always use port 443 for https. "
                f"You are about to use {self.port}."
            )

    @classmethod
    @abstractmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        """Verifies if versions matches this Device model."""

    def _get(
        self,
        data: Dict[str, Any],
        path: str,
        skip_keys: Union[List[str], None] = None,
        remove_mapped_keys: bool = False,
    ) -> Dict[str, Any]:
        """Process get data (dict) with mapping."""
        if data is not None:
            updates = {}
            for key, value in data.items():
                if skip_keys and key in skip_keys:
                    continue
                mapper = self.mapping.get(key)
                if mapper is not None:
                    mapped = mapper["format"](value)
                    if isinstance(mapper["name"], list):
                        for name, val in zip(mapper["name"], mapped):
                            updates[name] = val
                    else:
                        updates[mapper["name"]] = mapped
            data.update(updates)
            if remove_mapped_keys:
                # Remove keys that were parsed/mapped
                for key, val in self.mapping.items():
                    if (
                        isinstance(val["name"], str)
                        and key != val["name"]
                        and (skip_keys is None or key not in skip_keys)
                    ):
                        data.pop(key, None)
        # Run extra parsers, that need to work on whole response.
        for parser in self.parsers:
            parser_func = getattr(self, parser)
            parser_func(data, path)
        return data

    def get(
        self,
        path: str,
        skip_keys: Union[List[str], None] = None,
        remove_mapped_keys: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """Get data, process parsed part with mapping."""
        response = get(
            self.host,
            path,
            schema=self.schema,
            port=self.port,
            username=self.username,
            password=self.password,
            **kwargs,
        )
        return self._get(response.get("parsed"), path, skip_keys, remove_mapped_keys)

    def set_out(self, index, value=None):
        """Set output state to value or toggle if value is None."""
        if callable(getattr(self, "_set_out", None)):
            return self.get(self._set_out(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling OUTs"
        )

    def set_pwm(self, index, value):
        """Set pwm state to value or toggle if value is None."""
        if callable(getattr(self, "_set_pwm", None)):
            return self.get(self._set_pwm(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling PWMs"
        )

    def set_pwm_duty(self, index, value):
        """Set pwm duty to value."""
        if callable(getattr(self, "_set_pwm_duty", None)):
            return self.get(self._set_pwm_duty(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling PWM duty"
        )

    def set_pwm_freq(self, index, value):
        """Set pwm freq to value."""
        if callable(getattr(self, "_set_pwm_freq", None)):
            return self.get(self._set_pwm_freq(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling PWM freq"
        )

    def set_var(self, index, value):
        """Set VAR/EVENT variable to value."""
        if callable(getattr(self, "_set_var", None)):
            return self.get(self._set_var(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling VARs"
        )

    def set_ds(self, index: int, value: str):
        """Set ID of DS on position to value."""
        if callable(getattr(self, "_set_ds", None)):
            return self.get(self._set_ds(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support setting DSs"
        )

    def get_all(self, remove_mapped_keys: bool = False) -> Dict[str, Any]:
        """Get set of all sensor/readings."""
        if callable(getattr(self, "_get_all", None)):
            data = {}
            for url in self._get_all():
                data.update(self.get(url, remove_mapped_keys=remove_mapped_keys))
            return data
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support get_all command"
        )

    def reset_to_defaults(self):
        """Reset settings to defaults."""
        if callable(getattr(self, "_reset_to_defaults", None)):
            return self.get(self._reset_to_defaults())
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support reset to defaults"
        )

    def restart(self):
        """Restart device."""
        if callable(getattr(self, "_restart", None)):
            return self.get(self._restart())
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support restart command"
        )

    # region Async variants
    async def async_get(
        self,
        path: str,
        skip_keys: Union[List[str], None] = None,
        remove_mapped_keys: bool = False,
        **kwargs,
    ):
        """Async version of get."""
        if self.session is None:
            self.session = ClientSession()
            self._close_session = True
        response = await async_get(
            self.host,
            path,
            schema=self.schema,
            port=self.port,
            username=self.username,
            password=self.password,
            session=self.session,
            **kwargs,
        )
        return self._get(response.get("parsed"), path, skip_keys, remove_mapped_keys)

    async def async_set_out(self, index, value=None):
        """Async set_out."""
        if callable(getattr(self, "_set_out", None)):
            return await self.async_get(self._set_out(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling OUTs"
        )

    async def async_set_pwm(self, index, value):
        """Async set_pwm."""
        if callable(getattr(self, "_set_pwm", None)):
            return await self.async_get(self._set_pwm(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling PWMs"
        )

    async def async_set_var(self, index, value):
        """Async set_var."""
        if callable(getattr(self, "_set_var", None)):
            return await self.async_get(self._set_var(index, value))
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support controlling VARs"
        )

    async def async_get_all(self, remove_mapped_keys: bool = False) -> Dict[str, Any]:
        """Async get_all."""
        if callable(getattr(self, "_get_all", None)):
            data = {}
            for url in self._get_all():
                data.update(await self.async_get(url, remove_mapped_keys=remove_mapped_keys))
            return data
        raise TinyToolsUnsupported(
            f"{self.__class__.__name__} does not support get_all command"
        )

    # region Session handling for asyncio
    async def close(self) -> None:
        """Close open client session."""
        await self.session.close()

    async def __aenter__(self) -> "DeviceModel":
        """Async enter.

        Returns
        -------
            The Device object.
        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()

    # endregion
    # endregion


def set_cmd_helper(
    caller: DeviceModel,
    cmd_prefix: str,
    cmd_param: str,
    index: Union[int, List[int]],
    value: Union[int, List[int], None],
    negation=False,
    toggle_available=True,
    cmd_set_format="{cmd_param}{index}={value}",
    cmd_toggle_format="{cmd_param}={cmd_param}{index}",
):
    """Helper for building GET query for setting, eg OUTs, PWMs, VARs.

    It handles negation (or forced inversion of state, eg. when device
    uses 0 for on and 1 for off), toggle commands (only chainable mode,
    eg. out=out1&out=out2), and also mixed combination of index+value.

    Example output (for single index and single value, set command):
    `{cmd_prefix}{cmd_param}{index}={value}`
    """
    cmd = cmd_prefix
    # Invert states for negation or forced inversion.
    if negation and value is not None:
        if isinstance(value, list):
            value = [int_inverted(val) for val in value]
        else:
            value = int_inverted(value)
    # Handle case when value is missing but toggle is not available.
    if toggle_available is False and value is None:
        raise TinyToolsUnsupported(
            f"{caller.__class__.__name__} does not support toggle for command {cmd_param}"
        )
    # Handle combinations of index + value: int + int/None, [int] + int/[int]/None.
    if isinstance(index, list):
        if toggle_available and value is None:
            cmd += "&".join(
                [
                    cmd_toggle_format.format(cmd_param=cmd_param, index=ix)
                    for ix in index
                ]
            )
        elif isinstance(value, list):
            cmd += "&".join(
                [
                    cmd_set_format.format(cmd_param=cmd_param, index=ix, value=val)
                    for ix, val in zip(index, value)
                ]
            )
        else:
            cmd += "&".join(
                [
                    cmd_set_format.format(cmd_param=cmd_param, index=ix, value=value)
                    for ix in index
                ]
            )
    else:
        if toggle_available and value is None:
            cmd += cmd_toggle_format.format(cmd_param=cmd_param, index=index)
        else:
            cmd += cmd_set_format.format(cmd_param=cmd_param, index=index, value=value)
    return cmd


def apply_index_offset(
    index: Union[int, List[int]], offset: int = 0, func=operator.add
) -> Union[int, List[int]]:
    """Apply an integer offset to a single index or list of indices.

    Use offset=-1 to convert 1-based → 0-based, offset=+1 to convert 0-based → 1-based.
    Might change how it processes by providing func, which will be given 2 params: index and offset.
    """
    if isinstance(index, list):
        return [func(i, offset) for i in index]
    return func(index, offset)


@dataclass
class LK_HW_20_PS(DeviceModel):
    """Methods for working with Power Socket on LK2.0.

    Note: for outputs it uses unified values 0 - off, 1 - on.
    """

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "IP Power Socket v1 (LK2.0)",  # 5G10A/6G10A
        DeviceFamily.PS,
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6, "outputs_inverted": True}, # or 5 for SW 6.12a
    )
    mapping: ClassVar[Dict[str, Dict]] = {
        # --- st0.xml
        "out0": {"name": "out0", "format": int_inverted},
        "out1": {"name": "out1", "format": int_inverted},
        "out2": {"name": "out2", "format": int_inverted},
        "out3": {"name": "out3", "format": int_inverted},
        "out4": {"name": "out4", "format": int_inverted},
        "out5": {"name": "out5", "format": int_inverted},
        "out6": {"name": "out_negation", "format": int_inverted},
        "di0": {"name": "iDValue1", "format": up_to_int},
        "di1": {"name": "iDValue2", "format": up_to_int},
        "ia0": {"name": "boardTemp", "format": float_div10},
        "ia1": {"name": "ds1", "format": float_div10},
        "ia2": {"name": "ds2", "format": float_div10},
        "ia3": {"name": "ds3", "format": float_div10},
        "ia4": {"name": "ds4", "format": float_div10},
        "ia5": {"name": "iAValue1", "format": float_div100},  # Voltage input
        "ia6": {"name": "boardVoltage", "format": float_div10},
        # Doubled keys for time
        "sec0": {"name": "uptimeSeconds", "format": int},
        "sec1": {"name": "uptimeMinutes", "format": int},
        "sec2": {"name": "uptimeHours", "format": int},
        "sec3": {"name": "uptimeDays", "format": int},
        "sec4": {"name": "time", "format": int},
        "t": {"name": "time", "format": int},
        # --- st2.xml
        "ver": {"name": "software_version", "format": str},
        "hw": {"name": "hardware_version", "format": lambda x: "2." + x},
        "na": {"name": "hostname", "format": str},
        "r0": {"name": "out0_reset_time", "format": int},
        "r1": {"name": "out1_reset_time", "format": int},
        "r2": {"name": "out2_reset_time", "format": int},
        "r3": {"name": "out3_reset_time", "format": int},
        "r4": {"name": "out4_reset_time", "format": int},
        "r5": {"name": "out5_reset_time", "format": int},
        "r6": {"name": "out0_name", "format": str},
        "r7": {"name": "out1_name", "format": str},
        "r8": {"name": "out2_name", "format": str},
        "r9": {"name": "out3_name", "format": str},
        "r10": {"name": "out4_name", "format": str},
        "r11": {"name": "out5_name", "format": str},
        # Autoswitch times 6*on + 6*off (X*X*X*...)
        "a": {"name": "autoswitch_times", "format": str},
        # Autoswitch enabled (int with bin values 000000)
        "as": {"name": "autoswitch_active", "format": str},
        # Names divided with *
        "d": {"name": "dsName1-4_iAName1_iDName1-2", "format": str},
        # --- board.xml (configuration like network, remote access, email, etc.)
        # a0, a1, a2 - auto send trap settings
        # Email
        "b0": {"name": "email_host", "format": str},
        "b1": {"name": "email_port", "format": int},
        "b2": {"name": "email_username", "format": str},
        "b3": {"name": "email_password", "format": str},
        "b4": {"name": "email_to", "format": str},
        "b5": {"name": "email_sender", "format": str},
        "b26": {"name": "email_subject", "format": str},
        # Network
        "b6": {"name": "mac", "format": str},
        "b7": {"name": "hostname", "format": str},
        "b27": {"name": "dhcp", "format": bool},  # 'true' or ''
        "b8": {"name": "ip_address", "format": str},
        "b9": {"name": "gateway", "format": str},
        "b10": {"name": "netmask", "format": str},
        "b11": {"name": "dns_primary", "format": str},
        "b12": {"name": "dns_secondary", "format": str},
        "b13": {"name": "http_port", "format": int},
        # Access
        "b14": {"name": "admin_username", "format": str},
        "b15": {"name": "admin_password", "format": str},
        "b29": {"name": "basic_auth", "format": bool},  # 'true' or ''
        "b30": {"name": "user_username", "format": str},
        "b31": {"name": "user_password", "format": str},
        # NTP
        "b16": {"name": "ntp_host", "format": str},
        "b17": {"name": "ntp_port", "format": int},
        "b18": {"name": "ntp_interval", "format": int},
        "b19": {"name": "ntp_timezone", "format": int},
        # SNMP
        "b20": {"name": "snmp_public_community", "format": str},
        "b21": {"name": "snmp_public_community2", "format": str},
        "b22": {"name": "snmp_private_community", "format": str},
        "b23": {"name": "snmp_private_community2", "format": str},
        "b24": {"name": "snmp_trap_ip", "format": str},
        "b25": {"name": "snmp_trap_community", "format": str},
        "b28": {"name": "snmp_trap_active", "format": bool},  # 'true' or ''
        # r0, r1, r2 - remote control
    }
    parsers: ClassVar[List[str]] = [
        "_parse_outs",
    ]

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return hardware_version == "2.0" and software_version in [
            "6.00",
            "6.09",
            "6.10",
            "6.12a",
            "6.12",
        ]

    def is_5_socket_ps(self):
        """Helper check whether it's version of LK 2.0 PS with 5 sockets."""
        return type(self) == LK_HW_20_PS and self.software_version == "6.12a"

    # region Parser methods that modifies data in _get()
    def _parse_outs(self, data: Dict[str, Any], path: str) -> None:
        """Parse outputs OUT with including negation."""
        # Parser is called post mapping so original keys might be missing already.
        if "out_negation" in data:
            self._context["out_negation"] = int(data.get("out_negation"))
        if "out0" in data:
            out_negation = self._context.get("out_negation")
            number_of_outputs = self.info.extras["number_of_outputs"]
            if self.is_5_socket_ps():
                number_of_outputs = 5
            for name in name_list("out", number_of_outputs, 0):
                data[name] = (
                    int_inverted(data[name]) if out_negation else int(data[name])
                )
    # endregion

    def _get(
        self,
        data: Dict[str, Any],
        path: str,
        skip_keys: Union[List[str], None] = None,
        remove_mapped_keys: bool = False,
    ) -> Dict[str, Any]:
        """Manage properties depending on path.

        Remove problematic keys, or do extra mapping for some keys.
        """
        if self.is_5_socket_ps() and path == "/st2.xml":
            # For PS HW 2.0 SW 6.12a (5 socket)
            if skip_keys is None:
                skip_keys = set()
            # Ignore r5-r11 from normal mapping - process that post _get()
            skip_keys.update(["r5", "r6", "r7", "r8", "r9", "r10", "r11"])
        elif path == "/board.xml":
            # Ignore few variables for /board.xml as they overlap in /st2.xml and /board.xml,
            # but with different meaning (out reset time instead of remote control).
            if skip_keys is None:
                skip_keys = set()
            skip_keys.update({"r0", "r1", "r2", "r3", "r4"})
        get_result = super()._get(data, path, skip_keys, remove_mapped_keys)
        if self.is_5_socket_ps() and path == "/st2.xml":
            # For PS HW 2.0 SW 6.12a (5 socket) apply parsing for r5-r9
            mapping = {
                "r5": {"name": "out0_name", "format": str},
                "r6": {"name": "out1_name", "format": str},
                "r7": {"name": "out2_name", "format": str},
                "r8": {"name": "out3_name", "format": str},
                "r9": {"name": "out4_name", "format": str},
            }
            for key, mapper in mapping.items():
                get_result[mapper["name"]] = mapper["format"](get_result[key])
            if remove_mapped_keys:
                for key in mapping:
                    get_result.pop(key)
        return get_result

    def _set_out(
        self, index: Union[int, List[int]], value: Union[int, List[int], None]
    ) -> str:
        """Prepare command for setting outputs OUT.

        Arguments:
            index: 0-5 (single or list)
            value: 0-1 (single or list)
        """
        cmd = "/outs.cgi?"
        if value is None:
            # Handle different toggle command
            if isinstance(index, list):
                cmd += "out=" + "".join(map(str, index))
            else:
                cmd += f"out={index}"
        else:
            cmd = set_cmd_helper(
                self,
                cmd,
                "out",
                index,
                value,
                operator.xor(
                    self._context["out_negation"], self.info.extras["outputs_inverted"]
                ),
                False,
            )
        # Fix command for OUT5 (non-inverted) is only for LK HW 2.0 PS 6G (HW=2.0, SW=6.12),
        # but PS 5G simply doesn't have OUT5, so for simplicity checks for LK_HW_20_PS.
        if type(self) == LK_HW_20_PS:
            if "out5=0" in cmd:
                cmd = cmd.replace("out5=0", "out5=1")
            elif "out5=1" in cmd:
                cmd = cmd.replace("out5=1", "out5=0")
        return cmd

    def _get_all(self) -> List[str]:
        """Prepare list of URLs to fetch data from."""
        return ["/st0.xml", "/board.xml", "/st2.xml"]


@dataclass
class LK_HW_20(LK_HW_20_PS):
    """Methods for working with LK2.0.

    Note: for outputs it uses unified values 0 - off, 1 - on.
    """

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 2.0",
        DeviceFamily.LK,
        "lc20",
        "https://tinycontrol.pl/en/archives/lan-controller-20/#firmware",
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6, "outputs_inverted": True},
    )
    mapping: ClassVar[Dict[str, Dict]] = {
        # Overwrite PS mapping (there will be extra b30, b31)
        **LK_HW_20_PS.mapping,
        # --- st0.xml
        "di2": {"name": "iDValue3", "format": up_to_int},
        "di3": {"name": "iDValue4", "format": up_to_int},
        "ia0": {"name": "boardTemp", "format": float_div10},
        "ia1": {"name": "boardVoltage", "format": float_div10},
        "ia2": {"name": "iAValue1", "format": float_div100},
        "ia3": {"name": "iAValue2", "format": float_div100},
        "ia4": {"name": "iAValue3", "format": float_div10},
        "ia5": {"name": "iAValue4", "format": float_div100},
        "ia6": {"name": "iAValue5", "format": float_div10},
        "ia7": {"name": "ds1", "format": float_div10},
        "ia8": {"name": "ds2", "format": float_div10},
        "ia9": {"name": "ds3", "format": float_div10},
        "ia10": {"name": "ds4", "format": float_div10},
        "ia11": {"name": "ds5", "format": float_div10},
        "ia12": {"name": "ds6", "format": float_div10},
        "ia13": {"name": "dth22 temp", "format": float_div10},
        "ia14": {"name": "dth22 hum", "format": float_div10},
        "ia15": {"name": "power1", "format": float_div1000},  # power1 is iA4*iA5
        "ia16": {"name": "energy1", "format": float_div1000},
        "ia17": {
            "name": "power2",
            "format": float_div1000,
        },  # power2 is iD4 impulse counter
        "ia18": {"name": "inp4d_ia18", "format": float_div1000},  # No idea what is it
        "ia19": {"name": "diff1", "format": float_div10},
        "freq": {"name": "pwmFrequency0", "format": int},
        "duty": {"name": "pwmDuty0", "format": float_div10},
        "pwm": {"name": "pwm0", "format": int},
        # --- st2.xml
        # Calibrations
        "k0": {"name": "cal_board_temp", "format": float_div10},
        "k1": {"name": "cal_board_voltage", "format": float_div10},
        "k2": {"name": "cal_iA1", "format": float_div100},
        "k3": {"name": "cal_iA2", "format": float_div100},
        "k4": {"name": "cal_iA3", "format": float_div10},
        "k5": {"name": "cal_iA4", "format": float_div100},
        "k6": {"name": "cal_iA5", "format": float_div10},
        "k7": {"name": "cal_iA1_sensor", "format": float_div10},
        "k8": {"name": "cal_iA4_sensor", "format": float_div10},
        "k9": {"name": "cal_iA5_sensor", "format": float_div10},
        "k10": {"name": "diff1_part1", "format": int},
        "k11": {"name": "diff1_part2", "format": int},
        # Names divided with *
        "d": {"name": "dsName1-6_iDName1-4", "format": str},
        "dz": {"name": "power2_iD4_divisor", "format": int},
        "mm": {"name": "power2_iD4_unit", "format": str},
        "mh": {"name": "power2_iD4_divisor2", "format": int},
        # Negation of iD (int with bin 0000) - it does not change visual state of inputs.
        "db": {"name": "iD_negation", "format": str},
        # --- board.xml
        "ds": {"name": "ds_read_id", "format": str},
    }

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return (
            hardware_version == "2.0"
            and LK_HW_20_PS.check_version(hardware_version, software_version) is False
        )

    def _set_pwm(self, index: int, value: int) -> str:
        """Prepare command for setting PWM(0).

        Arguments:
            index: 0 (single int)
            value: 0-1 (single int)
        """
        cmd = set_cmd_helper(self, "/ind.cgi?", "pwm", index, value, False, False)
        cmd = cmd.replace("pwm0", "pwm")
        return cmd

    def _set_pwm_duty(self, index: int, value: int) -> str:
        """Prepare command for setting PWM(0) duty.

        Arguments:
            index: 0 (single int)
            value: 0-100 (single int)
        """
        cmd = set_cmd_helper(self, "/ind.cgi?", "pwmd", index, value*10, False, False)
        cmd = cmd.replace("pwmd0", "pwmd")
        return cmd

    def _set_pwm_freq(self, index: Any, value: int) -> str:
        """Prepare command for setting PWM freq.

        Arguments:
            index: not used (only one frequency)
            value: 2_600-4_000_000
        """
        return "/ind.cgi?pwmf={}".format(value)

    def _set_ds(self, index: int, value: Any = None) -> str:
        """Prepare command for setting DS ID.

        Arguments:
            index - 1-6
            value - not used for LK2.X
        """
        cmd = f"/ind.cgi?ds={index}"
        return cmd

    def get_ds_id(self) -> str:
        """Get ID of detected DS."""
        self.get("/ind.cgi?ds=0")
        return self.get("/board.xml").get("ds_read_id")


@dataclass
class LK_HW_25(LK_HW_20):
    """Methods for working with LK2.5."""

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 2.5",
        DeviceFamily.LK,
        "lc25",
        "https://tinycontrol.pl/en/lan-controller-25/firmware-docs/#firmware",
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6, "outputs_inverted": True},
    )

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return (
            hardware_version == "2.5"
            and LK_HW_25_PS.check_version(hardware_version, software_version) is False
        )

    # pylint: disable=useless-super-delegation, useless-parent-delegation
    def _set_pwm(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting PWM.

        Arguments:
            index: 0-3 (single or list)
            value: 0-1 (single or list)
        NOTE: 1-3 can be only set, not read
        """
        return super()._set_pwm(index, value)

    # pylint: disable=useless-super-delegation, useless-parent-delegation
    def _set_pwm_duty(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting PWM duty.

        Arguments:
            index: 0-3 (single or list)
            value: 0-100 (single or list)
        NOTE: 1-3 can be only set, not read
        """
        return super()._set_pwm_duty(index, value)


@dataclass
class LK_HW_25_PS(LK_HW_20_PS):
    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "IP Power Socket v2 (LK2.5)",
        DeviceFamily.PS,
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6, "outputs_inverted": False},
    )
    mapping: ClassVar[Dict[str, Dict]] = {
        **LK_HW_20_PS.mapping,
        "out0": {"name": "out0", "format": int},
        "out1": {"name": "out1", "format": int},
        "out2": {"name": "out2", "format": int},
        "out3": {"name": "out3", "format": int},
        "out4": {"name": "out4", "format": int},
        "out5": {"name": "out5", "format": int},
        # There are 6 DS instead of 4
        "ia5": {"name": "ds5", "format": float_div10},
        "ia6": {"name": "ds6", "format": float_div10},
        "ia7": {"name": "iAValue1", "format": float_div100},  # Voltage input
        "ia8": {"name": "boardVoltage", "format": float_div10},
        # Names divided with *
        "d": {"name": "dsName1-6_iAName1_iDName1-2", "format": str},
    }

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        # Tested FW 6.15 on LK2.5 and it returns HW 2.0, so include it.
        return hardware_version in ["2.0", "2.5"] and software_version == "6.15"


@dataclass
class LK_HW_30(DeviceModel):
    """Methods for working with LK3.0.

    Note that INPD/digital for HW 3.5+ SW 1.49+ includes negation
    right in response from LK. Previous SW and HW 3.0 do NOT.
    """

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 3.0",
        DeviceFamily.LK,
        "lc30",
        "https://tinycontrol.pl/en/archives/lan-controller-30/#firmware",
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6, "number_of_digital_inputs": 4},
    )
    mapping: ClassVar[Dict[str, Dict]] = {
        # OUTs - further parsed with _parse_outs
        "out0": {"name": "out0", "format": int},
        "out1": {"name": "out1", "format": int},
        "out2": {"name": "out2", "format": int},
        "out3": {"name": "out3", "format": int},
        "out4": {"name": "out4", "format": int},
        "out5": {"name": "out5", "format": int},
        "out": {"name": name_list("out", 6, 0), "format": strint_to_int_list(6)},
        # PWM
        "pwm": {"name": name_list("pwm", 4, 0), "format": strint_to_int_list(4)},
        "pwmd0": {"name": "pwmDuty0", "format": int},
        "pwmd1": {"name": "pwmDuty1", "format": int},
        "pwmd2": {"name": "pwmDuty2", "format": int},
        "pwmd3": {"name": "pwmDuty3", "format": int},
        "pwmf0": {"name": "pwmFrequency0", "format": int},
        "pwmf1": {"name": "pwmFrequency13", "format": int},
        # EVENT
        "eventVariables": {
            "name": name_list("event", 8),
            "format": strint_to_int_list(8),
        },
        # analog
        "inpp1": {"name": "iAValue1", "format": float_div100},
        "inpp2": {"name": "iAValue2", "format": float_div100},
        "inpp3": {"name": "iAValue3", "format": float_div100},
        "inpp4": {"name": "iAValue4", "format": float_div100},
        "inpp5": {"name": "iAValue5", "format": float_div100},
        "inpp6": {"name": "iAValue6", "format": float_div100},
        # ds
        "ds1": {"name": "ds1", "format": float_div10},
        "ds2": {"name": "ds2", "format": float_div10},
        "ds3": {"name": "ds3", "format": float_div10},
        "ds4": {"name": "ds4", "format": float_div10},
        "ds5": {"name": "ds5", "format": float_div10},
        "ds6": {"name": "ds6", "format": float_div10},
        "ds7": {"name": "ds7", "format": float_div10},
        "ds8": {"name": "ds8", "format": float_div10},
        # i2c
        "dthTemp": {"name": "i2cTemp", "format": float_div10},
        "dthHum": {"name": "i2cHum", "format": float_div10},
        "bm280p": {"name": "i2cPressure", "format": float_div100},
        "dewPoint": {"name": "dewPoint", "format": float_div10},
        # pm1-10
        "pm1": {"name": "pm1.0", "format": float_div10},
        "pm2": {"name": "pm2.5", "format": float_div10},
        "pm4": {"name": "pm4.0", "format": float_div10},
        "pm10": {"name": "pm10.0", "format": float_div10},
        # co2
        "co2": {"name": "co2", "format": int},
        # m1-30 - parsed in _parse_custom_readings
        # diffs w/ diffConfig - they have special parsing _parse_diffs
        # digital
        "ind": {"name": name_list("iDValue", 4), "format": strint_to_int_list(4)},
        "inpdnn": {"name": name_list("iDNegation", 4), "format": strint_to_int_list(4)},
        # power and energy
        "power1": {"name": "power1", "format": float_div1000},
        "power2": {"name": "power2", "format": float_div1000},
        "power3": {"name": "power3", "format": float_div1000},
        "power4": {"name": "power4", "format": float_div1000},
        "power5": {"name": "power5", "format": float_div1000},
        "power6": {"name": "power6", "format": float_div1000},
        "energy1": {"name": "energy1", "format": float_div1000},
        "energy2": {"name": "energy2", "format": float_div1000},
        "energy3": {"name": "energy3", "format": float_div1000},
        "energy4": {"name": "energy4", "format": float_div1000},
        "energy5": {"name": "energy5", "format": float_div1000},
        "energy6": {"name": "energy6", "format": float_div1000},
        # serial port sensors?
        "distanceSensor": {"name": "distanceSensor", "format": float},
        "ozon": {"name": "ozon", "format": int},  # the same value as co2
        # "rhewa": {"name": 'rhewa', "format": str},
        # "barcode": {"name": 'barcode', "format": str},
        # general stuff
        "hw": {"name": "hardware_version", "format": str},
        "sw": {"name": "software_version", "format": str},
        "ip4": {"name": "mac", "format": str},
        "vin": {"name": "boardVoltage", "format": float_div100},
        "tem": {"name": "boardTemp", "format": float_div100},
        "time": {"name": "time", "format": int},
        "sname": {"name": "hostname", "format": str},
        # others
        "inpd1tim": {"name": "digital1_impulse_timer", "format": int},
        "inpd3tim": {"name": "digital3_impulse_timer", "format": int},
        # DS reading
        "dsid": {"name": "ds_read_id", "format": str},
        "d0": {"name": "duralux0", "format": float_div10},
        "d1": {"name": "duralux1", "format": float_div10},
        "d2": {"name": "duralux2", "format": float_div10},
        "d3": {"name": "duralux3", "format": float_div10},
        "d4": {"name": "duralux4", "format": float_div100},
        "d5": {"name": "duralux5", "format": int},
        "d6": {"name": "duralux6", "format": int},
        "d7": {"name": "duralux7", "format": float_div10},
        "d8": {"name": "duralux8", "format": int},
    }
    parsers: ClassVar[List[str]] = [
        "_parse_outs",
        "_parse_diffs",
        "_parse_custom_readings",
        "_parse_inpd",
    ]

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return hardware_version == "3.0"

    # region Parser methods that modifies data in _get()
    def _parse_diff(self, value, source, diffsel, depth=3):
        """Parse value of diff according to source sensor.

        Valid for HW3.0 and HW 3.5+ up to SW 1.47a
        """
        if depth == 0:
            return 0
        if source < 6 or source == 24:
            return value / 100
        elif source < 14 or source == 22 or source == 23:
            return value / 10
        elif source >= 25 and source <= 27:
            return self._parse_diff(value, diffsel[source - 25], diffsel, depth - 1)
        else:
            return value / 1000

    def _parse_diffs(self, data: Dict[str, Any], path: str) -> None:
        """Parse diffs according to sw/hw versions if set."""
        if "diff1" not in data:
            return
        if self.hardware_version != "3.0" and self.software_version >= "1.49":
            # HW3.5+ SW 1.49+ - Version with 6 diffs
            for index in range(1, 7):
                key = "diff{}".format(index)
                data[key] = float_div1000(data[key])
        elif "diffsel" in data:
            # HW 3.0 or HW3.5+ SW <1.49 - Version with 3 diffs.
            # Requires diffsel to parse, so currently it will only work for all.json.
            diffsel = list(map(int, data.get("diffsel").split("*")))
            if diffsel[0] != 25 and diffsel[1] != 26 and diffsel[2] != 27:
                # No pointing itself 25-27 is diff1-3
                for index in range(1, 4):
                    key = "diff{}".format(index)
                    data[key] = self._parse_diff(
                        float(data[key]), diffsel[index - 1], diffsel
                    )

    def _parse_custom_readings(self, data: Dict[str, Any], path: str) -> None:
        """Parse readings mappings (Modbus/1 Wire) and HW 3.0 SDMs."""
        if not (self.hardware_version and self.software_version):
            # No data
            return
        if self.hardware_version == "3.0" or (
            self.hardware_version != "3.0" and self.software_version <= "1.31"
        ):
            # LK HW 3.0 or HW 3.5+ SW <=1.31 - Dict method for sdm1-sdm14, rest is unknown
            if "sdm1" not in data:
                return
            for index in range(1, 15):
                data["mValue{}".format(index)] = float_div100(
                    data["sdm{}".format(index)]
                )
            for index in range(15, 31):
                data["mValue{}".format(index)] = 0
        elif self.hardware_version != "3.0" and self.software_version < "1.33":
            # HW 3.5+ SW 1.32+ - List method for sdm1-sdm29
            if "modbusSensor" not in data or "sdm1" not in data:
                return
            modbus_sensor = int(data.get("modbusSensor", 0))
            # Prepare list of 30 values
            tmp = list_map(int)(data.get("sdm")) + [0]
            if modbus_sensor == 5:
                tmp[6] = tmp[6] / 10
                tmp[7] = tmp[7] / 100
                tmp[8] = tmp[8] / 10
                tmp[9] = tmp[9] / 100
                tmp[10] = tmp[10] / 100
                tmp[11] = tmp[11] / 100
                tmp[12] = tmp[12] / 100
                tmp[13] = tmp[13] / 100
                tmp[14] = tmp[14] / 100
                tmp[15] = tmp[15] / 10
                tmp[16] = tmp[16] / 100
                tmp[17] = tmp[17] / 10
                tmp[18] = tmp[18] / 100
                tmp[19] = tmp[19] / 10
                tmp[20] = tmp[20] / 100
                tmp[25] = tmp[25] / 100
            elif modbus_sensor == 4:
                for index in range(0, 9):  # 0-8
                    tmp[index] = tmp[index] / 100
                for index in range(13, 29):  # 13-28
                    tmp[index] = tmp[index] / 100
            else:
                for index in range(0, 29):  # 0-28
                    tmp[index] = tmp[index] / 100
            # Update data with changes above
            for index in range(0, 30):
                data["mValue{}".format(index + 1)] = tmp[index]
        elif self.hardware_version != "3.0" and self.software_version < "1.50":
            # HW 3.5+ SW 1.33+ (3 modbus slots)
            # modbusMapping points to positions in modbusReadings
            if "modbusMapping" not in data or "modbusReadings" not in data:
                return
            modbus_mapping = [
                (int(item[0]), int(item[1:]))
                for item in data.get("modbusMapping").split("*")
            ]
            modbus_values = data.get("modbusReadings")
            tmp = []
            for index, item in enumerate(modbus_mapping):
                if item[0] == 0:
                    tmp.append(0)
                else:
                    # Slots are 1-3, so `-1`
                    tmp.append(float(modbus_values[item[0] - 1][item[1]]))
            # Update data with changes above
            for index in range(0, 30):
                data["mValue{}".format(index + 1)] = tmp[index]
        elif self.hardware_version != "3.0" and self.software_version >= "1.50":
            # HW 3.5+ SW 1.50+ - direct access to m1-30
            if "customReadings" not in data:
                return
            for index, item in enumerate(data.get("customReadings")):
                data["mValue{}".format(index + 1)] = float(item)

    def _parse_outs(self, data: Dict[str, Any], path: str) -> None:
        """Parse outputs OUT including negation."""
        if "outnn" in data:
            self._context["out_negation"] = int(data.get("outnn"))
        if "out0" in data:
            out_negation = self._context.get("out_negation")
            for name in name_list("out", self.info.extras["number_of_outputs"], 0):
                data[name] = (
                    int_inverted(data[name]) if out_negation else int(data[name])
                )

    def _parse_inpd(self, data: Dict[str, Any], path: str):
        """Parse digital inputs and include negation in returned values."""
        if "iDNegation1" in data:
            for name in name_list(
                "iDNegation", self.info.extras["number_of_digital_inputs"]
            ):
                self._context[name] = data[name]
        if "iDValue1" in data and "iDNegation1" in self._context:
            for name1, name2 in zip(
                name_list("iDValue", self.info.extras["number_of_digital_inputs"]),
                name_list("iDNegation", self.info.extras["number_of_digital_inputs"]),
            ):
                if self._context.get(name2):
                    data[name1] = int_inverted(data[name1])

    # endregion

    def _set_out(
        self, index: Union[int, List[int]], value: Union[int, List[int], None]
    ) -> str:
        """Prepare command for setting outputs OUT.

        Arguments:
            index: 0-5 (single or list)
            value: 0-1 (single or list)
        NOTE: When out is negated it will negate passed value,
        so value=1 will actually set 0 and value=0 set 1.
        """
        cmd = set_cmd_helper(
            self, "/outs.cgi?", "out", index, value, self._context["out_negation"], True
        )
        return cmd

    def _set_pwm(
        self, index: Union[int, List[int]], value: Union[int, List[int], None]
    ) -> str:
        """Prepare command for setting PWM.

        Arguments:
            index: 0-3 (single or list)
            value: 0-1 (single or list)
        """
        cmd = set_cmd_helper(self, "/outs.cgi?", "pwm", index, value, False, True)
        return cmd

    def _set_pwm_duty(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting PWM duty.

        Arguments:
            index: 0-3 (single or list)
            value: 0-100 (single or list)
        """
        cmd = set_cmd_helper(
            self,
            "/stm.cgi?",
            "pwmd",
            index,
            value,
            False,
            False,
            "{cmd_param}={index}{value}",
        )
        return cmd

    def _set_pwm_freq(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting PWM freq.

        Arguments:
            index: 0-1 (single or list; 0 - pwm0, 1 - pwm1-3 shared)
            value: 1-1_000_000
        """
        cmd = set_cmd_helper(
            self,
            "/stm.cgi?",
            "pwmf",
            index,
            value,
            False,
            False,
            "{cmd_param}={index}{value}",
        )
        return cmd

    def _set_ds(
        self, index: Union[int, List[int]], value: Union[str, List[str]]
    ) -> str:
        """Prepare command for setting DS ID.

        Arguments:
            index: 1-8
            value: DS ID
        """
        cmd = set_cmd_helper(
            self,
            "/stm.cgi?",
            "dswrite",
            index,
            value,
            False,
            False,
            "{cmd_param}={index}:{value}",
        )
        return cmd

    def get_ds_id(self) -> str:
        """Get ID of detected DS."""
        self.get("/stm.cgi?dswrite=0")
        return self.get("/json/dsi2c.json").get("ds_read_id")

    def _get_all(self) -> List[str]:
        """Prepare list of URLs to fetch data from."""
        urls = ["/json/all.json", "/json/pwmpid.json"]
        # For LK3.0 add few extra paths, as all.json is incomplete there.
        if LK_HW_30.check_version(self.hardware_version, self.software_version):
            urls.insert(0, "/json/inputs.json")
            urls.insert(0, "/json/outputs.json")
        return urls

    def _reset_to_defaults(self):
        """Prepare command to reset settings to default."""
        return "/stm.cgi?eeprom_reset=1"

    def _restart(self):
        """Prepare command to restart device."""
        return "/stm.cgi?lk3restart=1"

    def set_analog_input(
        self,
        index: Union[int, List[int]],
        sensor: Union[int, List[int]],
        calibration: Union[int, List[int], None] = None,
        multiplier: Union[float, List[float], None] = None,
    ) -> Dict[str, Any]:
        """Set sensor, calibration and multiplier for analog input.

        Arguments:
            index: 1-6 (analog input index)
            sensor: 0-20, sensor to set (range varies depending on index)
            calibration: -32768 - 32767 (calibration offset)
            multiplier: 0.01 - 327.67 (before sending it will be int(X*100)
        """
        index = apply_index_offset(index, -1)  # -1 each index
        cmd = set_cmd_helper(
            self,
            "/inpa.cgi?",
            "sensor",
            index,
            sensor,
            False,
            False,
            "{cmd_param}={index}{value}",
        )
        if calibration is not None:
            cmd = set_cmd_helper(
                self,
                cmd,
                "calibration",
                index,
                calibration,
                False,
                False,
                "{cmd_param}={index}{value}",
            )
        if multiplier is not None:
            multiplier = apply_index_offset(multiplier, 100, lambda a, b: int(a * b))
            cmd = set_cmd_helper(
                self,
                cmd,
                "multiplier",
                index,
                multiplier,
                False,
                False,
                "{cmd_param}={index}{value}",
            )
        return self.get(cmd)


@dataclass
class LK_HW_35(LK_HW_30):
    """Methods for working with LK3.5."""

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 3.5",  # Covers HW 3.5, 3.6, 3.7, 3.8
        DeviceFamily.LK,
        "lc35",
        "https://tinycontrol.pl/en/lan-controller-35/firmware/#firmware",
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6, "number_of_digital_inputs": 4},
    )

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return (
            "3.5" <= hardware_version < "3.9"
            and not software_version.endswith("ps")
            and not software_version.endswith("dcdc")
        )

    # region Parser methods that modifies data in _get()
    def _parse_inpd(self, data: Dict[str, Any], path: str):
        """Apply fix for negation of digital inputs for earlier SW.

        Since SW 1.49, LK 3.5 automatically applies negation to readings,
        but older SWs works like LK3.0, so for those use inherited parsing.
        """
        if (
            LK_HW_35.check_version(self.hardware_version, self.software_version)
            and self.software_version < "1.49"
        ):
            super()._parse_inpd(data, path)
    # endregion

    def _set_var(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting VAR/EVENT variables.

        Arguments:
            index: 1-8 (single or list)
            value: 0-1 (single or list)
        """
        # Fix indexes to be 0-based, as outside we use 1-based indexes/names for VARs.
        index = apply_index_offset(index, -1)
        cmd = set_cmd_helper(self, "/outs.cgi?", "vout", index, value, False, False)
        return cmd

    def _get_all(self) -> List[str]:
        """Prepare list of URLs to fetch data from."""
        urls = super()._get_all()
        # Early SWs for LK3.5 require extra path to get state of EVENT.
        if LK_HW_35.check_version(self.hardware_version, self.software_version) and "1.50" > self.software_version >= "1.22b":
            urls.append("/json/events_per.json")
        return urls


@dataclass
class LK_HW_39(LK_HW_35):
    """Methods for working with LK3.9."""

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 3.9",  # Logically belongs to LK3.5 family
        DeviceFamily.LK,
        "lc39",
        "https://tinycontrol.pl/en/lan-controller-35/firmware/#firmware",
        fw_update_method=FWUpdateMethod.TFTP,
        extras={"number_of_outputs": 6},
    )

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return (
            "3.9" <= hardware_version < "4.0"
            and not software_version.endswith("ps")
            and not software_version.endswith("dcdc")
        )


@dataclass
class LK_HW_35_PS(LK_HW_35):
    """Methods for working with IP Power Socket v2 (LK3.5)."""

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "IP Power Socket v2 (LK3.5)",  # 5G10A/6G10A
        DeviceFamily.PS,
        fw_update_method=FWUpdateMethod.TFTP,
    )

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return "3.5" <= hardware_version < "4.0" and software_version.endswith("ps")


@dataclass
class LK_HW_35_DCDC(LK_HW_35):
    """Methods for working with LK3.5."""

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "Converter DC/DC",
        DeviceFamily.DCDC,
        fw_update_method=FWUpdateMethod.TFTP,
    )

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return "3.5" <= hardware_version < "4.0" and software_version.endswith("dcdc")


@dataclass
class LK_HW_40(DeviceModel):
    """Device model for LK4.

    For information about possible requests see:
    https://docs.tinycontrol.pl/en/lk4/api/commands/
    """

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 4.0",
        DeviceFamily.LK,
        "lc40",
        "https://tinycontrol.pl/en/lk4/downloads/#firmware",
        fw_update_method=FWUpdateMethod.HTTP,
        extras={"number_of_outputs": 6},
    )
    mapping: ClassVar[Dict[str, Dict]] = {
        "netMac": {"name": "mac", "format": str},
        "softwareVersion": {"name": "software_version", "format": str},
        "hardwareVersion": {"name": "hardware_version", "format": str},
        "pm1": {"name": "pm1.0", "format": float},
        "pm2": {"name": "pm2.5", "format": float},
        "pm4": {"name": "pm4.0", "format": float},
        "pm10": {"name": "pm10.0", "format": float},
    }
    parsers: ClassVar[List[str]] = ["_parse_outs"]

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return hardware_version == "4.0" and not software_version.endswith("mini")

    def _parse_outs(self, data: Dict[str, Any], path: str) -> None:
        """Parse outputs OUT including negation."""
        if "outNegation" in data:
            self._context["out_negation"] = data.get("outNegation")
        if "out1" in data:
            out_negation = self._context.get("out_negation")
            for name in name_list("out", self.info.extras["number_of_outputs"]):
                data[name] = (
                    int_inverted(data[name]) if out_negation else int(data[name])
                )

    def _set_out(
        self, index: Union[int, List[int]], value: Union[int, List[int], None]
    ) -> str:
        """Prepare command for setting outputs OUT.

        Arguments:
            index: 1-n (n - self.info.extras['number_of_outputs']; single or list)
            value: 0-1 (single or list)
        NOTE: When out is negated it will negate passed value,
        so value=1 will actually set 0 and value=0 set 1.
        """
        cmd = set_cmd_helper(
            self,
            "/api/v1/save/?",
            "out",
            index,
            value,
            self._context["out_negation"],
            True,
        )
        return cmd

    def _set_pwm(
        self, index: Union[int, List[int]], value: Union[int, List[int], None]
    ) -> str:
        """Prepare command for setting PWM.

        Arguments:
            index: 1-3 (single or list)
            value: 0-1 (single or list)
        """
        cmd = set_cmd_helper(self, "/api/v1/save/?", "pwm", index, value, False, True)
        return cmd

    def _set_pwm_duty(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting PWM duty.

        Arguments:
            index: 1-3 (single or list)
            value: 0-100 (single or list)
        """
        cmd = set_cmd_helper(self, "/api/v1/save/?", "pwmDuty", index, value, False, False)
        return cmd

    def _set_pwm_freq(self, index: Any, value: int) -> str:
        """Prepare command for setting PWM freq.

        Arguments:
            index: not used (only one frequency)
            value: 1-1_000_000
        """
        cmd = "/api/v1/save/?pwmFrequency={}".format(value)
        return cmd

    def _set_var(
        self, index: Union[int, List[int]], value: Union[int, List[int]]
    ) -> str:
        """Prepare command for setting VAR/EVENT variables.

        Arguments:
            index: 1-8 (single or list)
            value: 0-1 (single or list)
        """
        cmd = set_cmd_helper(self, "/api/v1/save/?", "var", index, value, False, False)
        return cmd

    def _set_ds(
        self, index: Union[int, List[int]], value: Union[str, List[str]]
    ) -> str:
        """Prepare command for setting DS ID.

        Arguments:
            index: 1-8
            value: DS ID
        """
        cmd = set_cmd_helper(self, "/api/v1/save/?", "dsID", index, value, False, False)
        return cmd

    def get_ds_id(self) -> str:
        """Get ID of detected DS."""
        self.get("/api/v1/save/?dsReadID=0")
        return self.get("/api/v1/read/status/?dsValues").get("dsReadID")

    def _get_all(self) -> List[str]:
        """Prepare list of URLs to fetch data from."""
        return [
            "/api/v1/read/set/?generalConfig&outConfig&powerConfig&networkConfig",
            "/api/v1/read/status/?boardValues&statusValues&timeValues&outValues&pwmValues&iAValues&dsValues&i2cValues&otherSensorsValues&diffValues&iDValues&powerValues&mrValues&varValues",
        ]

    def _reset_to_defaults(self):
        """Prepare command to reset settings to default."""
        return "/api/v1/save/?eeprom_reset=1"

    def _restart(self):
        """Prepare command to restart device."""
        return "/api/v1/save/?restart=1"


@dataclass
class TCPDU(LK_HW_40):
    """Device model for tcPDU.

    For information about possible requests see:
    https://docs.tinycontrol.pl/en/tcpdu/api/commands/
    """

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "tcPDU",
        DeviceFamily.TCPDU,
        "tcpdu",
        "https://tinycontrol.pl/en/tcpdu/downloads/#firmware",
        fw_update_method=FWUpdateMethod.HTTP,
        extras={"number_of_outputs": 7},
    )

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return hardware_version in ["1.0", "1.1"] and software_version.endswith("tcPDU")

    # Unset few commands - there are no PWM in tcPDU
    _set_pwm = None
    _set_pwm_duty = None
    _set_pwm_freq = None

    def _get_all(self) -> List[str]:
        """Prepare list of URLs to fetch data from.

        Compared to LK4 does not include pwm, analog, pm, co2, mapped (modbus readings).
        """
        return [
            "/api/v1/read/set/?generalConfig&outConfig&powerConfig&networkConfig",
            "/api/v1/read/status/?boardValues&statusValues&timeValues&outValues&dsValues&i2cValues&diffValues&iDValues&powerValues&varValues",
        ]


@dataclass
class LK_HW_40_mini(LK_HW_40):
    """Device model for LK4mini.

    It's basically the same as LK4 minus outputs, PWM outputs, analog
    inputs, digital inputs, power and energy, serial port.
    """

    info: ClassVar[Union[DeviceInfo, None]] = DeviceInfo(
        "LK HW 4.0 mini",
        DeviceFamily.LK,
        "lc40mini",
        "https://tinycontrol.pl/en/lk4mini/downloads/#firmware",
        fw_update_method=FWUpdateMethod.HTTP,
        extras={"number_of_outputs": 0},
    )
    parsers: ClassVar[List[str]] = []

    @classmethod
    def check_version(
        cls, hardware_version: Union[str, None], software_version: str
    ) -> bool:
        return hardware_version in ["4.0", "4.1"] and software_version.endswith("mini")

    # Unset few commands - there are no OUT, PWM in LK4 mini
    _set_out = None
    _set_pwm = None
    _set_pwm_duty = None
    _set_pwm_freq = None

    def _get_all(self) -> List[str]:
        """Prepare list of URLs to fetch data from."""
        return [
            "/api/v1/read/set/?generalConfig&networkConfig",
            "/api/v1/read/status/?boardValues&statusValues&timeValues&dsValues&i2cValues&otherSensorsValues&diffValues&mrValues&varValues",
        ]


DEVICE_MODELS = [
    LK_HW_40_mini,
    TCPDU,
    LK_HW_40,
    LK_HW_39,
    LK_HW_35,
    LK_HW_35_PS,
    LK_HW_35_DCDC,
    LK_HW_30,
    LK_HW_25,
    LK_HW_25_PS,
    LK_HW_20,
    LK_HW_20_PS,
]


def detect_version(version_text: str) -> Union[str, None]:
    """Detect hw version based on sw version (from discovery).

    Currently it is only useful for LK20/25.
    """
    pattern = re.compile(r"^(\d\.\d+)(.*)$")
    match = pattern.search(version_text)
    hardware_version = ""
    if match is not None:
        parts = match.groups()
        software_version = float(parts[0])
        # First check 'frozen' versions like 2.0 or 3.0
        if software_version in [
            2.0,
            2.03,
            2.07,
            2.09,
            3.03,
            3.06,
            3.10,
            3.13,
            3.15,
            3.18,
        ]:
            hardware_version = "2.0"
        elif software_version in [6.0, 6.09, 6.10, 6.12]:  # power socket 2.0
            hardware_version = "2.0"
        elif software_version == 6.15:  # power socket 2.5
            hardware_version = "2.5"
        elif software_version in [2.01, 3.01, 3.02]:
            hardware_version = "2.5"
    return hardware_version


def get_device_info(
    hardware_version: str, software_version: str, asdict_: bool = False
) -> Union[DeviceInfo, Dict[str, Any]]:
    """Return device info based on given HW and SW."""
    device_info = None
    for device_model in DEVICE_MODELS:
        if device_model.check_version(hardware_version, software_version):
            device_info = device_model.info
            break
    if not device_info:
        device_info = DeviceInfo("?", "?")
    if asdict_:
        device_info = asdict(device_info)
    return device_info


def get_device(
    hardware_version: str,
    software_version: str,
    host: str,
    schema: str = "http",
    port: int = 80,
    username: str = "",
    password: str = "",
    session: Union[ClientSession, None] = None,
) -> Union[DeviceModel, None]:
    """Get Device instance."""
    for device_model in DEVICE_MODELS:
        if device_model.check_version(hardware_version, software_version):
            return device_model(
                host,
                schema,
                port,
                username,
                password,
                hardware_version,
                software_version,
                session=session,
            )
    return None


def _get_version(
    response: Union[Any, None],
    host: str,
    port: str,
    username: str,
    password: str,
    with_info: bool,
    with_device: bool,
    session: Union[ClientSession, None],
) -> Union[Dict[str, Any], None]:
    """Analyze responses to get version info."""
    if response is None:
        return response
    version_info = parse_version(response["parsed"])
    version_info["network_info"] = {
        "host": host,
        "schema": str(response["_response"].url).split(":", 1)[0],
        "port": port,
        "username": username,
        "password": password,
    }
    if with_info:
        version_info.update(
            get_device_info(
                version_info["hardware_version"],
                version_info["software_version"],
                asdict_=True,
            )
        )
    if with_device:
        version_info["device_model"] = get_device(
            version_info["hardware_version"],
            version_info["software_version"],
            **version_info["network_info"],
            session=session,
        )
    return version_info


def _get_version_initial(
    exc: Exception, schema: str, port: int, silent: bool
) -> Tuple[str, str, int]:
    """Handle first response in get_version - prepare data for second request."""
    path = ""
    try:
        raise exc
    except TinyToolsRequestNotFound:
        # Likely LK3.X
        path = "/xml/stat.xml"
    except TinyToolsRequestInternalServerError:
        # Likely LK4/LK4mini/tcPDU
        path = "/api/v1/read/set/?generalConfig"
    except TinyToolsRequestSSLError:
        # When LK3 has https enabled it will redirect http and with ssl verification we land here.
        port = 443
        path = "/xml/stat.xml"
        schema = "https"
    except (TinyToolsRequestConnectionError, TinyToolsRequestTimeout):
        # Seems that newer SW LK4/tcPDU with https get here, but still include timeout
        port = 443
        path = "/api/v1/read/set/?generalConfig"
        schema = "https"
    except TinyToolsRequestError:
        if not silent:
            raise
    return path, schema, port


def get_version(
    host: str,
    port: int = 80,
    schema: str = "http",
    username: str = "",
    password: str = "",
    with_info: bool = True,
    with_device: bool = False,
    silent: bool = True,
) -> Union[Dict[str, Any], None]:
    """Query device for version and optionally device model.

    To work with https on port different than 443, schema has to be set to https.
    Normally LK always uses port 443 for https.
    """
    response = None
    try:
        response = get(host, "/st2.xml", schema, port, username, password)
    except TinyToolsRequestError as exc:
        path, schema, port = _get_version_initial(exc, schema, port, silent)
        if path:
            response = get(host, path, schema, port, username, password, silent=silent)
    return _get_version(
        response, host, port, username, password, with_info, with_device, None
    )


async def async_get_version(
    host: str,
    port: int = 80,
    schema: str = "http",
    username: str = "",
    password: str = "",
    with_info: bool = True,
    with_device: bool = False,
    silent: bool = True,
    session: Union[ClientSession, None] = None,
) -> Union[Dict[str, Any], None]:
    response = None
    try:
        response = await async_get(
            host, "/st2.xml", schema, port, username, password, session=session
        )
    except TinyToolsRequestError as exc:
        path, schema, port = _get_version_initial(exc, schema, port, silent)
        if path:
            response = await async_get(
                host,
                path,
                schema,
                port,
                username,
                password,
                silent=silent,
                session=session,
            )
    return _get_version(
        response, host, port, username, password, with_info, with_device, session
    )


async_get_version.__doc__ = get_version.__doc__
