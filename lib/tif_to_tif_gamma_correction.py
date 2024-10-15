from shutil import copy

from osgeo import gdal

def to_correction_gamma(src, dest, gamma):
    """
    Create an tif picture from a tif by applying a gamma correction
    and save it to dest

    Args:
        src: path of the input tif file
        dest: path of the output tif file
        gamma: gamma to apply
    Returns:
        None
    """

    copy(src, dest)    

    with gdal.Open(dest, gdal.GA_Update) as writer_gdal:
        im = writer_gdal.GetRasterBand(1).ReadAsArray()

        # gamma formula
        im = (im/255)**(1/gamma)*255

        writer_gdal.GetRasterBand(1).WriteArray(im)
