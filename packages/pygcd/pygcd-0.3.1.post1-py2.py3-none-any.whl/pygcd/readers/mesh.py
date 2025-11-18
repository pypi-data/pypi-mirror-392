POINTS = ("VRTX", "PVRTX", "ATOM", "PATOM")
FIELDS = (
    "PROPERTIES",
    "FIELDS",
    "NO_DATA_VALUES",
    "ESIZES",
)  # ignore "UNITS" since it wont be forwarded
CELLS = ("SEG", "TRGL", "TETRA")
SEP = ("ILINE", "TFACE", "TVOLUME")


def read_mesh(block: str, *args, **kwargs):  # noqa: ARG001
    nbp, nbc = 0, 0
    points, cells = [], []
    names, ndims, no_data_values, units = [], [], [], []
    point_props, cell_splits = [], []
    for line in block.splitlines():
        line = line.strip()  # noqa: PLW2901
        if not line:
            continue
        what, *stuff = line.split()
        if what in FIELDS:
            if what in ("PROPERTIES", "FIELDS"):
                assert not names, "Duplicated point properties definition"
                names = stuff
            elif what == "NO_DATA_VALUES":
                assert not no_data_values, "Duplicated point data default values"
                no_data_values = [float(x) for x in stuff]
                if ndims:
                    no_data_values = [
                        x if y == 1 else [x] * y for x, y in zip(no_data_values, ndims)
                    ]
            elif what == "UNITS":
                assert not units, "Duplicated point data units"
                units = stuff
            elif what == "ESIZES":
                assert not ndims, "Duplicated point data dimensions"
                ndims = (int(x) for x in stuff)
                if no_data_values:
                    no_data_values = [
                        x if y == 1 else [x] * y for x, y in zip(no_data_values, ndims)
                    ]
        elif what in POINTS:
            nbp += 1
            i, *stuff = stuff
            assert int(i) == nbp, "Wrong indexing in points indices"
            if what.endswith("VRTX"):
                x, y, z, *props = stuff
                points.append((float(x), float(y), float(z)))
            else:
                assert what.endswith("ATOM"), "Wrong point identifier"
                idx, *props = stuff
                points.append(points[int(idx) - 1])
            if props or len(no_data_values) > 0:
                point_props.append(props or no_data_values)
        elif what in CELLS:
            indices = [int(i) - 1 for i in stuff]
            if what == "SEG":  # merge zones to build lines
                if not cells:  # fist segment of first line
                    cells.append(indices)
                    nbc += 1
                elif not cells[-1]:  # new line detected
                    cells[-1] = indices
                    nbc += 1
                else:  # next zones extend last cell
                    assert cells[-1][-1] == indices[0], "Inconsistent PLine !"
                    cells[-1] += indices[1:]
            else:
                cells.append(indices)
                nbc += 1

        elif what in SEP:
            cell_splits.append(nbc)
            if what == "ILINE":  # new line forces a new cell
                cells.append([])
        else:
            continue

    if cells and not cells[-1]:  # clean up possibly empty last cell (only with PLine)
        cells = cells[:-1]

    assert nbp == len(points), "Number of points missmatch counter"
    assert nbc == len(cells), "Number of cells missmatch counter"

    cell_data = {}
    if cell_splits:  # create a cell_data attribute with part index
        cell_splits = cell_splits[::-1]
        parts, rank, idx = [], 0, cell_splits.pop()
        for i in range(nbc):
            if i == idx and cell_splits:
                idx = cell_splits.pop()
                rank += 1
            parts.append(rank)
        cell_data = {"block_id": parts}

    point_data = {}
    if point_props:
        for key, values in zip(names, zip(*point_props)):
            point_data[key] = values

    return points, cells, point_data, cell_data
