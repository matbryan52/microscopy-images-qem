import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator, griddata

data = np.load(rootdir / "gaps-small.npy")

plt.imshow(data, cmap="gray")

mask = np.logical_or(data > 0.45, data < 0.15)
plt.figure()
plt.imshow(mask, cmap="gray", vmin=data.min(), vmax=data.max())

h, w = data.shape
coordinates = np.mgrid[:h, :w].reshape(2, -1).T
valid = np.flatnonzero(~mask)
coordinates = coordinates[valid, :]
values = data.ravel()[valid]
infill = np.nonzero(mask)
invalid = np.flatnonzero(mask)


out_vals = griddata(
    coordinates,
    values,
    infill,
    method="cubic",
)

filled = data.copy()
filled.ravel()[invalid] = out_vals

plt.figure()
plt.imshow(filled, cmap="gray", vmin=data.min(), vmax=data.max())

plt.show()
