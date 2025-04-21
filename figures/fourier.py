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
output_orig = np.fft.fft2(input)
output = output_orig.copy()
output[0, 0] = 0.
output = np.fft.fftshift(output)
h, w = output.shape


signal_c = np.zeros_like(output_orig)
sl1, sl2 = np.s_[10, 5], np.s_[-10, -5]
signal_c[sl1] = output_orig[sl1]
signal_c[sl2] = output_orig[sl2]
recon_one = np.fft.ifft2(signal_c).real


signal_c = np.zeros_like(output_orig)
sl1, sl2 = np.s_[0, 28], np.s_[0, -28]
signal_c[sl1] = output_orig[sl1]
signal_c[sl2] = output_orig[sl2]
recon_two = np.fft.ifft2(signal_c).real

output_orig = np.fft.fftshift(output_orig)

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


fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(np.sign(output.real) * np.sqrt(np.abs(output.real)), cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-real.png", transparent=True)
plt.close(fig)

fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(np.sign(output.imag) * np.sqrt(np.abs(output.imag)), cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-imag.png", transparent=True)
plt.close(fig)


crop = 32
cy, cx = h//2, w//2
fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(np.log(np.abs(output_orig))[cy-crop:cy+crop+1, cx-crop:cx+crop+1], cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-crop.png", transparent=True)
plt.close(fig)


fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(recon_one, cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-recon-single.png", transparent=True)
plt.close(fig)


fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
ax.imshow(recon_two, cmap="gray")
ax.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "fourier-recon-single-2.png", transparent=True)
plt.close(fig)
