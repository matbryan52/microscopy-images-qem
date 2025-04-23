import pathlib
import numpy as np
import matplotlib.pyplot as plt
rootdir = pathlib.Path(__file__).parent
from scipy.ndimage import maximum_filter, center_of_mass

data = np.load(rootdir / "peaks.npy")
max_data = maximum_filter(data, size=20)

vmin, vmax = np.percentile(data, (1, 99.5))

# plt.figure()
# plt.imshow(data, cmap="gray", vmin=vmin, vmax=vmax)

vmin, vmax = np.percentile(max_data, (1, 99.5))

equal = np.argwhere(max_data == data)

# fig, ax = plt.subplots()
# ax.imshow(max_data, cmap="gray")
# ax.plot(equal[:, 1], equal[:, 0], 'o', color="orange")


# h, w = data.shape
# sl = np.s_[h // 2, 225:360]
# fig, ax = plt.subplots(figsize=(6, 4), dpi=180)
# ax.plot(data[sl], "k--", label="Raw")
# ax.plot(max_data[sl], "r-", label="Max-filter")
# values = np.argwhere(max_data[sl] == data[sl]).ravel()
# ax.plot(values, max_data[sl][values], "ro", label="Peaks")
# ax.set_xlabel("Pixel")
# ax.set_ylabel("Intensity")
# legend = ax.legend()
# # fig.patch.set_facecolor("#faf4ed")
# fig.patch.set_alpha(0.)
# ax.patch.set_alpha(0.)
# plt.savefig(rootdir / "peaks-plot.png", transparent=True)

display_window = 5
com_window = 2
for idx in (13,):
    my, mx = equal[idx]
    rel_cy, rel_cx = display_window, display_window
    patch = data[my - display_window: my + display_window + 1, mx - display_window: mx + display_window + 1]
    hh, ww = patch.shape
    hh2, ww2 = hh // 2, ww // 2
    com_patch = data[my - com_window: my + com_window + 1, mx - com_window: mx + com_window + 1]
    com_cy, com_cx = center_of_mass(com_patch)
    com_cy += (display_window - com_window)
    com_cx += (display_window - com_window)
    com_cy -= 0.2
    com_cx -= 0.05
    fig, ax = plt.subplots(figsize=(6, 6), dpi=180)
    ax.imshow(patch, cmap="gray")
    ax.plot(rel_cx, rel_cy, "o", color="#4E79A7", label="Raw peak")
    ax.plot(com_cx, com_cy, "o", color="#F28E2B", label="CoM peak")
    com_window2 = com_window + 0.5
    xvals = [ww2 - com_window2, ww2 + com_window2, ww2 + com_window2, ww2 - com_window2, ww2 - com_window2]
    yvals = [hh2 - com_window2, hh2 - com_window2, hh2 + com_window2, hh2 + com_window2, hh2 - com_window2]
    ax.plot(xvals, yvals, "--", color="#F28E2B", label="CoM window", linewidth=2)
    ax.legend()

fig.patch.set_alpha(0.)
plt.tight_layout()
plt.savefig(rootdir / "peaks-com.png", transparent=True)
plt.show()
