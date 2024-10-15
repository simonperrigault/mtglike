from PIL import Image, ImageDraw, ImageFont
from re import search
from os.path import basename, join
from shutil import copy

from osgeo import gdal
import numpy as np

def text_to_grayscale_array(text, font_size=100):
    """
    Convert a text string to an numpy array drawing the text

    Args:
        text: text to convert
        font_size: font size in pixels
    Returns:
        Numpy array
    """
    font = ImageFont.load_default(font_size)
    bbox = font.getbbox(text)
    # bbox = border box = size of the rectangle taken by the text with this font
    # so we can extract width and height to create the picture
    width, height = bbox[2]-bbox[0], bbox[3]-bbox[1]

    image = Image.new('L', (width, height*5//4), color=255)  # 'L' mode for grayscale
    draw = ImageDraw.Draw(image)
    draw.text((0,0), text, font=font, fill=0)  # fill=0 for black text

    return np.array(image)

def extract_metadata(src):
    """
    Extract the metadata from a tif input file and
    store them in a list.
    Give history, time_coverage_duration, time_coverage_start, time_coverage_end and date_created

    Args:
        src: path of the msg file
    Returns:
        List of content of metadata
    """
    reader_gdal = gdal.Open(src)
    metadata = gdal.Info(reader_gdal)
    res = []
    to_search = ["history", "time_coverage_duration", "time_coverage_start", "time_coverage_end", "date_created"]

    # metadata are written : history=example of history
    # so we can do a regex to find each
    for str in to_search:
        res.append(search(f"{str}=.+", metadata)[0])
    return res

def to_texted_tif(src, dest_directory):
    """
    Print some metadata of a tif file on itself and save it
    in dest_directory

    Args:
        src: path of the tif file
        dest_directory: directory where to save output file
    Returns:
        None
    """
    produits_faits = []
    reader_file = basename(src)
    metadata = extract_metadata(src)

    dest = join(dest_directory, f"texted_{reader_file}")
    copy(src, dest)

    font_size = 50 # font size for a 3km resolution
    if src.find("2km") != -1:
        font_size = font_size*3 // 2
    elif src.find("1km") != -1:
        font_size = font_size*3
    
    offset_x = 0 # we begin to write in the up left corner
    offset_y = 50

    with gdal.Open(dest, gdal.GA_Update) as writer_gdal:
        image = writer_gdal.GetRasterBand(1).ReadAsArray()

        for line in metadata:
            text_array = text_to_grayscale_array(line, font_size)
            image[offset_y:offset_y+text_array.shape[0], offset_x:offset_x+text_array.shape[1]] = text_array
            offset_y += font_size*3 // 2 # 3/2 is a good factor for the offset, found empirically

        writer_gdal.GetRasterBand(1).WriteArray(image)
    
    produits_faits.append(dest)
    
    return produits_faits
