import pathlib
import numpy as np
import matplotlib.pyplot as plt
rootdir = pathlib.Path(__file__).parent
from skimage.transform import rotate
from skimage.feature import match_descriptors, plot_matched_features, SIFT, ORB

size = 200
t = 250
l = 130
crop = np.s_[t: t + size, l: l + size]
shifty, shiftx = 40, -20
# shifty, shiftx = 0, -0
crop2 = np.s_[t + shifty: t + shifty + size, l + shiftx: l + shiftx + size]
data = np.load(rootdir / "overview_100K_binned.npy")
img1 = data[crop].copy()
# img2 = rotate(data, 15)[crop2].copy()
img2 = data[crop2].copy()

# fig = plt.figure()
# plt.imshow(data, cmap="gray")

descriptor_extractor = SIFT()

descriptor_extractor.detect_and_extract(img1)
keypoints1 = descriptor_extractor.keypoints
descriptors1 = descriptor_extractor.descriptors

descriptor_extractor.detect_and_extract(img2)
keypoints2 = descriptor_extractor.keypoints
descriptors2 = descriptor_extractor.descriptors

matches12 = match_descriptors(
    descriptors1, descriptors2, max_ratio=0.6, cross_check=True, max_distance=20,
)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(4, 8))
plot_matched_features(
    img1,
    img2,
    keypoints0=keypoints1,
    keypoints1=keypoints2,
    matches=matches12,
    ax=ax,
    keypoints_color="orange",
    # only_matches=True,
    alignment="vertical",
)
ax.axhline(y=img1.shape[0], color="red", alpha=0.8, linestyle="--")
ax.axis('off')
fig.patch.set_alpha(0.)
plt.tight_layout(pad=0.5)
plt.savefig(rootdir / "align-sift.png", transparent=True)
# plt.show()
