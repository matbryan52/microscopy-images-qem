import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import colorcet
from skimage.transform import downscale_local_mean


cmap = matplotlib.colormaps.get_cmap("cet_cyclic_isoluminant")

input = plt.imread(rootdir / "tiled-roofing-new-roof.jpg")[..., :3].mean(axis=-1)
input = downscale_local_mean(input, (2, 2))
output = np.fft.fft2(input)
output[0, 0] = 0.
output = np.fft.fftshift(output)

fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(input, cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-input.png", transparent=True)
plt.close(fig)
# plt.show()

fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(np.log(np.abs(output)), cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-abs.png", transparent=True)
plt.close(fig)

fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(np.angle(output), cmap="bwr", vmin=-np.pi, vmax=np.pi)
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-phase.png", transparent=True)
plt.close(fig)
