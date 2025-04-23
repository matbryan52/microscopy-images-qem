import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure
from libertem_ui.display.display_base import Cursor
from skimage.transform import warp_polar
from bokeh.models import LinearAxis, Range1d

pn.extension('floatpanel')


img1 = np.load(rootdir / "dp-spots.npy").astype(np.float32)
img1 = img1 ** 0.25

fig1 = (
    ApertureFigure
    .new(
        img1,
        title='Input',
        maxdim=350,
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.
fig1._outer_toolbar.height = 0

cy, cx = np.asarray(img1.shape) / 2.
cursor = (
    Cursor
    .new()
    .from_pos(288, 292)
    .on(fig1.fig)
    .editable(
        selected=True,
    )
)

img2 = warp_polar(img1, center=cursor.current_pos()[::-1])

fig2 = (
    ApertureFigure
    .new(
        img2,
        title='Transformed',
        maxdim=350,
    )
)
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.

fig2.fig.xaxis.axis_label = "Radius (px)"
fig2.fig.yaxis.axis_label = "Pixels"
fig2._outer_toolbar.height = 0

fig2.fig.extra_y_ranges['theta'] = Range1d(180., -180.)
ax2 = LinearAxis(
    axis_label="Theta (degrees)",
    y_range_name="theta",
)
fig2.fig.add_layout(ax2, 'left')

def _update_warped(attr, old, new):
    new_warped = warp_polar(img1, center=cursor.current_pos()[::-1])
    fig2.update(new_warped)

cursor.cds.on_change("data", _update_warped)

pn.Row(
    fig1.layout,
    pn.layout.HSpacer(max_width=25),
    fig2.layout,
).servable("warp-polar")
