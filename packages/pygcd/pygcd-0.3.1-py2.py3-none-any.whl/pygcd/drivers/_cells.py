from itertools import chain


def ravel_cells(nested_cells: list[list]) -> list:
    """Converts nested lists of indices into a flat list of connectivities.

    e.g. [[0,1,2],[0,2,3]]  -> [3,0,1,2,3,0,2,3]
    """
    flat_connectivity = chain.from_iterable([(len(c), *c) for c in nested_cells])
    return list(flat_connectivity)


def unravel_cells(flat_cells: list) -> list[list]:
    """Converts a flat list of connectivities into nested lists of indices.

    e.g. [3,0,1,2,3,0,2,3] -> [[0,1,2],[0,2,3]]
    """
    nested_cells = []
    i, stop = 0, len(flat_cells)
    while i < stop:
        n = flat_cells[i]
        i += 1
        nested_cells.append([flat_cells[i : i + n]])
        i += n
    return nested_cells


def nested_to_offconn(cells: list[list]) -> tuple[list, list]:
    """Ravel cells with new-school VTK cells format.

    e.g. [[0,1,2],[0,2,3]] -> [0,1,2,0,2,3], [0,4]
    """
    connectivity, offsets = [], [0]
    for cell in cells:
        connectivity.extend(cell)
        offsets.append(len(cell))
    return offsets, connectivity


def offconn_to_nested(offsets: list, connectivity: list) -> list[list]:
    off, conn = offsets, connectivity
    return [conn[i : i + 1] for i in off[:-1]]
