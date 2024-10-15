from os.path import basename, realpath, join
from re import search, match
from datetime import datetime, timedelta

from osgeo import gdal, gdalconst

gdal.DontUseExceptions()

def make_tif(src, dest, channel):
    """
    Create a tif from a NetCDF file and a channel and
    save it in dest

    Args:
        src: path of the NetCDF file
        dest: path of the output file
        channel: channel to save
    Returns:
        None
    """
    subdataset = gdal.Open(f'NETCDF:"{src}":{channel}')
    min, max = subdataset.GetRasterBand(1).ComputeRasterMinMax()
    translate_param = gdal.TranslateOptions(format="GTiff",
                                            outputType=gdalconst.GDT_Byte,
                                            scaleParams=[[min, max, 0, 255]],
                                            noData=None)
    gdal.Translate(dest, subdataset, options=translate_param)


def mtg_to_tif(src, dest_directory):
    """
    Create a tif from a mtg file and
    save it in dest_directory

    Args:
        src: path of the mtg file
        dest_directory: directory where to save output file
    Returns:
        List of path of the output files
    """
    produits_faits = []

    file = basename(realpath(src))

    # mtg : Multic1km_mtgi1_YYYYMMDD_hhmm.nc
    resolution, satellite, str_datetime = match("^([^_]+)_([^_]+)_(.+).nc$", file).groups()
    resolution = search(r"\dkm", resolution)[0] # we extract "1km" or "2km"
    
    # we can format the name of the output tif
    dest_file = f"{resolution}VIS006_{satellite}_{str_datetime}.tif"
    dest = join(dest_directory, dest_file)
    make_tif(src, dest, "VIS006")
    produits_faits.append(dest)

    if resolution == "2km":
        # if it's 2km, we add the IR105 channel
        dest_file = f"{resolution}IR105_{satellite}_{str_datetime}.tif"
        dest = join(dest_directory, dest_file)
        make_tif(src, dest, "IR_105")
        produits_faits.append(dest)
    
    return produits_faits


def msg_to_tif(src, dest_directory):
    """
    Create a tif from a msg file and
    save it in dest_directory

    Args:
        src: path of the msg file
        dest_directory: directory where to save output file
    Returns:
        List of path of the output files
    """
    produits_faits = []
    file = basename(realpath(src))

    # msg : Mmultic3kmNC4_msg03_YYYYMMDDhhmm.nc
    resolution, satellite, str_datetime = match("^([^_]+)_([^_]+)_(.+).nc$", file).groups()
    resolution = search(r"\dkm", resolution)[0] # we extract "3km"

    # msg pictures don't have the same naming convention
    # we have to put the coverage end time instead of coverage start time
    # and we know that msg takes 15 minutes
    format = "%Y%m%d%H%M"
    dt = datetime.strptime(str_datetime, format)
    dt += timedelta(minutes=15)
    str_datetime = dt.strftime(format)

    # we can format the name of the output tif
    dest_file = f"{resolution}VIS006_{satellite}_{str_datetime}.tif"
    dest = join(dest_directory, dest_file)
    make_tif(src, dest, "VIS006")
    produits_faits.append(dest)

    dest_file = f"{resolution}IR108_{satellite}_{str_datetime}.tif"
    dest = join(dest_directory, dest_file)
    make_tif(src, dest, "IR_108")
    produits_faits.append(dest)

    return produits_faits