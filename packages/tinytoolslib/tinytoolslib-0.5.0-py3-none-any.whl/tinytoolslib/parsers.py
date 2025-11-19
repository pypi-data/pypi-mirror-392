from datetime import datetime
from functools import lru_cache


def parse_version(data):
    """Parse version info from data."""
    hw = None
    sw = None
    if "ver" in data:
        # LK2.X
        hw = "2." + data.get("hw")
        sw = data.get("ver")
    elif "sw" in data:
        # LK3.X
        hw = data.get("hw")
        sw = data.get("sw")
    elif "hardwareVersion" in data:
        hw = data.get("hardwareVersion")
        sw = data.get("softwareVersion")
    return {
        "hardware_version": hw,
        "software_version": sw,
    }


def int_inverted(value):
    """Invert 0/1 value."""
    return int(not int(value))


def up_to_int(value):
    """Convert text 'up' to 1 for LK2.5"""
    if value == "up":
        return 1
    return 0


def float_div10(value):
    """Convert string number to float divided by 10"""
    return float(value) / 10


def float_div100(value):
    """Convert string number to float divided by 100"""
    return float(value) / 100


def float_div1000(value):
    """Convert string number to float divided by 1000"""
    return float(value) / 1000


def str_datetime(value):
    """Convert string timestamp to datetime"""
    return datetime.fromtimestamp(int(value))


def strint_to_int_list(length):
    """Convert string with number to list of ints (one for bit)"""
    return lambda x: list(
        reversed([int(item) for item in bin(int(x)).lstrip("-0b").zfill(length)])
    )


def strdot_to_int_list(value):
    """Convert string with numbers divided with '*' to list of ints"""
    return [int(item) for item in value.split("*")]


def int_mul(value, multiplier):
    """Multiply value and return int."""
    return int(value * multiplier)


def name_list(name, count, start=1):
    """Return list of names with included index."""
    tag = "{}"
    if tag not in name:
        name = name + tag
    return [name.format(i) for i in range(start, start + count)]


@lru_cache(None)
def list_map(type_):
    """Return function for mapping list items to given type."""
    return lambda x: list(map(type_, x))
