import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from imageio.v3 import imwrite
from matplotlib.backends.backend_agg import FigureCanvasAgg

import pathlib
rootdir = pathlib.Path(__file__).parent

import tempfile

rings = 20
cx = 0
cy = 0
lim = 100
r = 50
arrays = []
num_frames = 60
for i in 15 * np.sin(2 * np.pi * np.linspace(0, 1, num=num_frames)):
    fig, ax = plt.subplots(figsize=(4, 4), dpi=220)
    canvas = FigureCanvasAgg(fig)
    cy_shifted = i + cy
    for r in np.linspace(0.1 * r, r, num=rings, endpoint=True):
        circle = Circle((cx, cy_shifted), r, fill=False, linestyle="-", color='black')
        ax.add_artist(circle)
        circle = Circle((cx, cy), r, fill=False, linestyle="-", color='black')
        ax.add_artist(circle)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axis('off')
    ax.margins(0)
    # ax.patch.set_facecolor("#faf4ed")
    fig.patch.set_facecolor("#faf4ed")
    # fig.patch.set_alpha(0.)
    fig.tight_layout(pad=0)
    canvas.draw()
    buf = canvas.buffer_rgba()
    array = np.asarray(buf)
    arrays.append(array)
    plt.close(fig)

imwrite(rootdir / "moire.gif", arrays, loop=0)
