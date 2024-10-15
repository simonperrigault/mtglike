import numpy as np
from tqdm import tqdm
from shapely import Polygon, area, intersection, is_valid
from math import ceil
from time import perf_counter
from multiprocessing import Pool

def calculate_moved_tile(row, col):
    """
    Return the moved tile according to the vector field in
    next_row and next_col

    Args:
        row: int
        col: int
    Return:
        moved_tile: Polygon
    """
    return Polygon(((next_row[row,col], next_col[row,col]),
                (next_row[row,col+1], next_col[row,col+1]),
                (next_row[row+1,col+1], next_col[row+1,col+1]),
                (next_row[row+1,col], next_col[row+1,col])))

def calculate_coverage_moved_tile(args):
    """
    Compute the area of the intersection of a moved tile and the
    pixels it covers.

    Args:
        args: tuple (row, col)
    Return:
        list of intensities applied by the moved_tile[args] on a pixel: List[List[int, int, float]] (pixel_row, pixel_col, intensity)
    """
    row, col = args
    moved_tile = calculate_moved_tile(row, col)
    res = []
    if is_valid(moved_tile):
        bbox = moved_tile.bounds
        for interrow in range(int(bbox[0]), ceil(bbox[2])):
            for intercol in range(int(bbox[1]), ceil(bbox[3])):
                pixel = Polygon(((interrow, intercol),
                                 (interrow, intercol+1),
                                 (interrow+1, intercol+1),
                                 (interrow+1, intercol)))
                inter = intersection(pixel, moved_tile)
                coverage = area(inter)
                res.append((interrow, intercol, coverage*input[row,col]))
    return res

def compute_next_pos(args):
    """
    Return the next row and col of args=(row,col) according
    to the next_row and next_col matrix

    Args:
        args: tuple (row, col)
    Return:
        (row,col,next_row,next_col): tuple
    """
    row, col = args
    dr,dc = vector_field[:,row,col]

    next_r = np.clip(row+dr, up, down, dtype=np.float64)
    next_c = np.clip(col+dc, left, right, dtype=np.float64)

    return row, col, next_r, next_c

def apply_vector_field_forward(p_input, p_vector_field, p_up, p_down, p_left, p_right):
    """
    Extrapolate an image after input thanks to
    the vector field, only in the area [up:down, left:right]

    Args:
        input: ndarray
        vector_field: ndarray[2,input.shape]
        up: int
        down: int
        left: int
        right: int
    Returns:
        output: ndarray
    """
    global left,right,up,down 
    global width,height
    global input
    global next_row,next_col
    global vector_field

    vector_field = p_vector_field.copy()

    height, width = len(p_input), len(p_input[0]) 

    up = np.clip(p_up, 0, height)
    down = np.clip(p_down, 0, height)
    left = np.clip(p_left, 0, width)
    right = np.clip(p_right, 0, width)

    # +1 car on prend les bords des pixels donc ça rajoute un
    next_row, next_col = np.meshgrid(np.arange(height+1, dtype=np.float64),
                                     np.arange(width+1, dtype=np.float64),
                                     indexing="ij")

    print("début de l'application du champ de vecteurs...")
    input = p_input.copy()
    output = p_input.copy()
    output[up:down, left:right] = np.zeros((down-up, right-left))

    print("création des coordonnées...")
    temp = perf_counter()
    row_coords, col_coords = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
    print(f"=> {perf_counter() - temp} s")

    argument = np.column_stack((row_coords[up+1:down-1, left+1:right-1].ravel(),
                                col_coords[up+1:down-1, left+1:right-1].ravel()))
        
    chunksize = 1000 # argument.size // (cpu_count()*2) # ou 1000
    
    with Pool() as pool:
        print("calcul des nouvelles positions...")
        temp = perf_counter()
        res_tuples = np.array(list(tqdm(pool.imap(compute_next_pos,
                                                  argument, chunksize), total=len(argument))))
    rows = res_tuples[:, 0].astype(np.uint32)
    cols = res_tuples[:, 1].astype(np.uint32)

    next_row[rows, cols] = res_tuples[:, 2]
    next_col[rows, cols] = res_tuples[:, 3]
    print(f"=> {perf_counter() - temp} s")

    with Pool() as pool:
        print("calcul des intersections...")
        temp = perf_counter()
        res_tuples = [t for t in tqdm(pool.imap(calculate_coverage_moved_tile,
                                                argument, chunksize), total=len(argument)) if t]
        all_results = np.concatenate(res_tuples)
        print(f"=> {perf_counter() - temp} s")

    print("application des intersections...")
    temp = perf_counter()
    rows = all_results[:, 0].astype(np.uint32)
    cols = all_results[:, 1].astype(np.uint32)
    terms = all_results[:, 2].astype(np.uint8)
    np.add.at(output, (rows, cols), terms)
    print(f"=> {perf_counter() - temp} s")

    return output