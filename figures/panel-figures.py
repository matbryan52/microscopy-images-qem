import panel as pn
from bokeh.plotting import figure
from libertem_ui.figure import BokehImage


def film_particles():
    fig = figure(title="photo.fleurey.com", active_scroll="wheel_zoom")
    fig.background_fill_alpha = 0.
    fig.border_fill_color = None
    fig.x_range.range_padding = 0.
    fig.y_range.range_padding = 0.
    fig.y_range.flipped = True
    im = (
        BokehImage
        .new()
        .from_url(
            "https://photo.fleurey.com/uploads/5/0/8/9/50899857/9338092_orig.jpg"
        )
        .on(fig)
    )
    h, w = im.array.shape
    fig.frame_width = w
    fig.frame_height = h
    fig.toolbar_location = "below"
    return pn.pane.Bokeh(fig)


if __name__ == "__main__":
    pn.serve(
        panels={
            "film": film_particles,
        },
        title={
            "film": "Film Emulsion"
        },
        port=9091,
        show=False,
    )
