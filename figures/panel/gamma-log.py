import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from libertem_ui.display.display_base import Curve
import pathlib
rootdir = pathlib.Path(__file__).parent

pn.extension('floatpanel')

custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}


img1 = (
    np.load(rootdir.parent / "Image 10012.npy")
    .astype(np.float32)
) ** 1.25

# img1 /= img1.max()
img1 += 1.
min_lin, max_lin = img1.min(), img1.max()

log_img = np.log10(img1)
min_log, max_log = log_img.min(), log_img.max()

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
data_vals_log = np.log10((data_vals_norm * 1000) + 1)
data_vals_log -= data_vals_log.min()
data_vals_log /= data_vals_log.max()
data_vals_log *= 255

bins = np.linspace(*(fig1.im.current_minmax), 50)
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


map_type = pn.widgets.RadioButtonGroup(
    name='Mapping',
    value="Log",
    options=["Linear", "Gamma", "Log"],
    button_type="success",
    styles=custom_style,
)

gamma = pn.widgets.FloatSlider(
    name="Gamma",
    start=-0.99,
    end=2.,
    step=0.05,
    value=0.8,
    disabled=True,
    styles=custom_style,
)
gamma_btn = pn.widgets.Button(
    name="Reset",
    button_type="primary",
    disabled=True,
    styles=custom_style,
)

def reset_gamma(*e):
    gamma.value = 0.
    gamma.value_throttled = 0.

gamma_btn.on_click(reset_gamma)

cmap_select = fig1.im.color.get_cmap_select()

def _set_vminmax(*e):
    selected = map_type.value
    if selected == "Linear":
        fig1.im.update(img1)
        fig1.im.color._lin_mapper.update(
            low=min_lin, high=max_lin
        )
        curve.update(xvals=data_vals, yvals=np.arange(num_pts))
        return
    elif selected == "Log":
        fig1.im.update(log_img)
        fig1.im.color._lin_mapper.update(
            low=min_log, high=max_log
        )
        curve.update(xvals=data_vals, yvals=data_vals_log)
        return
    # Gamma
    gval = gamma.value + 1
    gval = 1 / gval
    new_img = img1 ** gval
    fig1.im.update(new_img)
    low, high = fig1.im.current_minmax
    fig1.im.color._lin_mapper.update(
        low=low, high=high
    )
    scaling = data_vals_norm ** gval
    mapped = np.clip(scaling  * 255, 0, 255)
    curve.update(xvals=data_vals, yvals=mapped)

gamma.param.watch(_set_vminmax, "value_throttled")


def switch_type(*e):
    selected = map_type.value
    is_gamma = selected == "Gamma"
    gamma.disabled = not is_gamma
    gamma_btn.disabled = not is_gamma
    _set_vminmax()

switch_type()
map_type.param.watch(
    switch_type,
    "value",
)

fig1._outer_toolbar.height = 0

pn.Row(
    fig1.layout,
    pn.HSpacer(width=20),    
    pn.Column(
        # cmap_select,
        pn.pane.Bokeh(fig2),
        pn.Row(map_type, gamma, gamma_btn),
    )
).servable("colour-map")
