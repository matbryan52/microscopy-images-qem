import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import downscale_local_mean
from skimage.filters import median
from scipy.ndimage import convolve

from skimage.io import imread, imsave
input = imread(rootdir / "overview_100K-binned.jpg", as_gray=True)
input = downscale_local_mean(input, (4, 4))
input *= 2


def arb_smooth_kernel(size: int):
    idxs = np.arange(size) - size // 2
    xx, yy = np.meshgrid(idxs, idxs)
    kernel = np.sqrt(xx ** 2 + yy ** 2)
    kernel *= -1
    kernel -= kernel.min()
    kernel += 1
    return kernel / kernel.sum()


def Smooth(image, window: int):
    k = arb_smooth_kernel(window)
    return (
        convolve(image, k, mode='reflect')
    )


h, w = input.shape

num = 1000
random_x = np.random.randint(0, w, size=num)
random_y = np.random.randint(0, h, size=num)

input[random_y, random_x] += 1.

random_x = np.random.randint(0, w, size=num)
random_y = np.random.randint(0, h, size=num)
input[random_y, random_x] = 0.

input -= input.min()
input /= input.max()

plt.figure()
plt.imshow(input, cmap="gray")
plt.figure()
plt.imshow(Smooth(input, 3), cmap="gray")
plt.figure()
plt.imshow(median(input), cmap="gray")
plt.show()
