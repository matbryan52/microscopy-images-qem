import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from libertem_ui.display.display_base import Curve

pn.extension('floatpanel')

size=256
coord = np.linspace(0, 1., num=size, endpoint=True)
img1 = np.tile(coord[np.newaxis, :], (size // 4, 1))

h, w = img1.shape
sin_intensity = 0.05 * (np.linspace(1, 0, num=h, endpoint=True) ** 1.7)
sin_coord = np.sin(coord * 2 * np.pi * 55)
sin_image = np.tile(sin_coord[np.newaxis, :], (h, 1))
sin_image *= sin_intensity[:, np.newaxis]

img1 = img1 * (1 + sin_image)
img1 = np.clip(img1, 0., 1.)
fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Linear Ramp (0 → 1) + Sine comb",
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

fig2 = (
    ApertureFigure
    .new(
        img1,
        title="Linear Ramp (0 → 1) + Sine comb",
        maxdim=500,
    )
)
fig2.fig.toolbar_location = "below"
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.
fig2.fig.right[0].width = 25
fig2._outer_toolbar.height = 0
fig2.im.color.change_cmap("Temperature")

fig1._outer_toolbar.pop(0)
fig2._outer_toolbar.pop(0)
fig1._outer_toolbar.pop(0)
fig2._outer_toolbar.pop(0)

tools1 = tuple(fig1._floatpanels.values())[0]['items']
tools2 = tuple(fig2._floatpanels.values())[0]['items']

pn.Column(
    pn.Row(tools1[0][0], tools1[-2]),
    fig1.layout,
    pn.Row(tools2[0][0], tools2[-2]),
    fig2.layout,
).servable("colour-uniformity")
