from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

import numpy as np
from numpy.typing import ArrayLike
from scipy.interpolate import splev, splprep

from . import Object, WellCurve, WellMarker, WellZone, read_well


@dataclass
class Well(Object):
    """Well object"""

    collar: tuple[float] = field(default_factory=tuple)
    path: list[tuple[float]] = field(default_factory=list)
    markers: list[WellMarker] = field(default_factory=list)
    zones: list[WellZone] = field(default_factory=list)
    curves: list[WellCurve] = field(default_factory=list)

    @classmethod
    def from_chunk(cls, chunk, *args, **kwargs) -> Object:
        self = cls()
        self.collar, self.path, self.markers, self.zones, self.curves = read_well(
            chunk, *args, **kwargs
        )
        return self

    def __setattr__(self, __name: str, __value: list[tuple[float]]) -> None:
        """Manage cached properties"""
        if __name == "path" and "spline" in self.__dict__:
            del self.__dict__["spline"]
        return super().__setattr__(__name, __value)

    def __repr__(self) -> str:
        s = super().__repr__() + "\n"
        s += f"\tCollar:\t{self.collar}\n"
        s += f"\tN Path:\t{len(self.path)}\n"
        s += f"\tN Markers:\t{len(self.markers)}\n"
        s += f"\tN Strata:\t{len(self.zones)}\n"
        s += f"\tN Curves:\t{len(self.curves)}\n"
        return s

    @cached_property
    def spline(self):
        points = np.array(self.path, float)
        if len(points) == 0:  # no path : use vertical hole from collar
            points = np.array((*self.collar, 0), float)
        if len(points) == 0:  # empty well ... raise ValueError
            msg = f"Well is empty: {self}"
            raise ValueError(msg)

        # remove duplicates (should not exists ... but ...)
        points = np.unique(points, axis=0)
        # single point path : use vertical hole
        if len(points) == 1:
            ref = points.squeeze()

            def spline(zm):  # wrapper around interpolator
                xy = np.tile(ref[:2], (np.asarray(zm).size, 1))
                z = ref[2] + ref[3] - zm
                return np.c_[xy, z]

        # multi point path : spline interpolation
        else:
            # splprep.u must be sorted
            order = np.argsort(points[:, -1])
            points = points[order, :]
            # interpolate using spline
            x = [points[:, 0], points[:, 1], points[:, 2]]
            u = points[:, 3].flatten()
            k = min(len(points) - 1, 3)
            tck, _ = splprep(x, u=u, k=k, s=0)

            def spline(zm):  # wrapper around interpolator
                return np.column_stack(splev(zm, tck))

        return spline

    def coords(self, zm: ArrayLike) -> ArrayLike:
        u = np.asarray(zm, float).flatten()
        interp = self.spline
        return interp(u)
