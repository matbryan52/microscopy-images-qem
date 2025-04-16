import pathlib
from skimage.io import imread
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib.pyplot as plt
from skimage import segmentation, feature, future
from sklearn.ensemble import RandomForestClassifier
from functools import partial

img = imread(rootdir / "base-image.png", as_gray=True)

# Build an array of labels for training the segmentation.
# Here we use rectangles but visualization libraries such as plotly
# (and napari?) can be used to draw a mask on the image.
training_labels = np.zeros(img.shape[:2], dtype=np.uint8)
training_labels[77:200, 200:] = 1
training_labels[325:390, 200:770] = 2
training_labels[440:580, 200:770] = 3
training_labels[660:800, :800] = 4
training_labels[930:975, 200:770] = 2
training_labels[:15, 200:] = 5

sigma_min = 1
sigma_max = 4
features_func = partial(
    feature.multiscale_basic_features,
    intensity=True,
    edges=True,
    texture=False,
    sigma_min=sigma_min,
    sigma_max=sigma_max,
)
features = features_func(img)
clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, max_depth=10, max_samples=0.05)
clf = future.fit_segmenter(training_labels, features, clf)
result = future.predict_segmenter(features, clf)

fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(9, 4))
ax[0].imshow(img, cmap="gray")
# ax[0].contour(training_labels)
ax[0].set_title('Image, mask and segmentation boundaries')
ax[1].imshow(result)
ax[1].set_title('Segmentation')
fig.tight_layout()
plt.show()
exit()

##############################################################################
# Feature importance
# ------------------
#
# We inspect below the importance of the different features, as computed by
# scikit-learn. Intensity features have a much higher importance than texture
# features. It can be tempting to use this information to reduce the number of
# features given to the classifier, in order to reduce the computing time.
# However, this can lead to overfitting and a degraded result at the boundary
# between regions.

fig, ax = plt.subplots(1, 2, figsize=(9, 4))
l = len(clf.feature_importances_)
feature_importance = (
    clf.feature_importances_[: l // 3],
    clf.feature_importances_[l // 3 : 2 * l // 3],
    clf.feature_importances_[2 * l // 3 :],
)
sigmas = np.logspace(
    np.log2(sigma_min),
    np.log2(sigma_max),
    num=int(np.log2(sigma_max) - np.log2(sigma_min) + 1),
    base=2,
    endpoint=True,
)
for ch, color in zip(range(3), ['r', 'g', 'b']):
    ax[0].plot(sigmas, feature_importance[ch][::3], 'o', color=color)
    ax[0].set_title("Intensity features")
    ax[0].set_xlabel("$\\sigma$")
for ch, color in zip(range(3), ['r', 'g', 'b']):
    ax[1].plot(sigmas, feature_importance[ch][1::3], 'o', color=color)
    ax[1].plot(sigmas, feature_importance[ch][2::3], 's', color=color)
    ax[1].set_title("Texture features")
    ax[1].set_xlabel("$\\sigma$")

fig.tight_layout()

##############################################################################
# Fitting new images
# ------------------
#
# If you have several images of similar objects acquired in similar conditions,
# you can use the classifier trained with `fit_segmenter` to segment other
# images. In the example below we just use a different part of the image.

img_new = full_img[:700, 900:]

features_new = features_func(img_new)
result_new = future.predict_segmenter(features_new, clf)
fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(6, 4))
ax[0].imshow(segmentation.mark_boundaries(img_new, result_new, mode='thick'))
ax[0].set_title('Image')
ax[1].imshow(result_new)
ax[1].set_title('Segmentation')
fig.tight_layout()

plt.show()
