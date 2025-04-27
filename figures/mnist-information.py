import numpy as np
from sklearn.datasets import load_digits
import matplotlib.pyplot as plt

digits = load_digits()
digit = digits["data"][205].astype(np.uint8)
digit: np.ndarray

plt.imshow(digit.reshape(8, 8), cmap="gray")
plt.figure()
plt.imshow(digit.view(np.uint16).reshape((4, 8), order="F"), cmap="gray")
plt.show()
