import matplotlib.pyplot as plt
import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
from skimage.transform import downscale_local_mean

size = 512
radius = (np.linalg.norm(np.mgrid[-size: size, -size: size], axis=0)).astype(np.float32)
radius /= size

freq = np.exp(4 * radius) / (2 * np.pi)
print("min period: ", 1 / freq[size, 0])
img1 = np.cos(2 * np.pi * freq)
fig, (ax1) = plt.subplots(figsize=(3, 3), dpi=180)
ax1.imshow(img1, cmap="gray")
ax1.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "sampling-high.png", transparent=True)
plt.close(fig)

print(img1.shape)
img2 = downscale_local_mean(img1, (2, 2))
print(img2.shape)
fig, (ax2) = plt.subplots(figsize=(3, 3), dpi=180)
ax2.imshow(img2, cmap="gray")
ax2.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "sampling-medium.png", transparent=True)
plt.close(fig)


img3 = downscale_local_mean(img1, (8, 8))
print(img3.shape)
fig, (ax2) = plt.subplots(figsize=(3, 3), dpi=180)
ax2.imshow(img3, cmap="gray")
ax2.axis('off')
fig.tight_layout()
plt.savefig(rootdir / "sampling-low.png", transparent=True)
plt.close(fig)


# fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True)
# ax1.imshow(np.fft.fftshift(np.fft.fft2(img1, s=img1.shape)).real)
# ax2.imshow(np.fft.fftshift(np.fft.fft2(img2, s=img1.shape)).real)
# ax3.imshow(np.fft.fftshift(np.fft.fft2(img3, s=img1.shape)).real)
# plt.show()
