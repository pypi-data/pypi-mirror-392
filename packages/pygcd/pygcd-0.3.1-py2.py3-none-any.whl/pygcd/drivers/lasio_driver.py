from logging import warning
from typing import Union

from ..objects import Chunk, Layer, Object, Well


def _cast(well: Well):
    if isinstance(well, str):
        well = Chunk(well)
    if isinstance(well, Chunk):
        well = well.decode()
    if not isinstance(well, Well):
        msg = f"Wrong geometry type: {well.geometry.name}"
        raise NotImplementedError(msg)

    import pandas as pd
    from lasio import LASFile

    index = "DEPT"

    las = LASFile()

    for mnem in las.well:
        las.well[mnem] = well.fields.get(mnem.lower(), "")

    las.well.WELL = well.name
    las.well.SRVC = "GOCAD"
    las.well.LOC = " ".join(str(e) for e in well.collar)

    if len(well.curves) == 1:
        for curve in well.curves:
            las.append_curve(index, curve.zm, unit=curve.z_unit)
            las.append_curve(curve.name, curve.values, unit=curve.v_unit)
    elif len(well.curves) > 1:
        curves = pd.concat(
            [
                pd.DataFrame({index: curve.zm, curve.name: curve.to_numpy()}).set_index(
                    index
                )
                for curve in well.curves
            ]
        )
        las.set_data(curves)
        for el, w in zip(las.curves[1:], well.curves):
            el.unit = w.v_unit

    extras = []
    crs = well.fields.get("crs", {}).get("projection", None)
    if crs:
        extras.append(f"CRS: {crs}")
    if well.path:
        path = "\n\t".join(str(e) for e in well.path)
        path = path.replace("(", "").replace(")", "")
        extras.append(f"WELL PATH: (X Y Z)\n\t{path}")

    las.other = "\n".join(extras)

    return las


def to_lasio(obj: Union[Object, list]):
    if isinstance(obj, (str, Layer)):
        obj = [obj]

    files = []
    for piece in obj:
        try:
            files.append(_cast(piece))
        except NotImplementedError:
            msg = f"Ignoring unsupported GOCAD object: {piece.geometry.name} ('{piece.name}')"
            warning(msg)
    return files
