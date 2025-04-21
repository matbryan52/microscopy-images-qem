import pathlib
rootdir = pathlib.Path(__file__).parent
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import RegularGridInterpolator


grid = np.mgrid[-4:5, -4:5]
radius = np.linalg.norm(grid, axis=0)
plt.imshow(radius, cmap="gray")


h, w = radius.shape
interp = RegularGridInterpolator((np.arange(h), np.arange(w)), radius, bounds_error=False)


dense_grid = np.meshgrid(
    np.linspace(0, h-1, num=128, endpoint=True),
    np.linspace(0, w-1, num=128, endpoint=True),
)
dense = interp(dense_grid)

plt.figure()
plt.imshow(dense, cmap="gray")



plt_slice = np.s_[4, :]
fig, ax = plt.subplots()
ax.plot(radius[plt_slice], "ko")
ax.plot(radius[plt_slice], "r--")
ax.set_xlabel("Coordinate (px)")
ax.set_ylabel("Value (px)")
plt.show()
