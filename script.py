from shapely import Polygon, Point
from math import ceil
from shapely.plotting import plot_polygon, plot_points
from random import uniform
import matplotlib.pyplot as plt
from time import perf_counter
import numpy as np
from tqdm import trange
from multiprocessing import Pool, Array
from multiprocessing.shared_memory import SharedMemory

array = [[(1,2,3), (4,5,6)], [], [(7,8,9)]]

print(np.concatenate([a for a in array if a]))