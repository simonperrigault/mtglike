from os import remove

from xarray import open_dataset
import numpy as np


def clear_dataset(src):
    """
    Put all the data of all the variables of a netcdf to NaN

    Args:
        src: file to handle
    Returns:
        None
    """
    # we don't touch to these variables because they don't change between 2 NetCDF
    white_list = {"time", "dtime", "commentaires", "satellite", "geos", "ImageNavigation", "ImageNavigation1km",
                  "ImageNavigation2km", "ImageNavigation4km", "GeosCoordinateSystem", "GeosCoordinateSystem1km",
                  "GeosCoordinateSystem2km", "GeosCoordinateSystem4km",
                  "Y", "Y1km", "Y2km", "Y4km", "X", "X1km", "X2km", "X4km"}
    
    writer = open_dataset(src, decode_cf=False, decode_times=False)

    for key in writer.data_vars.keys():
        if key in white_list: continue
        print(f"Efface {key}...")
        writer.data_vars[key].data = np.full(writer.variables[key].shape, np.nan)
    print("Ecriture...")
    remove(src)
    writer.to_netcdf(src, "w")