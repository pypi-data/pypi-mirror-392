from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import Object, read_grid


@dataclass
class Grid(Object):
    """Grid-geometry type object (Voxet, GSurf, SGrid)"""

    origin: tuple[float] = field(default_factory=tuple)
    dimension: tuple[float] = field(default_factory=tuple)
    spacing: tuple[float] = field(default_factory=tuple)
    axes: tuple[tuple[float]] = field(default_factory=tuple)
    data: dict[str : np.ndarray] = field(default_factory=list)

    @classmethod
    def from_chunk(cls, chunk: str, *args, **kwargs) -> Object:
        self = cls()
        geometry, data = read_grid(chunk, *args, **kwargs)
        # params, self.data = read_grid(chunk, *args, **kwargs)
        self.origin, self.dimension, self.spacing, self.axes = geometry
        self.data = dict(data)
        return self

    def __repr__(self) -> str:
        s = super().__repr__() + "\n"
        s += f"\tN cells:\t{' x '.join(str(n) for n in self.dimension)}\n"
        s += f"\tOrigin:  \t{len(self.origin)}\n"
        s += f"\tCell size:\t{self.spacing}\n"
        s += f"\tGrid axes:\t{self.axes[0]}\n"
        for axis in self.axes[1:]:
            s += f"\t\t\t{axis}\n"
        s += f"\tN properties:\t{len(self.data)} {tuple(self.data)}\n"
        return s
