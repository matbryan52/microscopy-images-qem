import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from skimage.io import imread
from libertem_ui.figure import ApertureFigure
from libertem_ui.utils import get_initial_pos
from libertem_ui.display.display_base import RingSet, DiskSet 
from bokeh.models import LinearAxis, Range1d
from skimage.filters import median

pn.extension('floatpanel')

shape = (32, 32)
hy, hx = np.asarray(shape) // 2
# img1 = imread(rootdir / "AlN_2D_sousGaNx6M.tif", as_gray=True)
# img1 = img1[:512, :512]
img1 = imread(rootdir / "tiled-roofing-new-roof.jpg", as_gray=True)
img1_fft = np.fft.fftshift(np.fft.fft2(img1))

initial_mode = "Low-pass"

fig1 = (
    ApertureFigure
    .new(
        np.log(img1_fft),
        title=f"FFT - {initial_mode}",
        maxdim=400,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.

fig1.fig.xaxis.axis_label = "u"
fig1.fig.yaxis.axis_label = "v"
fig1.fig.x_range.bounds = (0, img1_fft.shape[1])
fig1.fig.y_range.bounds = (0, img1_fft.shape[0])

view_text = fig1._toolbar.pop(0)
view_select = fig1._toolbar.pop(0)
fig1._outer_toolbar.height = 0

fig2 = (
    ApertureFigure
    .new(
        img1,
        title='Filtered image',
        maxdim=400,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.

fig2.fig.xaxis.axis_label = "x"
fig2.fig.yaxis.axis_label = "y"

fig2._outer_toolbar.height = 0


(cy, cx), (ri, ro), max_dim = get_initial_pos(img1_fft.shape)
ri = 50
ro = 150
ring_db = (
    RingSet
    .new()
    .from_vectors(
        x=[cx],
        y=[cy],
        inner_radius=ro,
        outer_radius=2 * max(img1.shape),
    )
    .on(fig1.fig)
    # .set_visible(True)
)
disk_db = (
    DiskSet
    .new()
    .from_vectors(
        x=[cx],
        y=[cy],
        radius=ri,
    )
    .on(fig1.fig)
    .set_visible(False)
)
ring_db.rings.line_alpha = 0.
ring_db.rings.fill_alpha = 1.
ring_db.rings.fill_color = "black"
disk_db.disks.line_alpha = 0.
disk_db.disks.fill_alpha = 1.
disk_db.disks.fill_color = "black"

mode_selector = pn.widgets.RadioButtonGroup(
    name='Filter mode',
    value=initial_mode,
    options=["Low-pass", "High-pass", "Band-pass"],
    button_type='primary',
)

radius_slider = pn.widgets.FloatSlider(
    name='Disk radius',
    value=ro,
    start=1.,
    end=max_dim,
    step=1.,
    width=250,
)

radii_slider = pn.widgets.RangeSlider(
    name='Annulus radii',
    value=(ri, ro),
    start=1.,
    end=max_dim,
    visible=False,
    step=1.,
    width=250,
)


mask = np.ones(img1_fft.shape, dtype=np.float32)
h, w = img1_fft.shape
ycoords = np.linspace(-h / 2, h / 2, num=h).tolist()
xcoords = np.linspace(-w / 2, w / 2, num=w).tolist()
radius = np.linalg.norm(np.stack(np.meshgrid(xcoords, ycoords), axis=0), axis=0)


def _update_image(*e):
    mode = mode_selector.value
    if mode == "High-pass":
        mask = radius > radius_slider.value
    elif mode == "Low-pass":
        mask = radius < radius_slider.value
    elif mode == "Band-pass":
        mask = np.logical_and(
            radius > radii_slider.value[0],
            radius < radii_slider.value[1],
        )
    mask = median(mask.astype(np.float32))
    fig2.update(
        np.fft.ifft2(np.fft.ifftshift(img1_fft * mask)).real
    )


def change_vis(e):
    if e.new == "High-pass":
        ring_db.set_visible(False)
        disk_db.set_visible(True)
        radius_slider.visible = True
        radii_slider.visible = False
        disk_db.update(radius=radius_slider.value)
        fig1.fig.title.text = "FFT - High-Pass"
        _update_image()
    elif e.new == "Band-pass":
        ring_db.set_visible(True)
        disk_db.set_visible(True)
        radius_slider.visible = False
        radii_slider.visible = True
        ring_db.update(inner_radius=radii_slider.value[1])
        disk_db.update(radius=radii_slider.value[0])
        fig1.fig.title.text = "FFT - Band-Pass"
        _update_image()
    elif e.new == "Low-pass":
        ring_db.set_visible(True)
        disk_db.set_visible(False)
        radius_slider.visible = True
        radii_slider.visible = False
        ring_db.update(inner_radius=radii_slider.value[0])
        fig1.fig.title.text = "FFT - Low-Pass"
        _update_image()


mode_selector.param.watch(change_vis, "value")


def update_radius(e):
    r = e.new
    mode = mode_selector.value
    if mode == "High-pass":
        disk_db.update(radius=r)
    elif mode == "Low-pass":
        ring_db.update(inner_radius=r)
    _update_image()


def update_radii(e):
    r0, r1 = e.new
    disk_db.update(radius=r0)
    ring_db.update(inner_radius=r1)
    _update_image()


radius_slider.param.watch(update_radius, 'value_throttled')
radii_slider.param.watch(update_radii, 'value_throttled')


pn.Column(
    pn.Row(mode_selector, radius_slider, radii_slider),
    pn.Row(
        fig1.layout,
        pn.layout.HSpacer(max_width=50),
        fig2.layout,
        align="center",
        # sizing_mode="stretch_both",
    )
).servable("fourier-filtering")
