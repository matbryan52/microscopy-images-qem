import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from imageio.v3 import imwrite
from skimage.transform import AffineTransform
from matplotlib.backends.backend_agg import FigureCanvasAgg

import pathlib
rootdir = pathlib.Path(__file__).parent

import tempfile

lines = 30
cx = 0
cy = 0
xlim = 75
ylim = 90
offset = 50
hlength = 75
arrays = []
num_frames = 61
for angle in 0.15 * np.sin(2 * np.pi * np.linspace(0, 1, num=num_frames)):
    fig, ax = plt.subplots(figsize=(4, 4), dpi=220)
    canvas = FigureCanvasAgg(fig)
    for dx in np.linspace(-offset, offset, num=lines, endpoint=True):
        line = Line2D((cx + dx, cx + dx), (cy - hlength, cy + hlength), linestyle="-", color='black')
        ax.add_artist(line)
        transform = AffineTransform(rotation=angle)
        xx1, yy1, _ = transform.params @ [
            line.get_xdata(True)[0], 
            line.get_ydata(True)[0],
            1
        ]
        xx2, yy2, _ = transform.params @ [
            line.get_xdata(True)[1], 
            line.get_ydata(True)[1],
            1
        ]        
        line = Line2D(
            (xx1, xx2),
            (yy1, yy2),
            linestyle="-",
            color='black'
        )
        ax.add_artist(line)
    ax.set_xlim(-xlim, xlim)
    ax.set_ylim(-ylim, ylim)
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

imwrite(rootdir / "moire-lines.gif", arrays, loop=0)
