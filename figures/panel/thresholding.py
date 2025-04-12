import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from skimage.io import imread
from bokeh.models import ColumnDataSource
from bokeh.events import Tap
from bokeh.models.glyphs import VSpan
import pathlib
rootdir = pathlib.Path(__file__).parent

pn.extension('floatpanel')


img1 = imread(rootdir.parent / "overview_100K-binned.jpg", as_gray=True).astype(np.float32)
vmin, vmax = img1.min(), img1.max()


frame_height = 350
fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Image",
        tools=False,
        maxdim=frame_height,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.im.color.add_colorbar(width=20)
fig1.fig.right[0].background_fill_alpha = 0.


fig2 = figure(title='Histogram', tools="xwheel_zoom,reset")
fig2.frame_height = frame_height
fig2.frame_width = int(fig2.frame_height * (350 / 250))
fig2.background_fill_alpha = 0.
fig2.border_fill_color = None
fig2.x_range.range_padding = 0.
fig2.y_range.range_padding = 0.

num_pts = 255
num_bins = 30
bins = np.linspace(*(fig1.im.current_minmax), num_bins)
hist, edges = np.histogram(img1.ravel(), density=True, bins=bins)
hist /= hist.max()
hist *= 240.
fig2.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
         fill_color="skyblue", line_color="white")

span_cds = ColumnDataSource(dict(x=[(vmin + vmax) / 2]))
span = VSpan(x="x", line_width=2, line_color="#000000")
span_renderer = fig2.add_glyph(span_cds, span)
span_renderer.visible = False

def pan_end_cb(event: Tap):
    val = event.x
    if val < vmin or val > vmax:
        span_renderer.visible = False
        fig1.update(img1)
        return
    span_renderer.visible = True
    span_cds.update(data=dict(x=[val]))
    fig1.update((img1 > val).astype(np.float32))

fig2.on_event(
    Tap,
    pan_end_cb,
)

fig1._outer_toolbar.height = 0

pn.Row(
    fig1.layout,
    pn.layout.HSpacer(max_width=50),
    pn.pane.Bokeh(fig2, align='end'),
    align="center",
).servable("thresholding")
