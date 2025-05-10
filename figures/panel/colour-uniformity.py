import panel as pn
import numpy as np
from bokeh.plotting import figure
import colorcet as cc
from matplotlib import colormaps
from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import Curve

pn.extension('floatpanel')
custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}

shape = (256 // 5, 256)


def to_hex(array):
    hexvals = []
    for row in array:
        hexvals.append("#" + row.tobytes().hex().upper())
    return hexvals


from libertem_ui.utils.colormaps import image_colormaps
hot = colormaps["hot"].resampled(256)(np.linspace(0, 1, num=256, endpoint=True), bytes=True)[...,:3]
image_colormaps["Hot"] = to_hex(hot)
image_colormaps["Fire"] = cc.fire
image_colormaps["Cyclic MYBM"] = to_hex((np.asarray(cc.cyclic_mybm_20_100_c48) * 255).astype(np.uint8))


def linear_ramp(shape):
    h, w = shape
    coord = np.linspace(0, 1., num=w, endpoint=True)
    return np.tile(coord[np.newaxis, :], (h, 1))


def gaussian(shape):
    h, w = shape
    coord = np.linspace(-1., 1., num=w, endpoint=True)
    gauss = np.exp(-1 * coord**2 / 0.1)
    return np.tile(gauss[np.newaxis, :], (h, 1))


def cosine(shape):
    h, w = shape
    coord = np.linspace(-2 * np.pi, 2 * np.pi, num=w, endpoint=True)
    cos = np.cos(coord)
    return np.tile(cos[np.newaxis, :], (h, 1))


def asymmetric(shape):
    h, w = shape
    coord = np.linspace(-1., 1., num=w, endpoint=True)
    profile = np.exp(-1 * (coord - 0.3)**2 / 0.05)
    profile -= 0.5 * np.exp(-1 * (coord + 0.5)**2 / 0.02)
    return np.tile(profile[np.newaxis, :], (h, 1))


def comb(image):
    h, w = image.shape
    coord = np.linspace(0, 40 * 2 * np.pi, num=w, endpoint=True)
    sin_coord = np.sin(coord)
    sin_image = np.tile(sin_coord[np.newaxis, :], (h, 1))
    sin_intensity = 0.05 * (np.linspace(1, 0, num=h, endpoint=True) ** 2.5)
    sin_image *= sin_intensity[:, np.newaxis]
    vmin = image.min()
    vmax = image.max()
    return np.clip(image + sin_image, vmin, vmax)


def phase(shape):
    h, w = shape
    coord = np.linspace(-6 * np.pi, 6 * np.pi, num=w, endpoint=True)
    phase = np.angle(np.exp(1j * coord))
    return np.tile(phase[np.newaxis, :], (h, 1))


signals = {
    "Ramp": linear_ramp(shape),
    "Ramp + Comb": comb(linear_ramp(shape)),
    "Gaussian": gaussian(shape),
    "Cosine": cosine(shape),
    "Asymmetric": asymmetric(shape),
    "Phase": phase(shape),
}


selected = "Ramp"
img1 = signals[selected]
fig1 = (
    ApertureFigure
    .new(
        img1,
        title=selected,
        maxdim=500,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.
fig1.fig.right[0].width = 25
fig1._outer_toolbar.height = 0
fig1.im.color.change_cmap("Spectrum")
fig1.fig.toolbar_location=None


fig2 = figure(title="Signal")

yvals = signals[selected][0]
xvals = np.arange(yvals.size)
curve = (
    Curve
    .new()
    .from_vectors(
        xvals,
        yvals,
    )
    .on(fig2)
)
fig2.frame_width = fig1.fig.frame_width
fig2.frame_height = int(fig1.fig.frame_height * 0.8)
fig2.toolbar_location = "below"
fig2.background_fill_alpha = 0.
fig2.border_fill_color = None
fig2.toolbar_location=None
fig1.fig.below.pop(-1)


data_select = pn.widgets.RadioButtonGroup(
    name='Radio Button Group',
    value=selected,
    options=[*signals.keys()],
    button_type='success',
    styles=custom_style,
)


fig3 = (
    ApertureFigure
    .new(
        img1,
        title=selected,
        maxdim=500,
    )
)
fig3.fig.toolbar_location = "below"
fig3.fig.background_fill_alpha = 0.
fig3.fig.border_fill_color = None
fig3.fig.right[0].background_fill_alpha = 0.
fig3.fig.right[0].width = 25
fig3._outer_toolbar.height = 0
fig3.im.color.change_cmap("Temperature")
fig3.fig.toolbar_location=None
fig3.fig.below.pop(-1)


def _change_image(*e):
    selected = data_select.value
    fig1.fig.title.text = selected
    fig1.update(signals[selected])
    fig3.fig.title.text = selected
    fig3.update(signals[selected])
    yvals = signals[selected][0]
    curve.update(xvals=xvals, yvals=yvals)

data_select.param.watch(_change_image, "value")


tools1 = tuple(fig1._floatpanels.values())[0]['items']
cmap = tools1[0][0]
cmap.options.pop(cmap.options.index("Reds"))
cmap.options.pop(cmap.options.index("Greens"))
cmap.options.pop(cmap.options.index("Blues"))
cmap.options.pop(cmap.options.index("Oranges"))
cmap.options.pop(cmap.options.index("Cividis"))
cmap.options.pop(cmap.options.index("Cyclic Isoluminant"))
tools1[-2].align = "end"
tools1[-2].width = 200
tools1[-1].align = "end"
tools1[-1].width = 200
tools1[1][1].align = "end"
tools2 = tuple(fig3._floatpanels.values())[0]['items']
cmap2 = tools2[0][0]
cmap2.options.pop(cmap2.options.index("Reds"))
cmap2.options.pop(cmap2.options.index("Greens"))
cmap2.options.pop(cmap2.options.index("Blues"))
cmap2.options.pop(cmap2.options.index("Oranges"))
cmap2.options.pop(cmap2.options.index("Cividis"))
cmap2.options.pop(cmap2.options.index("Cyclic Isoluminant"))
tools2[-2].align = "end"
tools2[-2].width = 200
tools2[-1].align = "end"
tools2[-1].width = 200
tools2[1][1].align = "end"

pn.Column(
    data_select,
    pn.pane.Bokeh(fig2),
    pn.Row(tools1[0][0], tools1[1][1],tools1[-2], tools1[-1], margin=(0, 0)),
    fig1.layout,
    pn.Row(tools2[0][0], tools2[1][1],tools2[-2], tools2[-1], margin=(0, 0)),
    fig3.layout,
).servable("colour-uniformity")
