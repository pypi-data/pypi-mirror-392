import re

"""GOCAD Object file template:

GOCAD <type> <version>
HEADER {
name: <name>
[<key>: <value>]
}
[PROPERTIES <name> ... <name>]
ATOM <ID> <X> <Y> <Z> [<PV> ...]
[<SUBSET_TYPE>]
[<CELL_TYPE> <ATOM> ... <ATOM>]
END

based on : http://paulbourke.net/dataformats/gocad/gocad.pdf
"""

OBJECT = re.compile(r"(?P<object>GOCAD.*?END)\s*?$", re.M | re.S)


def find_objects(raw: str) -> list:
    """Split raw text into object chunks"""
    return OBJECT.findall(raw)


# geometry readers
from .grid import read_grid
from .header import read_header
from .mesh import read_mesh
from .well import read_well
