import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib.pyplot as plt

from skimage.io import imread
image = imread(rootdir / "overview_100K-binned.jpg", as_gray=True)
image = image[410:]
image *= 255
image= image.astype(np.uint8)

import matplotlib.pyplot as plt

from skimage.feature import graycomatrix, graycoprops
from skimage import data


PATCH_SIZE = 10


patch_def = {
    "Void": [(274, 151), (303, 250), (300, 205)],
    "LightGrey": [(75, 90), (115, 370), (271, 640), (195, 467)],
    "DarkGrey": [(150, 25), (134, 214), (194, 726), (285, 545)],
    # "Bright": [(310, 25), (3, 200)],
}

patches = {}
for name, regions in patch_def.items():
    patches[name] = []
    for loc in regions:
        patches[name].append(
            image[loc[0] : loc[0] + PATCH_SIZE, loc[1] : loc[1] + PATCH_SIZE]
        )

# compute some GLCM properties each patch
xs = {}
ys = {}
for name, sub_patches in patches.items():
    xs[name] = []
    ys[name] = []
    for patch in sub_patches:
        glcm = graycomatrix(
            patch, distances=[5, 2], angles=[0, np.pi / 2], levels=256, symmetric=True, normed=True
        )
        xs[name].append(graycoprops(glcm, 'dissimilarity')[0, 0])
        ys[name].append(graycoprops(glcm, 'correlation')[0, 0])

# # create the figure
# fig = plt.figure(figsize=(8, 8))

# # display original image with locations of patches
# ax = fig.add_subplot(3, 2, 1)
# ax.imshow(image, cmap=plt.cm.gray, vmin=0, vmax=255)
# for y, x in void_locations:
#     ax.plot(x + PATCH_SIZE / 2, y + PATCH_SIZE / 2, 'gs')
# for y, x in sky_locations:
#     ax.plot(x + PATCH_SIZE / 2, y + PATCH_SIZE / 2, 'bs')
# ax.set_xlabel('Original Image')
# ax.set_xticks([])
# ax.set_yticks([])
# ax.axis('image')

# for each patch, plot (dissimilarity, correlation)
fig, ax = plt.subplots()
for name in xs.keys():
    ax.plot(xs[name], ys[name], 'o', label=name)
ax.set_xlabel('GLCM Dissimilarity')
ax.set_ylabel('GLCM Correlation')
ax.legend()

# # display the image patches
# for i, patch in enumerate(void_patches):
#     ax = fig.add_subplot(3, len(void_patches), len(void_patches) * 1 + i + 1)
#     ax.imshow(patch, cmap=plt.cm.gray, vmin=0, vmax=255)
#     ax.set_xlabel(f"void {i + 1}")

# for i, patch in enumerate(sky_patches):
#     ax = fig.add_subplot(3, len(sky_patches), len(sky_patches) * 2 + i + 1)
#     ax.imshow(patch, cmap=plt.cm.gray, vmin=0, vmax=255)
#     ax.set_xlabel(f"Sky {i + 1}")


# # display the patches and plot
# fig.suptitle('Grey level co-occurrence matrix features', fontsize=14, y=1.05)
# plt.tight_layout()
plt.show()
