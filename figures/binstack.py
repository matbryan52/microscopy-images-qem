import numpy as np
from skimage.io import imread
import matplotlib.pyplot as plt
import pathlib
from skimage.transform import downscale_local_mean, resize
rootdir = pathlib.Path(__file__).parent

img1 = imread(rootdir / "noisy.png", as_gray=True)
print(img1.shape)
binned = downscale_local_mean(img1, (4, 4))
print(binned.shape)
binned = resize(binned, img1.shape, order=0)

fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.imshow(img1, cmap="gray")
ax2.imshow(binned, cmap="gray")

fig, (ax1) = plt.subplots(1, 1)
ax1.plot(img1[290, :], color="black", alpha=0.7, label="Raw")
ax1.plot(binned[290, :], color="orange", label="Binned", linewidth=2)
ax1.legend()
fig.patch.set_facecolor("#faf4ed")
plt.show()
