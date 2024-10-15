import numpy as np
from tqdm import tqdm
from multiprocessing import Pool

# vitesse max 400 km/h = 100 km/15 min
DEPLACEMENT_MAX = 100

def intercorrelation(img1, img2):
    s = np.square(img1 - img2)
    res = np.sum(np.where(np.isnan(s), 0, s))
    return res / np.sum(np.where(np.isnan(s), 0, 1))

def calcul_meilleur_vecteur(rowcol):
    tile_row, tile_col = rowcol[0]*step, rowcol[1]*step
    height, width = len(img_now), len(img_now[0])

    vmax = height * DEPLACEMENT_MAX // 11136 # deplacement max en pixels entre 2 images
    vmax = min(vmax, tile_size//2)

    if intercorrelation(img_now[tile_row:tile_row+tile_size, tile_col:tile_col+tile_size],
                        img_prev[tile_row:tile_row+tile_size, tile_col:tile_col+tile_size]) == 0:
        return rowcol[0], rowcol[1],0,0

    meilleure_correlation = float('inf')
    meilleur_dr = meilleur_dc = 0

    # de 4 en 4 d'abord
    for dr in range(-vmax, vmax+1, 4):
        for dc in range(-vmax, vmax+1, 4):
            to_add_left = to_add_right = 0
            to_add_up = to_add_down = 0

            left = tile_col+dc
            if left < 0:
                to_add_left = -left
                left = 0
            right = tile_col+tile_size+dc
            if right > width:
                to_add_right = right-width
                right = width
            up = tile_row+dr
            if up < 0:
                to_add_up = -up
                up = 0
            down = tile_row+tile_size+dr
            if down > height:
                to_add_down = down-height
                down = height


            translated_img = img_now[up:down, left:right]
            translated_img = np.pad(translated_img,
                                    ((to_add_up, to_add_down), (to_add_left, to_add_right)),
                                    constant_values=np.nan)

            intercorr = intercorrelation(translated_img,
                                         img_prev[tile_row:tile_row+tile_size, tile_col:tile_col+tile_size])
            if intercorr < meilleure_correlation:
                meilleure_correlation = intercorr
                meilleur_dr = dr
                meilleur_dc = dc
    
    # recherche fine de 1 en 1
    for dr in range(max(-vmax, meilleur_dr-3), min(vmax+1, meilleur_dr+4)):
        for dc in range(max(-vmax, meilleur_dc-3), min(vmax+1, meilleur_dc+4)):
            to_add_left = to_add_right = 0
            to_add_up = to_add_down = 0

            left = tile_col+dc
            if left < 0:
                to_add_left = -left
                left = 0
            right = tile_col+tile_size+dc
            if right > width:
                to_add_right = right-width
                right = width
            up = tile_row+dr
            if up < 0:
                to_add_up = -up
                up = 0
            down = tile_row+tile_size+dr
            if down > height:
                to_add_down = down-height
                down = height


            translated_img = img_now[up:down, left:right]
            translated_img = np.pad(translated_img,
                                    ((to_add_up, to_add_down), (to_add_left, to_add_right)),
                                    constant_values=np.nan)

            intercorr = intercorrelation(translated_img, 
                                         img_prev[tile_row:tile_row+tile_size, tile_col:tile_col+tile_size])
            
            if intercorr < meilleure_correlation:
                meilleure_correlation = intercorr
                meilleur_dr = dr
                meilleur_dc = dc

    return rowcol[0], rowcol[1], meilleur_dr, meilleur_dc

            
def vector_field_intercorrelation(p_img_now, p_img_prev, p_tile_size=32, p_step=8, p_up=0, down=1000, p_left=1150, right=2650):
    global img_prev, img_now
    global tile_size, step
    global up, left

    img_prev = p_img_prev.copy()
    img_now = p_img_now.copy()
    up = p_up
    left = p_left
    step = p_step
    tile_size = p_tile_size

    height, width = len(img_now), len(img_now[0])
    vector_height, vector_width = (height-tile_size) // step + 1, (width-tile_size) // step + 1



    i_vectors_calculated, j_vectors_calculated = np.meshgrid(np.arange(up//step, (down-tile_size)//step+1),
                                                             np.arange(left//step, (right-tile_size)//step+1),
                                                             indexing="ij")
    argument = np.column_stack((i_vectors_calculated.ravel(),
                                j_vectors_calculated.ravel()))
    
    vector_field = np.zeros((2, vector_height, vector_width))

    chunksize = 50 # argument.size // (cpu_count()*2) # ou 1000
    
    with Pool() as pool:
        res_tuples = np.array(list(tqdm(pool.imap(calcul_meilleur_vecteur,
                                                  argument, chunksize), total=len(argument))))
    rows = res_tuples[:, 0].astype(np.uint32)
    cols = res_tuples[:, 1].astype(np.uint32)

    vector_field[0, rows, cols] = res_tuples[:, 2]
    vector_field[1, rows, cols] = res_tuples[:, 3]
    
    return vector_field