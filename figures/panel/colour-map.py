import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from libertem_ui.display.display_base import Curve

pn.extension('floatpanel')


img1 = np.random.uniform(size=(128, 128)).astype(np.float32)
img1 *= 5.

fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Image",
        tools=False,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.im.color.add_colorbar(width=20)
fig1.fig.right[0].background_fill_alpha = 0.


fig2 = figure(title='Value-to-Colour')
fig2.frame_height = 325
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
    value=0.5
)
brightness_btn = pn.widgets.Button(name="Reset", button_type="primary")

def reset_brightness(*e):
    brightness.value = 0.5

brightness_btn.on_click(reset_brightness)

contrast = pn.widgets.FloatSlider(
    name="Contrast",
    start=0.01,
    end=0.99,
    step=0.01,
    value=0.5
)
contrast_btn = pn.widgets.Button(name="Reset", button_type="primary")

def reset_contrast(*e):
    contrast.value = 0.5

contrast_btn.on_click(reset_contrast)

cmap_select = fig1.im.color.get_cmap_select()

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
    mapped = 0.5 + ((cval + 0.5) * (data_vals_norm - 0.5)) - ((bval - 0.5) * 2)
    mapped = np.clip(mapped  * 255, 0, 255)
    curve.update(xvals=data_vals, yvals=mapped)

brightness.param.watch(_set_vminmax, "value")
contrast.param.watch(_set_vminmax, "value")

pn.Row(
    fig1.layout,
    pn.Column(
        cmap_select,
        pn.Row(brightness, brightness_btn),
        pn.Row(contrast, contrast_btn),
        pn.pane.Bokeh(fig2),
    )
).servable("colour-map")
