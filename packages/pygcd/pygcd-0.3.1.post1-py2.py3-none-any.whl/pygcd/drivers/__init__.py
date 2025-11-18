from .geopandas_driver import to_geopandas
from .lasio_driver import to_lasio
from .pyvista_driver import to_pyvista

Drivers = {
    "vtk": to_pyvista,
    "pyvista": to_pyvista,
    "gdf": to_geopandas,
    "geopandas": to_geopandas,
    "las": to_lasio,
    "lasio": to_lasio,
}
