import numpy as np
import matplotlib.pyplot as plt
from lib.apply_vector_field_forward import apply_vector_field_forward
from lib.vector_field_intercorrelation import vector_field_intercorrelation
from PIL import Image
import scipy.ndimage as spim

img_now = plt.imread("data_verification/msg_initial/tif/3kmVIS006_msg03_202401011200.tif")
img_prev = plt.imread("data_verification/msg_initial/tif/3kmVIS006_msg03_202401011145.tif")

size = 3712
tile_size = 128
step = 16

print("calcul champ d'advection...")
vector_field_center = vector_field_intercorrelation(img_now, img_prev, tile_size, step, 0, size, 0, size)

# np.save(f"ignore/array_{tile_size}_{step}_europe.npy", vector_field_center)

# vector_field_center = np.load(f"ignore/champ_radial_1856_20_expo.npy")

print("zoom...")
vector_field_center_zoomed = np.zeros((2,vector_field_center.shape[1]*step, vector_field_center.shape[2]*step))
vector_field_center_zoomed[0] = spim.zoom(vector_field_center[0], step)
vector_field_center_zoomed[1] = spim.zoom(vector_field_center[1], step)

_, width_center, height_center = vector_field_center_zoomed.shape

to_add = (size - width_center) // 2
vector_field = np.zeros((2, size, size))
vector_field[0] = np.pad(vector_field_center_zoomed[0], ((to_add,), (to_add,)))
vector_field[1] = np.pad(vector_field_center_zoomed[1], ((to_add,), (to_add,)))

# center = 1856
# norme = 20
# vector_field = np.zeros((2, size, size))

# vector_field = np.load(f"ignore/champ_radial_1856_20_expo.npy")

# def expo_norme(norme, r, c):
#     x = (r-center)**2 + (c-center)**2
#     return norme*exp(- (x / 1_000_000)**2)

# for row in trange(size):
#     for col in range(size):
#         if row == center:
#             dr = 0
#             dc = expo_norme(norme, row, col) * np.sign(col - center)
#         else:
#             alpha = atan((col - center) / (row - center))
#             if row-center < 0:
#                 if col-center < 0:
#                     alpha -= pi
#                 else:
#                     alpha += pi
#             dr = expo_norme(norme, row, col) * cos(alpha)
#             dc = expo_norme(norme, row, col) * sin(alpha)
#         vector_field[0, row, col] = dr
#         vector_field[1, row, col] = dc
# np.save("ignore/champ_radial_1856_20_expo.npy", vector_field)

# plt.figure()
# plt.imshow(img_now, cmap="gray")
# plt.quiver(np.arange(tile_size//2, len(img_now)-tile_size//2+1, step),
#            np.arange(tile_size//2, len(img_now[0])-tile_size//2+1, step),
#            vector_field_center[1],
#            vector_field_center[0],
#            color="red",
#            angles="xy",
#            scale_units="xy",
#            scale=1)
# plt.figure()
# plt.imshow(img_now, cmap="gray")
# plt.quiver(np.arange(size, step=10),
#            np.arange(size, step=10),
#            vector_field[1, ::10, ::10],
#            vector_field[0, ::10, ::10],
#            color="red",
#            angles="xy",
#            scale_units="xy",
#            scale=1)

print("application du champ d'advection...")
# output = apply_vector_field_forward(img_now, vector_field, 500, 1000, 1150, 1400)
# output = apply_vector_field_forward(img_now, vector_field, 0, 1000, 1150, 2650)
output = apply_vector_field_forward(img_now, vector_field, 0, 3712, 0, 3712)

Image.fromarray(output).save(f"ignore/3kmVIS006_msg03_202401011215_forward_{tile_size}_{step}.tif")

plt.show()