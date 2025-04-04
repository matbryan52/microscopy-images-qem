import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from libertem_ui.display.display_base import Curve

pn.extension('floatpanel')

size=256
coord = np.linspace(-1, 1., num=size, endpoint=True)
xx, yy = np.meshgrid(coord, coord)
img1 = np.sqrt(xx ** 2 + yy ** 2)
img1 /= 1.
img1 = img1 + xx * 1j

fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Complex image",
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.

pn.Row(
    fig1.layout,
).servable("complex-image")