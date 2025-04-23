import pathlib
import numpy as np
import matplotlib.pyplot as plt
from skimage.registration import phase_cross_correlation
rootdir = pathlib.Path(__file__).parent
from skimage.io import imread
from scipy.fft import fftn, ifftn
from imageio.v3 import imwrite


crop = np.s_[450:850, 350:750]
shifty, shiftx = 40, 30
crop2 = np.s_[450 + shifty:850 + shifty, 350 + shiftx:750 + shiftx]
img1 = imread(rootdir / "ADF-00011.png", as_gray=True)[crop]
img2 = imread(rootdir / "ADF-00011.png", as_gray=True)[crop2]
# img2 = imread(rootdir / "ADF-00021.png", as_gray=True)[crop2]
shift, error, phasediff = phase_cross_correlation(img1, img2)
shift = tuple(int(s) for s in shift)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), dpi=180)
ax1.imshow(img1, cmap="gray")
ax2.imshow(img2, cmap="gray")

src_freq = fftn(img1)
target_freq = fftn(img2)

img1 -= img1.min()
img2 -= img2.min()
img1 /= img1.max()
img2 /= img2.max()
img1 *= 255
img2 *= 255
imwrite(rootdir / "to-align.gif", [img1.astype(np.uint8), img2.astype(np.uint8)], fps=2, loop=0)

start = (237, 204)
end = tuple(a + b for a, b in zip(start, shift))
# ax2.annotate("", xy=end[::-1], xytext=start[::-1], arrowprops=dict(facecolor='orange', shrink=0.05))

image_product = src_freq * target_freq.conj()
cross_correlation = np.abs(ifftn(image_product))
cross_correlation = np.fft.fftshift(cross_correlation)
maxy, maxx = np.unravel_index(np.argmax(cross_correlation), cross_correlation.shape)

hh2, ww2 = np.asarray(cross_correlation.shape) / 2
fig, ax1 = plt.subplots(1, 1, figsize=(4.5, 4), dpi=180)
ax1.imshow(cross_correlation, cmap="gray", extent=(-ww2, ww2, hh2, -hh2))
ax1.plot(maxx-ww2, maxy-ww2, "o", color="red", label="Correlation max")
ax1.axhline(y=0, color="blue", linestyle="--", alpha=0.5, label="Zero shift")
ax1.axvline(x=0, color="blue", linestyle="--", alpha=0.5)
ax1.legend()
ax1.set_xlabel("X-shift (px)")
ax1.set_ylabel("Y-shift (px)")
fig.patch.set_alpha(0.)
plt.tight_layout(pad=0.5)
plt.savefig(rootdir / "xcorr-align.png", transparent=True)
plt.show()
