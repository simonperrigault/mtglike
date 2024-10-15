import scipy.ndimage as spim
import numpy as np
import matplotlib.pyplot as plt
from lib.vector_field_intercorrelation import vector_field_intercorrelation, calcul_meilleur_vecteur
from lib.apply_vector_field import apply_vector_field
from lib.apply_vector_field_forward import apply_vector_field_forward
from PIL import Image
from math import atan, cos, sin, pi, exp
from tqdm import trange

size = 500
tile_size = 64
step = 32

img_now = np.zeros((size, size))
img_prev = plt.imread("data_verification/msg_initial/tif/3kmVIS006_msg03_202401011145.tif")
cloud_type = plt.imread("data_verification/msg_initial/cloudtype_tif/cloudtype_msg03_202401011200.tif")

img_now = img_prev[1500:2000, 1500:2000]

# for r in range(size):
#     for c in range(size):
#         # radius = (r-50)**2 + (c-50)**2
#         # img_now[r,c] = 255*exp(-(radius/1000)**2)
#         # if int(radius) % 50 < 10:
#         #     img_now[r,c] = 0
#         if ((r+c) % 2) == 0: img_now[r,c] = 255

print("calcul champ d'advection...")

center = size // 2
norme = 20
vector_field = np.zeros((2, size, size))

# vector_field = np.load(f"champ_radial_1856_1.npy")

def expo_norme(norme, r, c):
    x = (r-center)**2 + (c-center)**2
    return norme*exp(- (x / 30000)**2)

for row in trange(size):
    for col in range(size):
        if row == center:
            dr = 0
            dc = expo_norme(norme, row, col) * np.sign(col - center)
        else:
            alpha = atan((col - center) / (row - center))
            if row-center < 0:
                if col-center < 0:
                    alpha -= pi
                else:
                    alpha += pi
            dr = expo_norme(norme, row, col) * cos(alpha)
            dc = expo_norme(norme, row, col) * sin(alpha)
        vector_field[0, row, col] = dr
        vector_field[1, row, col] = dc
np.save("champ_radial_50_5_expo.npy", vector_field)

# vector_field = np.full((2, size, size), 20)

print("application du champ d'advection...")
output, next_row, next_col = apply_vector_field_forward(img_now, vector_field, 150, 350, 150, 350)

plt.figure()
plt.imshow(img_now, cmap="gray")

plt.figure()
plt.imshow(output, cmap="gray")

plt.figure()
plt.imshow(output, cmap="gray")
plt.plot(*np.meshgrid(np.arange(size+1)-0.5, np.arange(size+1)-0.5, indexing="ij"), "ob")
plt.plot(next_row.reshape(((size+1)**2))-0.5, next_col.reshape(((size+1)**2))-0.5, "or")

# Image.fromarray(output).save(f"3kmVIS006_msg03_202401011215_forward_{tile_size}_{step}.tif")

plt.show()