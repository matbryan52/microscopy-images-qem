import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib.pyplot as plt

from skimage import img_as_float
from skimage.util import view_as_windows
from skimage.morphology import footprint_rectangle
from skimage.restoration import denoise_nl_means, estimate_sigma


noisy = img_as_float(np.load(rootdir / "noisy.npy"))
noisy -= noisy.min()
noisy /= noisy.max()

sigma = 0.08

# estimate the noise standard deviation from the noisy image
sigma_est = np.mean(estimate_sigma(noisy))
print(f'estimated noise standard deviation = {sigma_est}')

patch_kw = dict(
    patch_size=7,  # 5x5 patches
    patch_distance=18,  # 13x13 search area
)


test_pt = (220, 150)
mean_image = view_as_windows(noisy, (7, 7)).mean(axis=(-1, -2))
similarity = np.exp(-1 * np.abs(mean_image**2 - mean_image[test_pt]**2) / sigma_est**2)
plt.figure()
plt.imshow(similarity)
# plt.plot(*test_pt[::-1], 'ro', markersize=20)


plt.figure()
plt.imshow(mean_image)

# # slow algorithm
# denoise = denoise_nl_means(noisy, h=1.15 * sigma_est, fast_mode=False, **patch_kw)

# # slow algorithm, sigma provided
# denoise2 = denoise_nl_means(
#     noisy, h=0.8 * sigma_est, sigma=sigma_est, fast_mode=False, **patch_kw
# )

# # fast algorithm
# denoise_fast = denoise_nl_means(noisy, h=0.8 * sigma_est, fast_mode=True, **patch_kw)

# fast algorithm, sigma provided
denoise2_fast = denoise_nl_means(
    noisy, h=sigma_est, sigma=sigma_est, fast_mode=True, **patch_kw
)

plt.imshow(denoise2_fast, cmap="gray")
plt.show()
exit()

fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(8, 6), sharex=True, sharey=True)

ax[0, 0].imshow(noisy, cmap="gray")
ax[0, 0].axis('off')
ax[0, 0].set_title('noisy')
ax[0, 1].imshow(denoise, cmap="gray")
ax[0, 1].axis('off')
ax[0, 1].set_title('non-local means\n(slow)')
ax[0, 2].imshow(denoise2, cmap="gray")
ax[0, 2].axis('off')
ax[0, 2].set_title('non-local means\n(slow, using $\\sigma_{est}$)')
ax[1, 0].set_title('original\n(noise free)')
ax[1, 1].imshow(denoise_fast, cmap="gray")
ax[1, 1].axis('off')
ax[1, 1].set_title('non-local means\n(fast)')
ax[1, 2].imshow(denoise2_fast, cmap="gray")
ax[1, 2].axis('off')
ax[1, 2].set_title('non-local means\n(fast, using $\\sigma_{est}$)')

fig.tight_layout()

# # print PSNR metric for each case
# psnr_noisy = peak_signal_noise_ratio(astro, noisy)
# psnr = peak_signal_noise_ratio(astro, denoise)
# psnr2 = peak_signal_noise_ratio(astro, denoise2)
# psnr_fast = peak_signal_noise_ratio(astro, denoise_fast)
# psnr2_fast = peak_signal_noise_ratio(astro, denoise2_fast)

# print(f'PSNR (noisy) = {psnr_noisy:0.2f}')
# print(f'PSNR (slow) = {psnr:0.2f}')
# print(f'PSNR (slow, using sigma) = {psnr2:0.2f}')
# print(f'PSNR (fast) = {psnr_fast:0.2f}')
# print(f'PSNR (fast, using sigma) = {psnr2_fast:0.2f}')

plt.show()