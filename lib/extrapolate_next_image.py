from .apply_vector_field_forward import apply_vector_field_forward
from .phase_correlation import fourier_flow
from scipy.ndimage import zoom
import numpy as np


def extrapolate_next_image(img_now, img_prev, input_delta, output_delta):
    """
    From 2 pictures, extrapolate the next one thanks to the optical flow

    Args:
        img_now: ndarray
        img_prev: ndarray
        input_delta: time between the 2 input pictures
        output_delta: deltatime wanted between img_now and the extrapolated picture
    Returns:
        output: ndarray
    """
    height, width = len(img_now), len(img_now[0])
    case_size = 32
    step = 16

    vector_field_center, _ = fourier_flow(img_now, img_prev, case_size, step)

    print("zoom...")
    vector_field_center_zoomed = np.zeros((2,vector_field_center.shape[1]*step, vector_field_center.shape[2]*step))
    vector_field_center_zoomed[0,:,:] = zoom(vector_field_center[0,:,:], step)
    vector_field_center_zoomed[1,:,:] = zoom(vector_field_center[1,:,:], step)

    _, height_center, width_center = vector_field_center_zoomed.shape

    width_to_add = (width - width_center) // 2
    height_to_add = (height - height_center) // 2
    vector_field = np.zeros((2, height, width))
    vector_field[0,:,:] = np.pad(vector_field_center_zoomed[0,:,:], ((height_to_add,), (width_to_add,)))
    vector_field[1,:,:] = np.pad(vector_field_center_zoomed[1,:,:], ((height_to_add,), (width_to_add,)))

    vector_field *= output_delta / input_delta

    output = apply_vector_field_forward(img_now, vector_field)

    return output