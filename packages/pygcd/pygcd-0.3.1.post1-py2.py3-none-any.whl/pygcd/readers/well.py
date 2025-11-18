from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np

DT = np.dtype(">f4")

from ._utils import safesplit

"""The Well ASCII format contains 4 sections:
(in addition to the sections relative to an Object definition)
    - a header section
    - a wellpath section
    - a well curves (log) section
    - a zone/marker section.
Curves data can be externalized in ASCII/BINARY_DATA_FILE (big-endian float 32).
Well path bounded by 2 endpoints can also be externalized in WP_CATALOG_FILE (useless in our case ?)
"""

########################
# WELL DATA STRUCTURES #
########################


@dataclass
class WellMarker:
    name: str  # marker (non unique) identifier
    zm: float  # depth along the path (from collar)
    unit: str = ""
    feature: str = ""
    horizon: str = ""
    dirdip: tuple[float, float] = ()  # (azimuth, dip) all in °
    norm: tuple[float, float, float] = ()  # (x,y,z)


@dataclass
class WellZone:
    name: str  # marker (non unique) identifier
    zfrom: float  # depth along the path (from collar)
    zto: float  # depth along the path (from collar)
    unit: str = ""
    feature: str = ""
    horizon: str = ""
    dip: tuple[float, float] = ()  # (azimuth, dip)
    norm: tuple[float, float, float] = ()  # (x,y,z)


@dataclass
class WellCurve:
    name: str
    zm: list = field(default_factory=list)
    values: list = field(default_factory=list)
    na: float = np.nan
    z_unit: str = ""
    v_unit: str = ""

    def __len__(self):
        return len(self.values)


################################
# EXTERNAL CURVES DATA STRUCTS #
################################


@dataclass
class _InternalData:
    file: str = None
    curves: list = field(default_factory=list)

    def append(self, name: str = ""):
        assert name not in self.curves
        self.curves.append(WellCurve(name))

    @property
    def current(self) -> WellCurve:
        return self.curves[-1] if self.curves else None

    def load(self) -> list[WellCurve]:
        return self.curves


@dataclass
class _ExternalAsciiData(_InternalData):
    ncolumns: int = -1
    nrows: int = -1
    depth_column: int = 0
    columns: list = field(default_factory=list)

    def __setattr__(self, name: str, value: Any):
        if name == "column":
            assert self.columns
            self.columns[-1] = value
        else:
            super().__setattr__(name, value)

    def append(self, name: str = "", col: int = -1):
        super().append(name)
        self.columns.append(col)

    @cached_property
    def data(self) -> np.ndarray:
        assert (self.nrows > 0) or (self.ncolumns > 0)
        return np.fromfile(self.file, sep=" ").reshape(self.nrows, self.ncolumns)

    def load(self) -> list[WellCurve]:
        zm = self.data[:, self.depth_column]
        for curve, column in zip(self.curves, self.columns):
            assert curve.name
            assert 0 <= column < self.ncolumns
            curve.zm = zm
            curve.values = self.data[:, column]
        return self.curves


@dataclass
class _ExternalBinaryData(_InternalData):
    offsets: list = field(default_factory=list)
    nb_pts: list = field(default_factory=list)

    def __setattr__(self, name: str, value: Any):
        if name == "seek":
            assert self.offsets
            self.offsets[-1] = int(value)
        elif name == "npts":
            assert self.nb_pts
            self.nb_pts[-1] = int(value)
        else:
            super().__setattr__(name, value)

    def append(self, name: str = "", nbp: int = 0, off: int = 0):
        super().append(name)
        self.nb_pts.append(nbp)
        self.offsets.append(off)

    def load(self) -> list[WellCurve]:
        for curve, off, n in zip(self.curves, self.offsets, self.nb_pts):
            assert curve.name
            assert n
            zv = np.fromfile(self.file, offset=off, count=2 * n, dtype=DT).astype(float)
            curve.zm = zv[:n]
            curve.values = zv[n:]
        return self.curves


###############
# WELL READER #
##############


