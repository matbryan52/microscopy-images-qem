import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import Cursor
from bokeh.models import LinearAxis, Range1d

pn.extension('floatpanel')

shape = (32, 32)
hy, hx = np.asarray(shape) // 2
out_shape = (128, 128)
img1 = np.zeros(shape, dtype=np.complex128)
img1_fft = np.zeros(shape[:1] + (shape[1] // 2 + 1,), dtype=np.complex128)

fig1 = (
    ApertureFigure
    .new(
        img1,
        title="FFT",
        maxdim=400,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.

fig1.fig.xaxis.axis_label = "u"
fig1.fig.yaxis.axis_label = "v"

# fig1.fig.extra_x_ranges['freqx'] = Range1d(-1 / hx, 1 / hx)
# ax2 = LinearAxis(
#     axis_label="X-Freq (1 / px)",
#     x_range_name='freqx',
# )
# fig1.fig.add_layout(ax2, 'below')

# fig1.fig.extra_y_ranges['freqy'] = Range1d(1 / hy, -1 / hy)
# ax3 = LinearAxis(
#     axis_label="Y-Freq (1 / px)",
#     y_range_name='freqy',
# )
# fig1.fig.add_layout(ax3, 'left')

# img2 = np.zeros(out_shape, dtype=np.float32)
img2 = np.fft.irfft2(img1_fft, s=out_shape).astype(np.float32)

fig2 = (
    ApertureFigure
    .new(
        img2,
        title='Image',
        maxdim=400,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.


fig2.fig.xaxis.axis_label = "x"
fig2.fig.yaxis.axis_label = "y"


period_slider = pn.widgets.IntSlider(value=2, start=2, end=16, name="Frequency")
angle_slider = pn.widgets.FloatSlider(value=0, start=0, end=90, step=5, name="Angle (deg)")
cos_sin = pn.widgets.RadioBoxGroup(value="sin()", options=["sin()", "cos()"], name="Component")


def _rfft2_to_fft2shifted(img):
    shifted = np.fft.fftshift(img, axes=0)
    return np.concatenate(
        (
            np.conjugate(np.flipud(np.fliplr(shifted[:, 1:]))),
            shifted,
        ),
        axis=1,
    )


extra_img = np.zeros_like(img1_fft)

def _current_component():
    global extra_img
    period = period_slider.value
    angle = np.deg2rad(angle_slider.value)
    component = 1 if cos_sin.value == "cos()" else 1j
    xidx = np.round(period * np.cos(angle)).astype(int)
    yidx = np.round(period * np.sin(angle)).astype(int)
    extra_img[:] = 0 + 0j
    extra_img[yidx, xidx] += component


def _live_version(*e):
    _current_component()
    fig1.update(_rfft2_to_fft2shifted(img1_fft + extra_img))
    fig2.update(np.fft.irfft2(img1_fft + extra_img, s=out_shape).astype(np.float32))

period_slider.param.watch(_live_version, "value")
angle_slider.param.watch(_live_version, "value")
cos_sin.param.watch(_live_version, "value")


def add_fft(*e):
    global img1_fft
    _current_component()
    img1_fft += extra_img
    fig1.update(_rfft2_to_fft2shifted(img1_fft))
    fig2.update(np.fft.irfft2(img1_fft, s=out_shape).astype(np.float32))


def clear_fft(*e):
    global img1_fft
    img1_fft[:] = 0 + 0j
    _live_version()


def add_dc(*e):
    global img1_fft
    img1_fft[0, 0] += 1 + 0j
    _live_version()


increase_level_btn = pn.widgets.Button(name="Add DC")
increase_level_btn.on_click(add_dc)

add_btn = pn.widgets.Button(name="Store")
add_btn.on_click(add_fft)

clear_btn = pn.widgets.Button(name="Clear")
clear_btn.on_click(clear_fft)

pn.Column(
    pn.Row(period_slider, cos_sin, angle_slider, add_btn, clear_btn, increase_level_btn),
    pn.Row(
        fig1.layout,
        pn.layout.HSpacer(max_width=50),
        fig2.layout,
        align="center",
        sizing_mode="stretch_both",
    )
).servable("fourier-image")
