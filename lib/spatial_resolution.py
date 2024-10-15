
import numpy as np

def triple(im):
    """ 
    Return an other np.array, whose dimensions are three times those of im, each pixel of im being duplicated three times
    
    Arguments : 
        im : np.array 
            Picture that will be duplicated


    Returns : 
        np.array
            Same as im but three times bigger
    """

    if len(im.shape)!=2:
        raise ValueError("Argument is not a 2D numpy array")
    
    out1 = np.repeat(im,   3, axis=1)
    return np.repeat(out1, 3, axis=0)

def double(im):

    if len(im.shape)!=2:
        raise ValueError("Argument is not a 2D numpy array")
    
    out1 = np.repeat(im,   2, axis=1)
    return np.repeat(out1, 2, axis=0)

def half(im):
    return im[::2, ::2]

def third(im):
    return im[::3, ::3]

def msg_to_mtg(im_in, res_out):
    if res_out == 1:
        return triple(im_in)
    elif res_out == 2:
        return half(triple(im_in))
    else :
        raise ValueError("Resolution not supported")

def mtg_to_msg(im_in, res_in):
    if res_in == 2:
        return third(double(im_in))
    elif res_in == 1:
        return third(im_in)
    else:
        raise ValueError("Resolution not supported")
    
def change_resolution(image, res_in, res_out):
    """
    Convert a numpy array from a resolution to another

    Args:
        image: numpy array to handle
        res_in: input resolution
        res_out: output resolution
    Returns:
        Numpy array of the new picture
    """
    if res_in == 1:
        if res_out == 2:
            return half(image)
        elif res_out == 3:
            return third(image)
    elif res_in == 2:
        if res_out == 1:
            return double(image)
        elif res_out == 3:
            return third(double(image))
    elif res_in == 3:
        if res_out == 1:
            return triple(image)
        elif res_out == 2:
            return half(triple(image))
    raise ValueError("Resolution not supported")