def read_well(block, filename: str = ".", *args, **kwargs):  # noqa: ARG001
    collar, path = (), []
    kb = 0.0
    markers, zones, curves = [], [], []
    in_marker, in_curve = False, False
    curve_data, wp_catalog = _InternalData(), []
    path_curve = [None, None, None]

    for line in block.splitlines():
        line = line.strip()  # noqa: PLW2901
        if not line:
            continue

        what, _, rest = line.partition(" ")
        stuff = safesplit(rest)

        if in_marker:
            if what == "UNIT":
                markers[-1].unit = rest
                continue
            if what == "FEATURE":
                markers[-1].feature = str(*stuff)
                continue
            if what == "MREF":
                markers[-1].horizon = str(*stuff)
                continue
            if what == "NORM":
                markers[-1].norm = tuple(float(el) for el in stuff)
                continue
            if what == "DIP":  # WARNING : The DIP information is given in Grads.
                markers[-1].dip = tuple(float(el) * 180 / 200 for el in stuff)
                continue
            if what == "DIPDEG":
                markers[-1].dip = tuple(float(el) for el in stuff)
                continue
            in_marker = False

        if in_curve:
            curve = curve_data.current
            assert curve is not None
            if what == "END_CURVE":
                in_curve = False
                continue
            if what == "PROPERTY":
                assert not curve.name
                curve.name = str(*stuff)
                continue
            if what == "UNITS":
                curve.z_unit, curve.v_unit = stuff
            elif what in "PROP_UNIT":
                curve.v_unit = str(*stuff)
            elif what in "ZM_UNIT":
                curve.z_unit = str(*stuff)
            elif what == "PROP_NO_DATA_VALUE":
                curve.na = float(*stuff)
            elif what == "REC":
                zm, val = (float(e) for e in stuff)
                curve.zm.append(zm)
                curve.values.append(val)
                continue
            elif what == "HOLE":
                continue
            elif what == "NPTS":
                curve_data.npts = int(*stuff)
                continue
            elif what == "SEEK":
                curve_data.seek = int(*stuff)
                continue
            elif what == "COLUMN":
                curve_data.column = int(*stuff)
                continue

        if what in ("WREF", "VRTX"):
            x, y, z = (float(e) for e in stuff)
            if what == "WREF":
                collar = [x, y, z]
            else:
                if len(path) == 0:
                    zm = 0
                else:
                    zm = np.linalg.norm(np.asarray(path[-1]) - np.array(collar))
                path.append((x, y, z, zm))
            continue
        if what == "KB":
            kb = float(*stuff)
            if kb:
                assert collar, "Well path must start with collar !"
                collar[2] = kb
            continue
        if what in ("PATH", "TVSS_PATH", "TVD_PATH"):
            assert collar, "Well path must start with collar !"
            zm, z, dx, dy = (float(e) for e in stuff)
            x, y = collar[0] + dx, collar[1] + dy
            if what.startswith("TVD"):
                z -= collar[2]
            path.append((x, y, z, zm))
            continue
        if what == "MRKR":
            label, _, zm = stuff
            markers.append(WellMarker(label, zm=float(zm)))
            in_marker = True  # marker extra info can be multiline ...
            continue
        if what == "ZONE":
            label, za, zb, i = stuff
            markers.append(WellZone(label, zfrom=float(za), zto=float(zb)))
            continue
        if what.startswith("PATH_CURVE_"):
            if what.endswith("X"):
                path_curve[0] = stuff
            elif what.endswith("Y"):
                path_curve[1] = stuff
            elif what.endswith("Y"):
                path_curve[2] = stuff
            else:
                raise AssertionError()
        elif what in ("WP_CATALOG_FILE", "BINARY_DATA_FILE", "ASCII_DATA_FILE"):
            # external data are declared BEFORE curve headers
            # we need to store the content and process it later
            file = Path(filename).parent / str(*stuff)
            if what == "WP_CATALOG_FILE":
                assert not wp_catalog
                # wp_catalog = np.fromfile(file, dtype=DT)
                # FIXME: external data is a list of ZM_NPTS
                #    Zm values along the path ... really necessary ?
                continue
            assert not curve_data.current
            if what.startswith("BINARY"):
                curve_data = _ExternalBinaryData(file=file)
            else:
                curve_data = _ExternalAsciiData(file=file)
        elif what == "WELL_CURVE":
            assert not in_curve
            curve_data.append()
            in_curve = True
        continue

    curves = curve_data.load()
    if all(path_curve):
        assert not path
        path = np.column_stack(
            [next(c.values for c in curves if c.name == n) for n in path_curve]
        )

    return collar, path, markers, zones, curves
