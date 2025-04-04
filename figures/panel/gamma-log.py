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
data_vals_log = np.log(data_vals_norm + 1)
data_vals_log /= data_vals_log.max()
data_vals_log *= 255
curve = (
    Curve
    .new()
    .from_vectors(
        data_vals,
        np.arange(num_pts),
    )
    .on(fig2)
)


map_type = pn.widgets.RadioButtonGroup(
    name='Mapping',
    value="Linear",
    options=["Linear", "Gamma", "Log"],
    button_type="success",
)

gamma = pn.widgets.FloatSlider(
    name="Gamma",
    start=-1.,
    end=1.,
    step=0.05,
    value=0,
    disabled=True,
)
gamma_btn = pn.widgets.Button(
    name="Reset",
    button_type="primary",
    disabled=True,
)

def reset_gamma(*e):
    gamma.value = 1.

gamma_btn.on_click(reset_gamma)

cmap_select = fig1.im.color.get_cmap_select()

def _set_vminmax(*e):
    selected = map_type.value
    if selected == "Linear":
        fig1.im.update(img1)
        curve.update(xvals=data_vals, yvals=np.arange(num_pts))
        return
    elif selected == "Log":
        fig1.im.update(np.log(img1+0.1))
        curve.update(xvals=data_vals, yvals=data_vals_log)
        return
    # Gamma
    gval = gamma.value
    positive = gval >= 0
    if positive:
        gval = 1 / (1 + gval)
    else:
        gval = 1 + gval
    fig1.im.update(img1 ** gval)
    scaling = data_vals_norm ** gval
    mapped = np.clip(scaling  * 255, 0, 255)
    curve.update(xvals=data_vals, yvals=mapped)

gamma.param.watch(_set_vminmax, "value")


def switch_type(*e):
    selected = map_type.value
    is_gamma = selected == "Gamma"
    gamma.disabled = not is_gamma
    gamma_btn.disabled = not is_gamma
    _set_vminmax()

map_type.param.watch(
    switch_type,
    "value",
)


pn.Row(
    fig1.layout,
    pn.Column(
        cmap_select,
        map_type,
        pn.Row(gamma, gamma_btn),
        pn.pane.Bokeh(fig2),
    )
).servable("colour-map")
