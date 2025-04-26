import pathlib
import numpy as np
import matplotlib.pyplot as plt

from skimage import data
from skimage import transform
from skimage.io import imread

rootdir = pathlib.Path(__file__).parent

img = imread(rootdir / "AlN_2D_sousGaNx6M.tif", as_gray=True)
img = img[:512, :512]

tform3 = transform.AffineTransform(shear=(np.deg2rad(5), np.deg2rad(2)))
warped = transform.warp(img, tform3, preserve_range=True)
fig, ax = plt.subplots(1, 2, figsize=(8, 5))
to_disp = img[100:500, 50:450]
vmin, vmax = to_disp.min(), to_disp.max()
ax[0].imshow(to_disp, cmap=plt.cm.gray, vmin=vmin, vmax=vmax)
ax[1].imshow(warped[100:500, 50:450], cmap=plt.cm.gray, vmin=vmin, vmax=vmax)
plt.show()
