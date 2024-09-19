# Define common grids
# Models are grid specific, so it's easier to regrid early on
#  and do everything on the common grid

import numpy as np

import iris
import iris.cube
import iris.util
import iris.analysis
import iris.analysis.cartography
import iris.coord_systems

import warnings

# I'm not that fussed about precise planetary geometry
warnings.filterwarnings("ignore", "Using DEFAULT_SPHERICAL_EARTH_RADIUS.")

# Define a standard-cube to work with
# Identical to that used in ERA5, except that the longitude cut is moved
#  to mid pacific (-180) instead of over the UK (0)
resolution = 0.25
xmin = -180
xmax = 180
ymin = -90
ymax = 90
pole_latitude = 90
pole_longitude = 180
npg_longitude = 0
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
lat_values = np.arange(ymin, ymax + resolution, resolution)
latitude = iris.coords.DimCoord(
    lat_values, standard_name="grid_latitude", units="degrees_north", coord_system=cs
)
latitude.guess_bounds()
lon_values = np.arange(xmin, xmax, resolution)
longitude = iris.coords.DimCoord(
    lon_values, standard_name="grid_longitude", units="degrees_east", coord_system=cs
)
longitude.guess_bounds()
dummy_data = np.ma.MaskedArray(np.zeros((len(lat_values), len(lon_values))), False)

E5sCube = iris.cube.Cube(
    dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]
)
E5sCube_grid_areas = iris.analysis.cartography.area_weights(E5sCube)
E5sCube_latitude_areas = np.mean(E5sCube_grid_areas, axis=1)
E5scs = cs

# Similar cube but for HadCRUT5
resolution = 5.0
xmin = -177.5
xmax = 180
ymin = -87.5
ymax = 90
pole_latitude = 90
pole_longitude = 180
npg_longitude = 0
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
lat_values = np.arange(ymin, ymax, resolution)
latitude = iris.coords.DimCoord(
    lat_values, standard_name="grid_latitude", units="degrees_north", coord_system=cs
)
latitude.guess_bounds()
lon_values = np.arange(xmin, xmax, resolution)
longitude = iris.coords.DimCoord(
    lon_values, standard_name="grid_longitude", units="degrees_east", coord_system=cs
)
longitude.guess_bounds()
dummy_data = np.ma.MaskedArray(np.zeros((len(lat_values), len(lon_values))), False)
HadCRUTCube = iris.cube.Cube(
    dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]
)
HadCRUTCube_grid_areas = iris.analysis.cartography.area_weights(HadCRUTCube)
HadCRUTscs = cs
