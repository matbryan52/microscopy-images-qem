import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from skimage.transform import downscale_local_mean
from libertem_ui.figure import ApertureFigure
from skimage.restoration import unwrap_phase

pn.extension('floatpanel')


img1 = np.load(rootdir / "hologram.npz")["image"]

if False:
    factors = (2, 2)
    small_real = downscale_local_mean(img1.real, (factors))
    small_imag = downscale_local_mean(img1.imag, (factors))
    img1 = (small_real + 1j * small_imag).astype(np.complex64)
    img1 = np.clip(np.abs(img1), 0., 2.5) * np.exp(1j * np.angle(img1))
    np.savez_compressed(rootdir / "hologram.npz", image=img1.astype(np.complex64))


fig1 = (
    ApertureFigure
    .new(
        {
            "Real": img1.real,
            "Imaginary": img1.imag,
        },
        title="Raw complex image",
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.
new_raw_select = pn.widgets.RadioButtonGroup(
    options=fig1._channel_select.options,
    value=fig1._channel_select.value,
    button_type="primary",
)
fig1._channel_select = new_raw_select
fig1._channel_select.param.watch(
    fig1._switch_channel_cb, 'value',
)
fig1._toolbar.pop(-1)
fig1._toolbar.append(new_raw_select)

fig2 = (
    ApertureFigure
    .new(
        {
            "Amplitude": np.abs(img1),
            "Phase": np.angle(img1),
            "Unwrapped": unwrap_phase(np.angle(img1)),
        },
        title="Processed complex image",
    )
)
fig2.fig.toolbar_location = "below"
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.
new_proc_select = pn.widgets.RadioButtonGroup(
    options=fig2._channel_select.options,
    value=fig2._channel_select.value,
    button_type="primary",
)
fig2._channel_select = new_proc_select
fig2._channel_select.param.watch(
    fig2._switch_channel_cb, 'value',
)
fig2._toolbar.pop(-1)
fig2._toolbar.append(new_proc_select)

pn.Row(
    fig1.layout,
    pn.layout.HSpacer(max_width=50),
    fig2.layout,
    align="center",
).servable("complex-image")