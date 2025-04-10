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
fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Linear Ramp (0 → 1)",
        maxdim=550,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.
fig1.fig.right[0].width = 25
fig1._outer_toolbar.height = 0

tools = tuple(fig1._floatpanels.values())[0]['items']

pn.Row(
    fig1.layout,
    pn.HSpacer(max_width=50),
    pn.Column(
        *tools,
    )
).servable("colour-uniformity")