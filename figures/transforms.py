import pathlib
import numpy as np
import matplotlib.pyplot as plt

from skimage import data
from skimage import transform

rootdir = pathlib.Path(__file__).parent

img = plt.imread(rootdir / "street.jpg")

h, w = 300, 300
src = np.array([[0, 0], [0, h], [w, h], [w, 0]])
dst = np.array([[113, 53], [260, 161], [250, 380], [78, 375]])

tform3 = transform.ProjectiveTransform()
tform3.estimate(src, dst)
warped = np.fliplr(np.rot90(transform.warp(img, tform3, output_shape=(h, w)), 3))

fig, ax = plt.subplots(nrows=2, figsize=(6, 6))

ax[0].imshow(img, cmap=plt.cm.gray)
ax[0].plot(dst[:, 0], dst[:, 1], '.g', markersize=20)
ax[0].set_ylim(400, 0)
ax[1].imshow(warped, cmap=plt.cm.gray)

for a in ax:
    a.axis('off')

plt.tight_layout()
# plt.show()
plt.savefig(rootdir / "skimage-transform.png", transparent=True)
plt.close()

h, w, c = img.shape

tform3 = transform.AffineTransform(scale=(0.5, 0.4))
warped = transform.warp(img, tform3)
plt.imsave(rootdir / "skimage-transform-scale.png", warped)

tform3 = transform.AffineTransform(translation=(100, -100))
warped = transform.warp(img, tform3)
plt.imsave(rootdir / "skimage-transform-shift.png", warped)

tform3 = transform.AffineTransform(shear=5.)
warped = transform.warp(img, tform3)
plt.imsave(rootdir / "skimage-transform-shear.png", warped)



from libertem_ui.applications.image_transformer import ImageTransformer

tt = ImageTransformer(img)
tt.rotate_about_center(rotation_degrees=20)
warped = tt.get_transformed_image(output_shape=(h, w, c), cval=0., preserve_range=False)
plt.imsave(rootdir / "skimage-transform-rotate.png", warped)
