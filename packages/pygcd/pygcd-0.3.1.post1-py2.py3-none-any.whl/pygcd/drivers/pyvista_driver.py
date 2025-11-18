from typing import Union
from warnings import warn

import numpy as np

from ..objects import Chunk, Grid, Mesh, Object, Well
from ._cells import ravel_cells
from ._utils import iterdict


def reencode(s):
    return str(s.encode("ascii", "replace"), "ascii")


def _cast_mesh(mesh: Mesh):
    assert isinstance(mesh, Mesh)

    from pyvista import CellType, PolyData, UnstructuredGrid

    if mesh.geometry.name == "VSet":
        part = PolyData(mesh.points)
    elif mesh.geometry.name == "PLine":
        part = PolyData(mesh.points, lines=ravel_cells(mesh.cells))
    elif mesh.geometry.name == "TSurf":
        part = PolyData(mesh.points, faces=ravel_cells(mesh.cells))
    elif mesh.geometry.name == "TSolid":
        part = UnstructuredGrid(
            ravel_cells(mesh.cells), [CellType.TETRA] * len(mesh.cells), mesh.points
        )
    else:
        msg = f"Wrong geometry type: {mesh.geometry.name}"
        raise ValueError(msg)

    # record cell_data
    for name, value in mesh.cell_data.items():
        part[reencode(name)] = value
    # record point_data
    for name, value in mesh.point_data.items():
        part[reencode(name)] = value

    return part


def _cast_well(well: Well):
    assert isinstance(well, Well)

    # raise NotImplementedError(
    #     f"Ignoring unsupported GOCAD object: {well.geometry.name} ('{well.name}')"
    # )

    from pyvista import MultiBlock, PolyData

    vtm = MultiBlock()
    # vtm["collar"] = PolyData(well.collar)
    # if len(well.markers) > 0:
    #     vtm["markers"] = PolyData(well.coords([wm.zm for wm in well.markers]))
    #     for prop in WellMarker.__dataclass_fields__.keys():  # forward properties
    #         array = np.array([wm.__getattribute__(prop) for wm in well.markers])
    #         if array.dtype.type is np.str_:
    #             array = np.array([reencode(el) for el in array])
    #         vtm["markers"][reencode(prop)] = array
    # if len(well.zones) > 0:
    #     _from = well.coords([s.zfrom for s in well.zones])
    #     _to = well.coords([s.zto for s in well.zones])
    #     pts = np.empty((_from.size + _to.size,), dtype=float)
    #     pts[0::2], pts[1::2] = _from, _to
    #     lines = []
    #     for i in range(len(_from)):
    #         lines += [2, 2 * i, 2 * i + 1]
    #     vtm["stratum"] = PolyData(pts, lines=lines)
    #     for prop in WellZone.__dataclass_fields__.keys():  # forward properties
    #         array = np.array([ws.__getattribute__(prop) for ws in well.zones])
    #         if array.dtype.type is np.str_:
    #             array = np.array([reencode(el) for el in array])
    #         vtm["stratum"][reencode(prop)] = array
    if len(well.path) > 0:
        pts = np.asarray(well.path, float)[:, :3]
        n = len(pts)
        vtm["path"] = PolyData(pts, lines=[n, *list(range(n))])
    return vtm


def _cast_grid(grid: Grid):
    from pyvista import StructuredGrid

    msg = f"Ignoring unsupported GOCAD object: {grid.geometry.name} ('{grid.name}')"
    raise NotImplementedError(msg)
    return StructuredGrid()


def to_pyvista(obj: Union[Object, list]):
    from pyvista import DataObject, MultiBlock

    if isinstance(obj, list):
        assert len(obj) > 0
        vtm = MultiBlock()
        for piece in obj:
            try:
                part = to_pyvista(piece)
                name = piece.name
                if name and name not in vtm:
                    vtm[name] = part
                else:
                    vtm.append(part)
            except NotImplementedError:
                msg = f"Ignoring unsupported GOCAD object: {piece.geometry.name} ('{piece.name}')"
                warn(
                    msg,
                    Warning,
                    stacklevel=2,
                )
        return vtm

    # build pv.DataSet
    if isinstance(obj, Chunk):
        obj = obj.decode()
    assert isinstance(obj, Object), f"Invalid object type: {type(obj)}"

    if isinstance(obj, Mesh):  # -> PolyData or UnstructuredGrid
        part = _cast_mesh(obj)
    elif isinstance(obj, Well):  # -> MultiBlock (of PolyData)
        part = _cast_well(obj)
    elif isinstance(obj, Grid):  # -> StructuredGrid
        part = _cast_grid(obj)
    else:
        msg = f"Invalid object type: {type(obj)}"
        raise ValueError(msg)

    assert isinstance(part, DataObject), f"Invalid object type: {type(obj)}"

    # record field_data
    part.add_field_data([reencode(obj.name)], "name")
    part.add_field_data([reencode(obj.geometry.name)], "geometry")
    for name, value in iterdict(obj.fields):
        name = reencode(name).strip("*").replace("*", ":")  # noqa: PLW2901
        if name in part.field_data:
            warn(
                f"Duplicated property will be overwritten: {name}",
                Warning,
                stacklevel=2,
            )
        if isinstance(value, str):
            value = [reencode(value)]  # noqa: PLW2901
        elif not hasattr(value, "__iter__"):
            value = [value]  # noqa: PLW2901
        part.add_field_data(value, name)

    return part
