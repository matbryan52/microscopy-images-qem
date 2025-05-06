import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from skimage.io import imread
from libertem_ui.figure import ApertureFigure
from libertem_ui.applications.image_transformer import ImageTransformer
from libertem_ui.display.display_base import PointSet
from scipy.interpolate import RegularGridInterpolator

custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}

pn.extension('floatpanel')

img1 = np.load(rootdir / "moire-atoms.npz")["image"]
sy, sx = img1.shape
sampling = 0.2498
unit_cell = 2.716
xvals = np.arange(sx) * sampling
yvals = np.arange(sy) * sampling
interpolator = RegularGridInterpolator((yvals, xvals), img1, method='linear', bounds_error=False, fill_value=0.)
cell_mult = 1.1
sample_period = unit_cell * cell_mult
x_samples = np.arange(np.floor(xvals.max() / sample_period)) * sample_period
y_samples = np.arange(np.floor(yvals.max() / sample_period)) * sample_period
(xx, yy) = np.meshgrid(x_samples, y_samples)
s_yvals, s_xvals = yy.ravel(), xx.ravel()
sampled_image = interpolator((yy, xx))

fig1 = (
    ApertureFigure
    .new(
        img1,
        title=f"True signal {img1.shape}",
        maxdim=450,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.

pointset = (
    PointSet
    .new()
    .from_vectors(
        s_xvals / sampling, s_yvals / sampling
    )
    .on(fig1.fig)
)
pointset.points.marker = "x"
pointset.points.line_color = "red"
pointset.points.size = 6
pointset.points.fill_color = "red"
pointset.set_visible(False)

fig2 = (
    ApertureFigure
    .new(
        sampled_image,
        title=f"Sampled image {sampled_image.shape}",
        maxdim=450,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.

sampling_slider = pn.widgets.FloatSlider(
    name="Sampling (/ unit-cell)",
    start=1.,
    end=3.,
    step=0.01,
    value=cell_mult,
    styles=custom_style,
)

def resample_image(*e):
    cell_mult = sampling_slider.value
    xvals = np.arange(sx) * sampling
    yvals = np.arange(sy) * sampling
    sample_period = unit_cell * cell_mult
    x_samples = np.arange(np.floor(xvals.max() / sample_period)) * sample_period
    y_samples = np.arange(np.floor(yvals.max() / sample_period)) * sample_period
    (xx, yy) = np.meshgrid(x_samples, y_samples)
    s_yvals, s_xvals = yy.ravel(), xx.ravel()
    sampled_image = interpolator((yy, xx))
    fig2.update(sampled_image)
    fig2.fig.title.text = f"Sampled image {sampled_image.shape}"
    pointset.update(
        s_xvals / sampling, s_yvals / sampling
    )

sampling_slider.param.watch(resample_image, "value_throttled")

hide_grid_toggle = pn.widgets.Toggle(
    name="Hide grid",
    button_type="primary",
    styles=custom_style,
    value=True,
)

def hide_grid(e):
    hide = e.new
    pointset.set_visible(not hide)

hide_grid_toggle.param.watch(hide_grid, "value")


fig1._toolbar.append(hide_grid_toggle)
fig2._toolbar.append(sampling_slider)

pn.Column(
    pn.Row(
        fig1.layout,
        pn.layout.HSpacer(max_width=50),
        fig2.layout,
        align="center",
        sizing_mode="stretch_both",
    )
).servable("stem-moire")
