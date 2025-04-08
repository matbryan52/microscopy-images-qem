import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from skimage.io import imread
from libertem_ui.figure import ApertureFigure
from libertem_ui.applications.image_transformer import ImageTransformer
from libertem_ui.display.display_base import PointSet
from scipy.interpolate import RegularGridInterpolator

pn.extension('floatpanel')

img1 = imread(rootdir / "si-karlik.png", as_gray=True)
# it = ImageTransformer(img1)
# it.rotate_about_center(rotation_degrees=-13)
# img1 = it.get_transformed_image()
sy, sx = img1.shape
xvals = np.arange(sx)
yvals = np.arange(sy)
interpolator = RegularGridInterpolator((yvals, xvals), img1, method='linear', bounds_error=False, fill_value=0.)
sample_period = 15.3
x_samples = sx / sample_period
y_samples = np.ceil(x_samples * (sy / sx)).astype(int)
x_samples = np.ceil(x_samples).astype(int)
s_xvals_lin = np.linspace(0, sx - 1, num=x_samples, endpoint=True)
s_yvals_lin = np.linspace(0, sy - 1, num=y_samples, endpoint=True)
(xx, yy) = np.meshgrid(s_xvals_lin, s_yvals_lin)
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
        s_xvals, s_yvals
    )
    .on(fig1.fig)
)
pointset.points.marker = "x"
pointset.points.line_color = "red"
pointset.points.size = 6
pointset.points.fill_color = "red"

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
    name="Sample period",
    start=4,
    end=20,
    step=0.1,
    value=sample_period,
)

def resample_image(*e):
    sample_period = sampling_slider.value
    x_samples = sx / sample_period
    y_samples = np.ceil(x_samples * (sy / sx)).astype(int)
    x_samples = np.ceil(x_samples).astype(int)
    s_xvals_lin = np.linspace(0, sx - 1, num=x_samples, endpoint=True)
    s_yvals_lin = np.linspace(0, sy - 1, num=y_samples, endpoint=True)
    (xx, yy) = np.meshgrid(s_xvals_lin, s_yvals_lin)
    s_yvals, s_xvals = yy.ravel(), xx.ravel()
    sampled_image = interpolator((yy, xx))
    fig2.update(sampled_image)
    fig2.fig.title.text = f"Sampled image {sampled_image.shape}"
    pointset.update(
        s_xvals, s_yvals
    )

sampling_slider.param.watch(resample_image, "value_throttled")

hide_grid_toggle = pn.widgets.Toggle(
    name="Hide grid",
    button_type="primary",
)

def hide_grid(e):
    hide = e.new
    pointset.set_visible(not hide)

hide_grid_toggle.param.watch(hide_grid, "value")


fig1._toolbar.append(hide_grid_toggle)
fig2._toolbar.append(sampling_slider)
fig1.layout.append(
    pn.widgets.StaticText(value="Karlík M., Materials Structure, vol. 8, number 1 (2001)")
)

pn.Column(
    # pn.Row(hide_grid_toggle, sampling_slider),
    pn.Row(
        fig1.layout,
        pn.layout.HSpacer(max_width=50),
        fig2.layout,
        align="center",
        sizing_mode="stretch_both",
    )
).servable("stem-moire")
