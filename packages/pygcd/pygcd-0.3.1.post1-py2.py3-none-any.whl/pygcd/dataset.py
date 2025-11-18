from __future__ import annotations

from copy import copy
from pathlib import Path
from typing import Any

from .drivers import Drivers
from .objects import Chunk, Geometry, Object, decode
from .readers import find_objects


class Dataset(list):
    """Container for GOCAD objects.

    Each GOCAD project file is composed of (multiple) object(s).
    All objects have a common structured header with general
    properties (i.e. name, geometry type, version, ...).
    These objects can be meshes, grids or wells ...
    their geometry needs to be decoded accordingly !

    A project file is read as follow:
    - `find`: split objects (block parsing based on "GOCAD ... END" regex)
    - `load`: identify object (parse headers, register {name, geometry, properties})
    - `read`: extract the geometry (decode meshes/grids/wells structure and data)

    Args:
        filename (str): The file to read.
            *! Only ASCII exports are currently supported !*
    """

    def __init__(self, obj=None, filename="") -> None:
        super().__init__()
        self.filename = filename
        if isinstance(obj, Dataset):
            self = copy(obj)  # noqa: PLW0642
        elif isinstance(obj, list):
            for e in filter(None, obj):
                self.append(copy(e))

    def __getitem__(self, key) -> Chunk | Object:
        if isinstance(key, str):
            return self[self.names.index(key)]
        return super().__getitem__(key)

    def __repr__(self) -> str:
        cout = f'"{self.filename}"\n↳ ' if self.filename else ""
        if self:
            cout += f"{len(self)} objects : " + "{\n"
            for obj in self:
                cout += f"  {obj}\n"
            cout += "}"
        else:
            cout += "[]"
        return cout

    def clear(self):
        super().clear()
        self.filename = ""

    def empty(self):
        super().clear()

    @property
    def names(self):
        return [el.name for el in self]

    @property
    def geometries(self):
        return [el.geometry for el in self]

    @property
    def properties(self):
        return [el.properties for el in self]

    def items(self):
        yield from zip(self.names, self)

    @property
    def objects(self):
        return [e for e in self if isinstance(e, Object)]

    def filter(self, *, indices=None, names=None, geometries=None):
        """Filter a specific geometry.

        Args:
            indices (Iterable[int]): The indices to select.
            names (Union[str, Iterable[str]]): The objects to select (list or regex).
            geometries (Union[Geometry, str, int]): The geometries to select.

        Returns:
            Dataset: A subset of the dataset mathcing filter criterions.
        """

        # geometries can be
        if geometries is None:
            geometries = []
        if names is None:
            names = []
        if indices is None:
            indices = []
        geometries = [
            Geometry[g] if isinstance(g, str) else Geometry(g) for g in geometries
        ]

        valids = []
        for i, el in enumerate(self):
            if (indices and i not in indices) or (names and el.name not in names):
                continue
            if geometries and el.geometry not in geometries:
                continue
            valids.append(el)

        return self.__class__(valids, self.filename)

    def to(self, wrapper: str) -> Any:
        if wrapper.lower() not in Drivers:
            msg = f"Unsupported format: {wrapper}"
            raise ValueError(msg)
        driver = Drivers[wrapper.lower()]
        return driver(self)

    @classmethod
    def find(cls, filename) -> list[str]:
        """Open an ascii file and split objects in it.

        Args:
            filename (str): Ascii GOCAD export file.

        Returns:
            list[str]: List of single GOCAD objects text blocks.
        """
        # TODO: handle binary/projects files
        path = Path(filename)
        return find_objects(path.read_bytes().decode("ascii", "replace"))

    @classmethod
    def load(cls, filename: str, **kwargs) -> list[Chunk]:
        """Open an ascii file and identify objects in it.

        Args:
            filename (str): Ascii GOCAD export file.
            **kwargs: Reading options for `pathlib.Path.read_text()`.

        Returns:
            Dataset[Chunk]: Collection of identified GOCAD objects.
        """

        blocks = cls.find(filename, **kwargs)
        n = len(blocks)
        if n == 0:
            return cls()

        blocks = [Chunk(b) for b in blocks]

        return cls(blocks, filename=filename)

    @classmethod
    def read(
        cls,
        filename: str,
        *,
        wrapper: str | None = None,
        index=None,
        indices=None,
        names=None,
        geometries=None,
    ) -> list[Object] | Object:
        """Open an ascii file and read objects in it.

        Args:
            filename (str): Ascii GOCAD export file.
            wrapper (str): The format to wrap the returned Dataset. Must be in `pygcd.getWrappers()`.
            index (Union[int, str]): Index of the object to return.
        Kwargs:
            indices (Iterable[int]): The indices to select.
            names (Union[str, Iterable[str]]): The objects to select (list or regex).
            geometries (Union[Geometry, str, int]): The geometries to select.

            geometries (Geometry): Filter objects to return based on the geometry.
            **kwargs: Reading options for `pathlib.Path.read_text()`.

        Returns:
            Dataset[Object]: Collection of parsed GOCAD objects.
        """

        if geometries is None:
            geometries = []
        if names is None:
            names = []
        if indices is None:
            indices = []
        kwargs = {"filename": filename}

        # identify ascii chunks
        ds = cls.load(**kwargs)

        # filter identified objects (avoid extensive parsing)
        if len(indices + names + geometries):
            filters = {"indices": indices, "names": names, "geometries": geometries}
            ds = ds.filter(**filters)

        # filter on index
        if index is not None:
            return decode(ds[index], **kwargs)

        ds = cls([decode(e, **kwargs) for e in ds], **kwargs)

        if wrapper:
            return ds.to(wrapper)
        return ds
