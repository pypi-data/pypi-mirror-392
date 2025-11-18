from __future__ import annotations

from dataclasses import dataclass, field

from . import Object, read_mesh


@dataclass
class Mesh(Object):
    """Mesh-geometry type object (VSet, TSurf, TSolid)"""

    points: list[tuple[float]] = field(default_factory=list)
    cells: list[list[int]] = field(default_factory=list)
    point_data: dict[str, list[str]] = field(default_factory=dict)
    cell_data: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_chunk(cls, chunk, *args, **kwargs) -> Object:
        self = cls()
        self.points, self.cells, self.point_data, self.cell_data = read_mesh(
            chunk, *args, **kwargs
        )
        return self

    # WIP: Make sure Layer.__getattr__ is called first !
    # def __getattr__(self, name: str) -> Any:
    #     """Make self.data accessible as class attributes.

    #     Any failed `self.name` attempt will trigger a lookup in
    #     self.data.keys() and return self.data[name] if match.

    #     Args:
    #         name (str): Point data attribute.

    #     Raises:
    #         AttributeError: Non existing keys will raise AttributeError.

    #     Returns:
    #         Any: Identical to `self.data[name]`.
    #     """
    #     if name in self.__getattribute__('data'):
    #         return self.data[name]
    #     else:
    #         raise AttributeError(f"'{self.__class__}' object has no attribute '{name}'")

    def __repr__(self) -> str:
        s = super().__repr__() + "\n"
        s += f"\tN Points:\t{len(self.points)}\n"
        s += f"\tN Cells:\t{len(self.cells)}\n"
        s += f"\tN Arrays:\t{len(self.arrays)}"
        return s

    @property
    def arrays(self):
        return list(self.point_data.keys()) + list(self.cell_data.keys())
