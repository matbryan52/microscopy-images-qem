import numpy as np
import tempfile
from skimage.io import imread
import matplotlib.pyplot as plt
import pathlib
from skimage.transform import rescale
rootdir = pathlib.Path(__file__).parent

img1 = imread(rootdir / "binary-particles.png", as_gray=True).astype(bool)
img1 = img1[25:125, 25:125]

yy, xx = np.nonzero(img1)
yyxx = np.stack((yy, xx), axis=1)
xx_unique = np.unique(xx)
yy_unique = np.unique(yy)
labelled = np.zeros_like(yy)

frames = []
next_label = 1
for this_idx, (y, x) in enumerate(zip(yy, xx)):
    group = [this_idx]
    for dx in range(-1, 2):
        _x = x + dx
        if not (_x in xx_unique):
            continue
        for dy in range(-1, 2):
            _y = y + dy
            if not (_y in yy_unique):
                continue
            idx, = (yyxx == (_y, _x)).all(axis=1).nonzero()
            if idx.size == 0:
                continue
            group.append(idx.item())

    if len(group) == 1:
        labelled[this_idx] = next_label
        next_label += 1
        continue
    else:
        group_labels = set(labelled[group])
        if group_labels == {0}:
            # new group
            labelled[group] = next_label
            next_label += 1
        else:
            group_labels = tuple(g for g in group_labels if g != 0)
            assert len(group_labels) == 1
            labelled[group] = group_labels[0]

    labelled_img = np.zeros(img1.shape, dtype=int)
    labelled_img[yy, xx] = labelled
    frames.append(labelled_img)

rgb_frames = []
with tempfile.TemporaryDirectory() as td:
    tempdir = pathlib.Path(td)
    for frame in frames:
        fpath = tempdir / "image.png"
        plt.imsave(fpath, rescale(frame, 4, order=0), cmap="tab10", vmin=0, vmax=labelled.max())
        rgb_frame = plt.imread(fpath)[..., :3]
        rgb_frame *= 255
        rgb_frames.append(rgb_frame.astype(np.uint8))

from imageio.v3 import imwrite

imwrite(rootdir / "connected.gif", rgb_frames, fps=40, loop=0)

# plt.imshow(labelled_img)
# plt.show()
