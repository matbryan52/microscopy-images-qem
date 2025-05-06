import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from scipy.ndimage import fourier_shift
from skimage.filters import gaussian

pn.extension('floatpanel')

custom_style = {
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}


hw = 24
coords = np.linspace(-hw, hw, num=2 * hw, endpoint=True)
coords = np.stack(np.meshgrid(coords, coords), axis=0)
radii = (np.linalg.norm(coords, axis=0) < (hw / 3.)).astype(np.float32)
radii = gaussian(radii, sigma=0.75)
img1 = radii.copy()
radii_fft = np.fft.fft2(radii)

fig1 = (
    ApertureFigure
    .new(
        img1,
        title='Fourier-shifted',
        maxdim=450,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right.pop(0)

xshift_s = pn.widgets.FloatSlider(
    name="X-Shift (px)",
    start=-hw / 2.,
    end=hw / 2.,
    value=0.,
    step=0.1,
    styles=custom_style,
    width=135,
)
yshift_s = pn.widgets.FloatSlider(
    name="Y-Shift (px)",
    start=-hw / 2.,
    end=hw / 2.,
    value=0.,
    step=0.1,
    styles=custom_style,
    width=135,
)
clear_btn = pn.widgets.Button(
    name="Reset",
    button_type="warning",
    styles=custom_style,
    width=100,
)

def clear_cb(*e):
    xshift_s.value = 0.
    yshift_s.value = 0.

clear_btn.on_click(clear_cb)


def _shift_image(*e):
    xshift = xshift_s.value
    yshift = yshift_s.value
    shifted = fourier_shift(radii_fft.copy(), (yshift, xshift))
    shifted = np.abs(np.fft.ifft2(shifted))
    fig1.update(shifted)

xshift_s.param.watch(_shift_image, "value")
yshift_s.param.watch(_shift_image, "value")

fig1._toolbar.append(xshift_s)
fig1._toolbar.append(yshift_s)
fig1._toolbar.append(clear_btn)

pn.Column(
    fig1.layout,
).servable("fourier-shift")
