from pathlib import Path

import numpy as np


def read_grid(raw: str, *args, **kwargs):  # noqa: ARG001
    # Directory containing the grid file definition and the associated property files
    root_dir = Path(kwargs["filename"]).parent
    lines = raw.splitlines()
    if lines[-1] == "END":
        lines.pop()
    # Skip header, focus on geometry and properties
    idx = lines.index("}")
    # header = lines[:idx]
    lines = lines[idx + 1 :]
    idx = next(i for i, line in enumerate(lines) if line == "")
    geometry = _read_geometry(lines[:idx])
    dimensions = geometry[1]
    assert lines[idx + 1].startswith("PROPERTY ")
    lines = lines[idx + 1 :]
    properties = []
    while lines:
        assert lines[0].startswith("PROPERTY ")
        idx = next(
            (i for i, line in enumerate(lines[1:], start=1) if line == ""), len(lines)
        )
        properties.append(lines[:idx])
        lines = lines[idx + 1 :]
    properties = [_read_property(root_dir, p, dimensions) for p in properties]
    return geometry, properties


def _read_geometry(block: list[str]):
    def as_array(stuff):
        return np.array([float(v) for v in stuff])

    def as_tuple(stuff):
        return tuple(float(v) for v in stuff)

    for line in block:
        what, *stuff = line.split()
        if what == "AXIS_N":
            # len(stuff) can be 2 (GSurf) or 3 (Voxet)
            dimensions = tuple(int(v) for v in stuff)
            nu, nv = dimensions[:2]
            nw = 1 if len(dimensions) == 2 else dimensions[2]
        if what in ("ORIGIN", "AXIS_0"):
            origin = as_array(stuff)
        elif what == "AXIS_U":
            u = as_array(stuff)
        elif what == "AXIS_V":
            v = as_array(stuff)
        elif what == "AXIS_W":
            w = as_array(stuff)
        elif what == "AXIS_MIN":
            p0 = as_array(stuff)
        elif what == "AXIS_MAX":
            p1 = as_array(stuff)
        elif what == "TYPE" and stuff != "POINTS":
            pass  # FIXME Handle corner-point grid case

    # Compute true origin in (x,y,z)
    umin, vmin, wmin = p0
    origin = as_tuple(origin + umin * u + vmin * v + wmin * w)
    # Rescale (u,v,w) axes to exactly match the grid axes
    du, dv, dw = p1 - p0
    u *= du
    v *= dv
    w *= dw
    axes = np.array([u / nu, v / nv, w / nw])
    spacing = np.linalg.norm(axes, axis=0)
    axes /= spacing
    spacing = as_tuple(spacing)
    axes = tuple(as_tuple(ax) for ax in axes)
    return origin, dimensions, spacing, axes


def _read_property(root_dir: Path, block: list[str], dimensions):
    # Note: while we do not have counter-examples, we consider that grid properties
    # are systematically floating-point values, stored in an external file
    for line in block:
        what, *stuff = line.split()
        if what == "PROPERTY":
            name = stuff[-1]
        if what == "PROP_NO_DATA_VALUE":
            ndv = float(stuff[-1])
        if what == "PROP_OFFSET":
            offset = int(stuff[-1])
        if what == "PROP_FILE":
            file = stuff[-1]
    file = root_dir / file
    data = np.fromfile(file, ">f4", count=np.prod(dimensions), offset=offset).reshape(
        dimensions[::-1]  # Native GOCAD order: nw * nv * nu
    )
    data[data == ndv] = np.nan
    return name, data
