import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib.pyplot as plt
from skimage.color import label2rgb

from skimage.io import imread
input = imread(rootdir / "overview_100K-binned.jpg", as_gray=True)
input = input[410:]

levels = [
    (0, 0.05),
    (0.05, 0.25),
    (0.25, 0.75),
    (0.75, 1.),
]

label_image = np.zeros(input.shape, dtype=np.uint8)
for idx, (low, high) in enumerate(levels, start=1):
    label_image[np.logical_and(input >= low, input < high)] = idx

plt.figure()
plt.imshow(input, cmap="gray")
plt.figure()
color1 = label2rgb(label_image, image=input, bg_label=0)
plt.imshow(color1)
plt.show()
