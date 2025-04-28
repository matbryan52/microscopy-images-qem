import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from skimage.io import imread
from skimage.measure import label, regionprops
from skimage.segmentation import clear_border
from skimage.morphology import binary_closing, disk, binary_erosion, binary_dilation, binary_opening, skeletonize, remove_small_objects, remove_small_holes
from bokeh.models import ColumnDataSource, ImageRGBA, Quad
from bokeh.events import Tap
from bokeh.models.glyphs import VSpan
from skimage.color import label2rgb
import pathlib
rootdir = pathlib.Path(__file__).parent

pn.extension('floatpanel')
custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}

img1 = imread(rootdir.parent / "binary-particles.png", as_gray=True).astype(np.float32)
vmin, vmax = img1.min(), img1.max()

img1 = img1 > 0.5
img1_base = img1.copy()

frame_height = 450
fig1 = (
    ApertureFigure
    .new(
        img1.astype(np.float32),
        title="Mask",
        tools=False,
        maxdim=frame_height,
        downsampling=False,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None

common_kwargs = dict(width=100, button_type="primary", margin=(3, 3), styles=custom_style)
reset_btn = pn.widgets.Button(name="Reset", **common_kwargs)
reset_btn.button_type = "warning"
erode_btn = pn.widgets.Button(name="Erode", **common_kwargs)
dilate_btn = pn.widgets.Button(name="Dilate", **common_kwargs)
close_btn = pn.widgets.Button(name="Close", **common_kwargs)
open_btn = pn.widgets.Button(name="Open", **common_kwargs)
skel_btn = pn.widgets.Button(name="Skeletonize", **common_kwargs)
common_kwargs["width"] = 150
remove_small_btn = pn.widgets.Button(name="Remove small regions", **common_kwargs)
fill_small_btn = pn.widgets.Button(name="Fill small holes", **common_kwargs)

def reset(*e):
    global img1
    img1 = img1_base.copy()
    fig1.update(img1)

def run_opt(fn, size):
    global img1
    img1 = fn(img1, disk(size))
    fig1.update(img1.astype(np.float32))

def erode(*e):
    run_opt(binary_erosion, 1)

def dilate(*e):
    run_opt(binary_dilation, 1)

def open(*e):
    run_opt(binary_opening, 1)

def close(*e):
    run_opt(binary_closing, 1)

def skeleton(*e):
    global img1
    img1 = skeletonize(img1)
    fig1.update(img1.astype(np.float32))

def remove_small(*e):
    global img1
    img1 = remove_small_objects(img1, min_size=16)
    fig1.update(img1.astype(np.float32))

def fill_small(*e):
    global img1
    img1 = remove_small_holes(img1, area_threshold=32)
    fig1.update(img1.astype(np.float32))

reset_btn.on_click(reset)
erode_btn.on_click(erode)
dilate_btn.on_click(dilate)
open_btn.on_click(open)
close_btn.on_click(close)
skel_btn.on_click(skeleton)
remove_small_btn.on_click(remove_small)
fill_small_btn.on_click(fill_small)


fig1.layout.insert(
    0, pn.Row(reset_btn, skel_btn, remove_small_btn)
)
fig1._toolbar.extend((
    erode_btn,
    dilate_btn,
    fill_small_btn,
))

pn.Row(
    fig1.layout,
    align="center",
).servable("morphological")
