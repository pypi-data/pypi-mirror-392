import re

from ._utils import safesplit

# regex to parse ascii files

HEADER = re.compile(r"HEADER\s*?{\s*?(?P<header>.*?)\s*?}", re.M | re.S)
HDR = re.compile(r"HDR\s+(?P<property>.*?)\s*?$", re.M | re.S)
CRS = re.compile(
    r"GOCAD_ORIGINAL_COORDINATE_SYSTEM(?P<crs>.+?)END_ORIGINAL_COORDINATE_SYSTEM",
    re.M | re.S,
)


def _parse_properties(block: str) -> dict:
    """Parse GOCAD Object attributes.

    Args:
        block (str): Single GOCAD Object string "GOCAD ... END".

    Returns:
        dict: Object attributes.
    """
    attribs = {}
    # get header block(s) and lines
    properties = "\n".join(HEADER.findall(block) + HDR.findall(block))
    for line in properties.splitlines():
        line = line.strip()  # noqa: PLW2901
        if not line:
            continue
        key, value = line.split(":")
        key = key.strip("*").strip().lower()
        value = value.strip()
        attribs[key] = value
    return attribs


def _parse_coordinate_system(block: str) -> dict:
    crs = {}
    match = CRS.search(block)
    if match:
        for line in match["crs"].strip().splitlines():
            key, *value = safesplit(line)
            crs[key.lower()] = " ".join(value)
    return crs


def _parse_geologic_information(block: str) -> dict:
    info = {}
    flags = ("GEOLOGICAL_TYPE", "GEOLOGICAL_FEATURE")
    for flag in flags:
        match = re.search(flag + r"\s+?(.+?)\s*?$", block, re.MULTILINE)
        if match:
            info[flag.lower()] = match.group(1)
    strati = re.search(r"STRATIGRAPHIC_POSITION\s+?(.+?)\s*?$", block, re.MULTILINE)
    if strati:
        age, time = strati.group(1).split()
        info["stratigraphic_age"], info["stratigraphic_time"] = age, float(time)
    return info


def read_header(block: str, *args, **kwargs):  # noqa: ARG001
    block = block.strip()
    if not block.startswith("GOCAD "):
        msg = "Invalid GOCAD object"
        raise OSError(msg)

    first, block = block.split("\n", 1)
    _, geometry, version = first.split()

    attributes = _parse_properties(block)
    header = {
        "name": attributes.pop("name", "Unknown block"),
        "geometry": geometry,
        "version": version,
    }
    header.update(_parse_geologic_information(block))
    header["crs"] = _parse_coordinate_system(block)
    header.update(attributes)

    return header
