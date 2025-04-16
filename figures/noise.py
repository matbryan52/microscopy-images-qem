import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
from skimage.io import imread, imsave
from skimage.util import random_noise
import matplotlib.pyplot as plt
from skimage.restoration import denoise_wavelet

input = imread(rootdir / "overview_100K-binned.jpg", as_gray=True)
input = input[80:630, :550]
sigma = 0.17
noisy = random_noise(input, var=sigma**2)

denoised = denoise_wavelet(noisy, sigma=sigma, mode="soft")

combined = np.concatenate((noisy, denoised), axis=0)
# imsave(rootdir / "restoration.png", combined)
                          
fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)
ax1.imshow(noisy, cmap="gray")
ax2.imshow(denoised, cmap="gray")
plt.show()
