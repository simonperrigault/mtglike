from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np


def pictures_differences(path_file1, path_file2, seuil=50, gamma=1.23):
    """
    Compare 2 pictures. Give the percentage of pixels that exceed the
    threshold and show a 2D graph of the differences.
    Apply a gamma correction on the file2

    Args:
        path_file1: path of the first file
        path_file2: path of the second file
        seuil: threshold, in percentage
        gamma: gamma to apply on file2
    Returns:
        None
    """
    with gdal.Open(path_file1) as reader1:
        with gdal.Open(path_file2) as reader2:
            array1 = reader1.GetRasterBand(1).ReadAsArray()
            array2 = reader2.GetRasterBand(1).ReadAsArray()
            if array1.shape != array2.shape:
                print("The 2 images don't have the same size")
                exit(1)
            
            # gamma formula
            array2 = (array2/255)**(1/gamma)*255

            # to show the new picture :
            # plt.imshow(array2, cmap="gray")
            # plt.show()

            res = (array1 - array2)**2

            # we count the pixels above the threshold
            pourcentage = (res > seuil).sum()
            pourcentage = (pourcentage*100) // res.size
            print(f"Pourcentage de pixels différents au delà du seuil : {pourcentage}%")
            
            plt.imshow(res, cmap="plasma", vmin=0, vmax=2*np.mean(res))
            plt.show()


    