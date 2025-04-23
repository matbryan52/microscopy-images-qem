import pathlib
import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from skimage.io import imread
from imageio.v3 import imwrite
rootdir = pathlib.Path(__file__).parent
from skimage.feature import match_template
from skimage.feature import peak_local_max
from scipy.ndimage import convolve

def arb_sobel_kernel(size: int):
    idxs = np.arange(size) - size // 2
    ii = np.tile(idxs[:, np.newaxis], (1, size))
    jj = ii.T.copy()
    det = ii * ii + jj * jj
    det[size // 2, size // 2] = 1
    kernel_y = ii / det
    kernel_x = jj / det
    return kernel_x, kernel_y

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


def Sobel(image, window: int):
    k_x, k_y = arb_sobel_kernel(window)
    return (
        np.abs(convolve(image, k_x, mode='reflect'))
        + np.abs(convolve(image, k_y, mode='reflect'))
    )

image = np.load(rootdir / "many-spots.npy")
image -= image.min()
image /= image.max()
image_sobel = Sobel(Smooth(image, 3), 3)
# image = (image * 255).astype(np.uint8)


cy, cx = 326, 220
t_window = 30
template = image[cy - t_window: cy + t_window + 1, cx - t_window: cx + t_window + 1]
template_sobel = image_sobel[cy - t_window: cy + t_window + 1, cx - t_window: cx + t_window + 1].copy()
template_sobel[template_sobel < 0.13] = -1.

t_xvals = [cx - t_window, cx + t_window, cx + t_window, cx - t_window, cx - t_window]
t_yvals = [cy - t_window, cy - t_window, cy + t_window, cy + t_window, cy - t_window]

result = match_template(image, template)
result_sobel = match_template(image_sobel, template_sobel)

xlim = (113, 330)
ylim = (216, 434)[::-1]

xlim_c = tuple(v - t_window for v in xlim)
ylim_c = tuple(v - t_window for v in ylim)

vmin, vmax = np.percentile(image, (1, 99.5))
fig = plt.figure()
plt.imshow(image, cmap="gray", vmin=vmin, vmax=vmax)
plt.plot(t_xvals, t_yvals, "--", color="#F28E2B", linewidth=2)
# plt.plot(coords[:, 1] + t_window, coords[:, 0] + t_window, "o", color="orange")
plt.xlim(*xlim)
plt.ylim(*ylim)
plt.tight_layout(pad=0.5)
fig.patch.set_alpha(0.)

vmin, vmax = np.percentile(image_sobel, (1, 99.5))
fig = plt.figure()
plt.imshow(image_sobel, cmap="gray", vmin=vmin, vmax=vmax)
plt.plot(t_xvals, t_yvals, "--", color="#F28E2B", linewidth=2)
# plt.plot(coords[:, 1] + t_window, coords[:, 0] + t_window, "o", color="orange")
plt.xlim(*xlim)
plt.ylim(*ylim)
plt.tight_layout(pad=0.5)
fig.patch.set_alpha(0.)

# vmin, vmax = np.percentile(result, (1, 99.5))
fig = plt.figure()
plt.imshow(result, cmap="gray") #, vmin=vmin, vmax=vmax)
# plt.plot(coords[:, 1] + t_window, coords[:, 0] + t_window, "o", color="orange")
plt.xlim(*xlim_c)
plt.ylim(*ylim_c)
plt.tight_layout(pad=0.5)
fig.patch.set_alpha(0.)

# vmin, vmax = np.percentile(result_sobel, (1, 99.5))
fig = plt.figure()
plt.imshow(result_sobel, cmap="gray") #, vmin=vmin, vmax=vmax)
# plt.plot(coords[:, 1] + t_window, coords[:, 0] + t_window, "o", color="orange")
plt.xlim(*xlim_c)
plt.ylim(*ylim_c)
plt.tight_layout(pad=0.5)
fig.patch.set_alpha(0.)

vmin, vmax = np.percentile(template_sobel, (1, 99.5))
fig = plt.figure()
plt.imshow(template_sobel, cmap="gray", vmin=vmin, vmax=vmax)
# plt.plot(coords[:, 1] + t_window, coords[:, 0] + t_window, "o", color="orange")
plt.tight_layout(pad=0.5)
fig.patch.set_alpha(0.)

plt.show()
