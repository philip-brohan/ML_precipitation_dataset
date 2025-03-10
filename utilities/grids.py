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


# Similar cube but for 20CRv3
# Exactly the same lat/lon grid as 20CR, but with longitudes shifted to have the UK in the middle
#  and latitudes running south to north
lon_values = np.arange(-180, 180, 0.703125)
lat_values = (
    [  # Copied from a file - there must be an algorithm, but I don't know what it is.
        -89.46282157,
        -88.76695135,
        -88.06697165,
        -87.36606343,
        -86.66480301,
        -85.96337216,
        -85.26184606,
        -84.56026138,
        -83.85863813,
        -83.15698813,
        -82.45531883,
        -81.75363514,
        -81.05194045,
        -80.35023715,
        -79.64852699,
        -78.94681128,
        -78.24509101,
        -77.54336694,
        -76.8416397,
        -76.13990975,
        -75.43817749,
        -74.73644324,
        -74.03470726,
        -73.33296977,
        -72.63123095,
        -71.92949096,
        -71.22774993,
        -70.52600796,
        -69.82426517,
        -69.12252163,
        -68.42077741,
        -67.71903259,
        -67.01728721,
        -66.31554132,
        -65.61379497,
        -64.9120482,
        -64.21030104,
        -63.50855352,
        -62.80680568,
        -62.10505753,
        -61.40330909,
        -60.7015604,
        -59.99981146,
        -59.2980623,
        -58.59631292,
        -57.89456335,
        -57.19281359,
        -56.49106366,
        -55.78931357,
        -55.08756333,
        -54.38581295,
        -53.68406242,
        -52.98231178,
        -52.28056101,
        -51.57881013,
        -50.87705915,
        -50.17530806,
        -49.47355688,
        -48.7718056,
        -48.07005424,
        -47.3683028,
        -46.66655129,
        -45.9647997,
        -45.26304804,
        -44.56129631,
        -43.85954452,
        -43.15779267,
        -42.45604076,
        -41.75428879,
        -41.05253678,
        -40.35078471,
        -39.6490326,
        -38.94728044,
        -38.24552823,
        -37.54377599,
        -36.8420237,
        -36.14027138,
        -35.43851902,
        -34.73676663,
        -34.0350142,
        -33.33326174,
        -32.63150925,
        -31.92975673,
        -31.22800418,
        -30.5262516,
        -29.824499,
        -29.12274637,
        -28.42099372,
        -27.71924105,
        -27.01748835,
        -26.31573564,
        -25.6139829,
        -24.91223014,
        -24.21047737,
        -23.50872458,
        -22.80697177,
        -22.10521894,
        -21.4034661,
        -20.70171325,
        -19.99996038,
        -19.2982075,
        -18.5964546,
        -17.89470169,
        -17.19294877,
        -16.49119584,
        -15.7894429,
        -15.08768995,
        -14.38593699,
        -13.68418402,
        -12.98243104,
        -12.28067806,
        -11.57892507,
        -10.87717206,
        -10.17541906,
        -9.47366605,
        -8.77191303,
        -8.07016,
        -7.36840698,
        -6.66665394,
        -5.96490091,
        -5.26314787,
        -4.56139482,
        -3.85964178,
        -3.15788873,
        -2.45613568,
        -1.75438263,
        -1.05262958,
        -0.35087653,
        0.35087653,
        1.05262958,
        1.75438263,
        2.45613568,
        3.15788873,
        3.85964178,
        4.56139482,
        5.26314787,
        5.96490091,
        6.66665394,
        7.36840698,
        8.07016,
        8.77191303,
        9.47366605,
        10.17541906,
        10.87717206,
        11.57892507,
        12.28067806,
        12.98243104,
        13.68418402,
        14.38593699,
        15.08768995,
        15.7894429,
        16.49119584,
        17.19294877,
        17.89470169,
        18.5964546,
        19.2982075,
        19.99996038,
        20.70171325,
        21.4034661,
        22.10521894,
        22.80697177,
        23.50872458,
        24.21047737,
        24.91223014,
        25.6139829,
        26.31573564,
        27.01748835,
        27.71924105,
        28.42099372,
        29.12274637,
        29.824499,
        30.5262516,
        31.22800418,
        31.92975673,
        32.63150925,
        33.33326174,
        34.0350142,
        34.73676663,
        35.43851902,
        36.14027138,
        36.8420237,
        37.54377599,
        38.24552823,
        38.94728044,
        39.6490326,
        40.35078471,
        41.05253678,
        41.75428879,
        42.45604076,
        43.15779267,
        43.85954452,
        44.56129631,
        45.26304804,
        45.9647997,
        46.66655129,
        47.3683028,
        48.07005424,
        48.7718056,
        49.47355688,
        50.17530806,
        50.87705915,
        51.57881013,
        52.28056101,
        52.98231178,
        53.68406242,
        54.38581295,
        55.08756333,
        55.78931357,
        56.49106366,
        57.19281359,
        57.89456335,
        58.59631292,
        59.2980623,
        59.99981146,
        60.7015604,
        61.40330909,
        62.10505753,
        62.80680568,
        63.50855352,
        64.21030104,
        64.9120482,
        65.61379497,
        66.31554132,
        67.01728721,
        67.71903259,
        68.42077741,
        69.12252163,
        69.82426517,
        70.52600796,
        71.22774993,
        71.92949096,
        72.63123095,
        73.33296977,
        74.03470726,
        74.73644324,
        75.43817749,
        76.13990975,
        76.8416397,
        77.54336694,
        78.24509101,
        78.94681128,
        79.64852699,
        80.35023715,
        81.05194045,
        81.75363514,
        82.45531883,
        83.15698813,
        83.85863813,
        84.56026138,
        85.26184606,
        85.96337216,
        86.66480301,
        87.36606343,
        88.06697165,
        88.76695135,
        89.46282157,
    ]
)

pole_latitude = 90
pole_longitude = 180
npg_longitude = 0
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
latitude = iris.coords.DimCoord(
    lat_values, standard_name="grid_latitude", units="degrees_north", coord_system=cs
)
latitude.guess_bounds()
longitude = iris.coords.DimCoord(
    lon_values, standard_name="grid_longitude", units="degrees_east", coord_system=cs
)
longitude.guess_bounds()
dummy_data = np.ma.MaskedArray(np.zeros((len(lat_values), len(lon_values))), False)
TWCRCube = iris.cube.Cube(
    dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]
)
TWCRCube_grid_areas = iris.analysis.cartography.area_weights(TWCRCube)
TWCRscs = cs
