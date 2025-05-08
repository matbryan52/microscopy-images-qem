import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from libertem_ui.display.display_base import Curve
from skimage.io import imread
import pathlib
rootdir = pathlib.Path(__file__).parent

pn.extension('floatpanel')

custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}


img1 = imread(rootdir.parent / "overview_100K-binned.jpg", as_gray=True).astype(np.float32)

fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Image",
        tools=False,
        maxdim=375,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.im.color.add_colorbar(width=20)
fig1.fig.right[0].background_fill_alpha = 0.


fig2 = figure(title='Value-to-Colour')
fig2.frame_height = 300
fig2.background_fill_alpha = 0.
fig2.border_fill_color = None
fig2.x_range.range_padding = 0.
fig2.y_range.range_padding = 0.
fig2.xaxis.axis_label = "Data value"
fig2.yaxis.axis_label = "Colourmap index"
fig2.y_range.start = 0
fig2.y_range.end = 255

num_pts = 255
data_vals = np.linspace(*(fig1.im.current_minmax), num=num_pts, endpoint=True)
data_vals_norm = (data_vals - data_vals.min()) / (data_vals.max() - data_vals.min())

bins = np.linspace(*(fig1.im.current_minmax), 30)
hist, edges = np.histogram(img1.ravel(), density=True, bins=bins)
hist /= hist.max()
hist *= 240.
fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
         fill_color="skyblue", line_color="white")

curve = (
    Curve
    .new()
    .from_vectors(
        data_vals,
        np.arange(num_pts),
    )
    .on(fig2)
)

brightness = pn.widgets.FloatSlider(
    name="Brightness",
    start=0.01,
    end=0.99,
    step=0.01,
    value=0.5,
    width=200,
    styles=custom_style,
)

brightness_btn = pn.widgets.Button(
    name="Reset",
    button_type="primary",
    styles=custom_style
)

contrast = pn.widgets.FloatSlider(
    name="Contrast",
    start=0.01,
    end=0.99,
    step=0.01,
    value=0.75,
    width=200,
)
reset_btn = pn.widgets.Button(
    name="Reset",
    button_type="primary",
    styles=custom_style
)

def _set_vminmax(*e):
    cmin, cmax = fig1.im.current_minmax
    crange = cmax - cmin
    bval = brightness.value
    cval = contrast.value
    bright_shift = ((bval - 0.5) * 2 * crange)
    contrast_shift = (cval - 0.5) * crange
    low = cmin - bright_shift + contrast_shift
    high = cmax - bright_shift - contrast_shift
    fig1.im.color._lin_mapper.update(
        low=low, high=high
    )
    mapped = 0.5 + ((cval + 0.5) * (data_vals_norm - 0.5)) - ((0.5 - bval) * 2)
    # mapped = (2 * cval) * data_vals_norm + 2 * (bval - 0.5) - (cval - 0.5)
    mapped = np.clip(mapped  * 255, 0, 255)
    curve.update(xvals=data_vals, yvals=mapped)

def reset(*e):
    brightness.value = 0.5
    contrast.value = 0.5
    _set_vminmax()

_set_vminmax()

reset_btn.on_click(reset)

brightness.param.watch(_set_vminmax, "value_throttled")
contrast.param.watch(_set_vminmax, "value_throttled")

fig1._outer_toolbar.height = 0

pn.Row(
    pn.Column(
        fig1.layout,

    ),
    pn.HSpacer(width=20),
    pn.Column(
        pn.pane.Bokeh(fig2, align='end'),
        pn.Row(brightness, contrast, reset_btn, align='end'),
    ),
    align='end'
).servable("brightness-contrast")
