from libertem_ui.applications.image_utils import fine_adjust, ImageTransformer
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from imageio.v3 import imwrite
rootdir = pathlib.Path(__file__).parent
from skimage.io import imread
from skimage.transform import AffineTransform


img1 = imread(rootdir / "ADF-00011.png", as_gray=True)
img2 = imread(rootdir / "ADF-00021.png", as_gray=True)

tfor = AffineTransform(scale=(1.051, 1.051), translation=(-21.3, 74.0))
transformer_moving = ImageTransformer(img2)
transformer_moving.add_transform(tfor, output_shape=img1.shape)
transformed = transformer_moving.get_transformed_image(cval=0)

print(img1.shape)

img1 = (np.tile(img1[..., np.newaxis], (1, 1, 4)) * 255).astype(np.uint8)
img1[..., -1] = 255
transparent = 1 - (transformed == 0)
transformed = (np.tile(transformed[..., np.newaxis], (1, 1, 4)) * 255).astype(np.uint8)
transformed[..., -1] = 255 * transparent

imwrite(rootdir / "align.gif", [img1, transformed], fps=2, loop=65000)

# fig, (ax1, ax2) = plt.subplots(1, 2)
# ax1.imshow(img1, cmap="gray")
# ax2.imshow(transformed, cmap="gray")
# plt.show()


# layout, getter = fine_adjust(img1, img2, initial_transform=tfor)
# layout.show()
# print(getter())

