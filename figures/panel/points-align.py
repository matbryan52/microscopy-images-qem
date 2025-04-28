import pathlib
import numpy as np
import panel as pn
import matplotlib.pyplot as plt
rootdir = pathlib.Path(__file__).parent.parent
from skimage.io import imread
custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}

from libertem_ui.applications.image_utils import point_registration


crop = np.s_[450:850, 350:750]
shifty, shiftx = 0, 0
crop2 = np.s_[450 + shifty:850 + shifty, 350 + shiftx:750 + shiftx]
img1 = imread(rootdir / "ADF-00011.png", as_gray=True)[crop]
img2 = imread(rootdir / "ADF-00021.png", as_gray=True)[crop2]

layout, getter = point_registration(img1, img2)

for el in layout[0]:
    layout.styles = custom_style

layout[-1][0][-1].object.background_fill_alpha = 0.
layout[-1][0][-1].object.border_fill_color = None
layout[-1][1][-1].object.background_fill_alpha = 0.
layout[-1][1][-1].object.border_fill_color = None
layout[-1].insert(1, pn.HSpacer(max_width=50))

layout.servable("points-align")
