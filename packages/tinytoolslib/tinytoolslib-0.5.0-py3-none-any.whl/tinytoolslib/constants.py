"""Constants related to tinycontrol devices."""

from enum import Enum


LK_UDP_PORT = 30403
"""Port for UDP commands"""

LK_UDP_DISCOVERY_MSG = b"Discovery: Who is out there?"
"""Message for Discovery query"""

LK_UDP_BOOTLOADER_MSG = b"\x12\xf4\x81"
"""Message for starting bootloader/restart device"""


FW_URL_TEMPLATE = "https://tinycontrol.pl/firmware/{}/latest/"
"""URL format for getting information about firmware from tinycontrol.pl"""


class FWUpdateMethod(str, Enum):
    """Method used for updating FW.

    HTTP - for LK4, tcPDU (generally ESP32 based ones)
    TFTP - for LK3.5, LK3, LK2.5, LK2
    """

    TFTP = "TFTP"
    HTTP = "HTTP"


class DeviceFamily(str, Enum):
    """Device families.

    PS and DCDC are pretty much the same as LK (UI differs)
    """

    LK = "LK"
    PS = "PS"  # Power socket
    DCDC = "DCDC"  # Converter DC/DC
    TCPDU = "tcPDU"
