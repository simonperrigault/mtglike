from scipy.ndimage import map_coordinates
import numpy as np
from tqdm import trange

def can_move(cloudtype_indice):
    # 1:  Cloud-free land
    # 2:  Cloud-free sea
    # 3:  Snow over land
    # 4:  Sea ice
    # 5:  Very low clouds
    # 6:  Low clouds
    # 7:  Mid-level clouds
    # 8:  High opaque clouds
    # 9:  Very high opaque clouds
    # 10:  Fractional clouds
    # 11:  High semitransparent thin clouds
    # 12:  High semitransparent moderately thick clouds
    # 13:  High semitransparent thick clouds
    # 14:  High semitransparent above low or medium clouds
    # 15:  High semitransparent above snow/ice
    # return True
    can_move_set = {5, 6, 7, 8, 9}
    return cloudtype_indice in can_move_set

def apply_vector_field(input_image, vector_field, cloudtype):
    """
    Extrapolate an image after input_image thanks to
    the vector field

    Args:
        input_image: ndarray
        vector_field: ndarray[2,input_image.shape]
        cloudtype: ndarray[input_image.shape]
    Returns:
        output: ndarray
    """
    height, width = len(input_image), len(input_image[0])
    prev_row, prev_col = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
    prev_row = prev_row.astype(np.float64)
    prev_col = prev_col.astype(np.float64)
    for row in trange(height):
        for col in range(width):
            dr, dc = vector_field[0,row,col], vector_field[1,row,col]

            # # change cartesian into matrix
            # dr = -dy
            # dc = dx

            newr, newc = row+dr, col+dc
            newr = int(newr - 0.5)
            newc = int(newc - 0.5)

            if not (0 <= newr < height-1 and 0 <= newc < width-1):
                continue

            for ir in (newr, newr+1):
                for ic in (newc, newc+1):
                    if can_move(cloudtype[ir, ic]) or can_move(cloudtype[row, col]):
                        prev_row[ir, ic] = ir-dr
                        prev_col[ir, ic] = ic-dc

    output = map_coordinates(input_image, (prev_row, prev_col))
    return output