from __future__ import annotations

from warnings import warn

import numpy as np

from ..objects import Chunk, Grid, Mesh, Object, Well
from ._utils import iterdict


def build_df(obj: Object) -> GeoDataFrame:  # noqa: F821
    from geopandas import GeoDataFrame

    if isinstance(obj, Mesh):
        geometries = _cast_mesh(obj)
    elif isinstance(obj, Well):
        geometries = _cast_well(obj)
    elif isinstance(obj, Grid):
        geometries = _cast_grid(obj)
    else:
        msg = f"Invalid object type: {type(obj)}"
        raise ValueError(msg)

    if not isinstance(geometries, dict):
        geometries = {obj.geometry.name: geometries}

    n = len(geometries)

    fields = obj.fields
    crs = fields.pop("crs", {})  # handled separatly
    epsg = crs.get("PROJECTION", "").strip('"')
    fields["name"] = obj.name
    fields["type"] = list(geometries.keys())
    # flatten nested fields
    fields = {k: [v] * n for k, v in iterdict(fields)}
    return GeoDataFrame(fields, geometry=list(geometries.values()), crs=epsg).set_index(
        "name"
    )


def _cast_mesh(mesh: Mesh) -> dict[Geometry]:  # noqa: F821
    from shapely.geometry import (
        LineString,
        MultiLineString,
        MultiPoint,
        MultiPolygon,
        Point,
        Polygon,
    )

    assert isinstance(mesh, Mesh)

    if mesh.geometry.name == "VSet":
        geometry = (
            MultiPoint(mesh.points) if len(mesh.points) > 1 else Point(mesh.points)
        )
    elif mesh.geometry.name == "PLine":
        nodes = [[mesh.points[i] for i in cell] for cell in mesh.cells]
        geometry = (
            MultiLineString([LineString(pts) for pts in nodes])
            if len(nodes) > 1
            else LineString(nodes[0])
        )
    elif mesh.geometry.name == "TSurf":
        points = np.asarray(mesh.points, dtype=float)
        cells = np.asarray(mesh.cells, dtype=int)
        nodes = points[
            cells
        ]  # 10x faster than list comprehesion `[[points[i] for i in cell] for cell in obj.cells]`
        geometry = (
            MultiPolygon([Polygon(pts) for pts in nodes])
            if len(nodes) > 1
            else Polygon(nodes[0])
        )
    else:  # FIXME: how to cast 'TSolid' to 2D format ?!
        msg = f"Ignoring unsupported GOCAD object: {mesh.geometry.name} ('{mesh.name}')"
        raise NotImplementedError(msg)
    return {mesh.geometry.name: geometry}


def _cast_well(well: Well) -> dict[Geometry]:  # noqa: F821
    from shapely.geometry import LineString, MultiLineString, MultiPoint, Point

    assert isinstance(well, Well)

    geometries = {}
    if well.collar:
        geometries["WellCollars"] = Point(well.collar)
    if well.path:
        geometries["WellPath"] = LineString(np.asarray(well.path)[:, :3])
    if well.markers:
        geometries["WellMarkers"] = MultiPoint(
            [well.coords(m.zm) for m in well.markers]
        )
    if well.zones:
        geometries["WellZones"] = MultiLineString(
            [
                [
                    (well.coords(z.zfrom), well.coords(z.zto)),
                ]
                for z in well.zones
            ]
        )

    return geometries


def _cast_grid(grid: Grid) -> dict[Geometry]:  # noqa: F821
    msg = f"Ignoring unsupported GOCAD object: {grid.geometry.name} ('{grid.name}')"
    raise NotImplementedError(msg)


def to_geopandas(obj):
    from geopandas import GeoDataFrame
    from pandas import concat

    if isinstance(obj, list):
        pieces = []
        for piece in obj:
            try:
                pieces.append(to_geopandas(piece))
            except NotImplementedError:
                msg = f"Ignoring unsupported GOCAD object: {piece.geometry.name} ('{piece.name}')"
                warn(
                    msg,
                    Warning,
                    stacklevel=2,
                )
        return concat(pieces) if pieces else GeoDataFrame()

    assert isinstance(obj, Object)

    # build GeoDataFrame
    if isinstance(obj, Chunk):
        obj = obj.decode()
    assert isinstance(obj, Object), f"Invalid object type: {type(obj)}"

    return build_df(obj)
