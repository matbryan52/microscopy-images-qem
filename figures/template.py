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

image = imread(rootdir / "noisy.png", as_gray=True)
image -= image.min()
image /= image.max()
image = (image * 255).astype(np.uint8)

cy, cx = 345, 162
t_window = 47
template = image[cy - t_window: cy + t_window + 1, cx - t_window: cx + t_window + 1]

t_xvals = [cx - t_window, cx + t_window, cx + t_window, cx - t_window, cx - t_window]
t_yvals = [cy - t_window, cy - t_window, cy + t_window, cy + t_window, cy - t_window]
result = match_template(image, template)
coords = peak_local_max(result, min_distance=20)

vmin, vmax = np.percentile(image, (1, 99.5))
fig = plt.figure()
plt.imshow(image, cmap="gray", vmin=vmin, vmax=vmax)
plt.plot(t_xvals, t_yvals, "--", color="#F28E2B", linewidth=2)
plt.plot(coords[:, 1] + t_window, coords[:, 0] + t_window, "o", color="orange")
plt.tight_layout(pad=0.5)
fig.patch.set_alpha(0.)
plt.savefig(rootdir / "template-matches.png", transparent=True)

# vmin, vmax = np.percentile(template, (1, 99.5))
# plt.figure()
# plt.imshow(template, cmap="gray", vmin=vmin, vmax=vmax)
# plt.show()

fig = plt.figure()
pos = plt.imshow(result, cmap="gray")
plt.plot(coords[:, 1], coords[:, 0], "o", color="orange")
fig.colorbar(pos)
fig.patch.set_alpha(0.)
plt.tight_layout(pad=0.5)
plt.savefig(rootdir / "template-correlation.png", transparent=True)
plt.show()




# row = 222

# frames = []
# correlations = []
# px_values = tuple(range(50, 450, 4))
# for idx, col in enumerate(tqdm.tqdm(px_values)):
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), dpi=180)
#     canvas = FigureCanvasAgg(fig)
#     disp = image.copy()
#     target = disp[row - t_window: row + t_window + 1, col - t_window: col + t_window + 1].copy()
#     correlation = np.mean((target - target.mean()) * (template - template.mean())) / (np.std(target)*np.std(template))
#     correlations.append(correlation)
#     disp[row - t_window: row + t_window + 1, col - t_window: col + t_window + 1] = template
#     ax1.imshow(disp, cmap="gray", vmin=vmin, vmax=vmax)

#     xvals = [col - t_window, col + t_window, col + t_window, col - t_window, col - t_window]
#     yvals = [row - t_window, row - t_window, row + t_window, row + t_window, row - t_window]
#     ax1.plot(xvals, yvals, "--", color="#F28E2B", linewidth=2)
#     ax1.plot(t_xvals, t_yvals, "--", color="#F28E2B", alpha=0.5, linewidth=2)

#     ax2.plot(px_values[:idx + 1], correlations, "kx-")
#     ax2.set_xlim(min(px_values), max(px_values))
#     ax2.set_ylim(-0.2, 0.5)
#     ax2.set_xlabel("Position (px)")
#     ax2.set_ylabel("Correlation (-)")
#     fig.tight_layout(pad=0.5)
#     fig.patch.set_facecolor("#faf4ed")
#     ax2.patch.set_facecolor("#faf4ed")
#     canvas.draw()
#     buf = canvas.buffer_rgba()
#     frames.append(buf)
#     plt.close(fig)
#     # break

# imwrite(rootdir / "template.gif", frames, fps=10, loop=0)

# vmin, vmax = np.percentile(template, (1, 99.5))
# plt.show()
