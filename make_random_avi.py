from glob import glob
from random import random
from sys import argv
from os.path import basename
from re import search

from lib.tif_to_avi import tif_to_avi

def sort_key(filename):
    """
    Extract the datetime of a msg or mtg tif file

    Args:
        filename: name of the file to extract
    Returns:
        None
    """
    res = basename(filename)
    # msg : YYYYMMDDhhmm
    # mtg : YYYYMMDD_hhmmss
    # we can handle both with this regex
    res = search(r"(\d{8}_?\d+)\.tif", res)[0]
    return res

def make_random_avi(type, proba, dest):
    """
    Create a avi video with pictures of initial or simulated msg or mtg

    Args:
        type: type of pictures, mtg or msg
        proba: probability of getting initial picture instead of simulated, for each frame
        dest: output file
    Returns:
        None
    """
    if type == "msg":
        iterator_initial = glob(f"data_verification/msg_initial/tif/*VIS*")
        iterator_simule = glob(f"data_verification/msg_simule/tif_gamma_correction/*VIS*")
        size = 3712
    elif type == "mtg":
        iterator_initial = glob(f"data_verification/mtg_initial/tif/*2*VIS*")
        iterator_simule = glob(f"data_verification/mtg_simule/texted_tif/*2*VIS*")
        size = 5568
    
    iterator_initial.sort()
    iterator_simule.sort()

    # we remove the datetime that are not present in both the iterator
    # to compare the same datetime at each iteration
    while sort_key(iterator_initial[0]) < sort_key(iterator_simule[0]):
        iterator_initial.pop(0)
    while sort_key(iterator_initial[0]) > sort_key(iterator_simule[0]):
        iterator_simule.pop(0)
    
    frames = []
    for ini, sim in zip(iterator_initial, iterator_simule):
        if random() < proba:
            frames.append(ini)
        else:
            frames.append(sim)

    tif_to_avi(frames, dest, size, size)

if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage : python3 make_random_avi.py mtg|msg proba dest")
        exit(1)
    make_random_avi(argv[1], float(argv[2]), argv[3])