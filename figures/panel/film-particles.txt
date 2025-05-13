import panel as pn
from bokeh.plotting import figure
from libertem_ui.figure import BokehImage


fig = figure(active_scroll="wheel_zoom")
fig.background_fill_alpha = 0.
fig.border_fill_color = None
fig.x_range.range_padding = 0.
fig.y_range.range_padding = 0.
fig.y_range.flipped = True
im = (
    BokehImage
    .new()
    .from_url(
        "https://www.photomacrography.net/forum/userpix/2226_Rollei_IR_D23_1.jpg"
    )
    .on(fig)
)
h, w = im.array.shape
fig.frame_width = 500
fig.frame_height = int(fig.frame_width * (h / w))
fig.toolbar_location = "below"
pn.pane.Bokeh(fig).servable("film")
