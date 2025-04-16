import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure, figure
from skimage.io import imread
from skimage.measure import label, regionprops
from skimage.segmentation import clear_border
from skimage.morphology import closing, footprint_rectangle, erosion
from bokeh.models import ColumnDataSource, ImageRGBA, Quad
from bokeh.events import Tap
from bokeh.models.glyphs import VSpan
from skimage.color import label2rgb
import pathlib
rootdir = pathlib.Path(__file__).parent

pn.extension('floatpanel')


img1 = imread(rootdir.parent / "nanoparticles.jpg", as_gray=True).astype(np.float32)
img1 = img1[:img1.shape[1], :]
vmin, vmax = img1.min(), img1.max()

frame_height = 350
fig1 = (
    ApertureFigure
    .new(
        img1,
        title="Image",
        tools=False,
        maxdim=frame_height,
        downsampling=False,
    )
)
fig1.fig.toolbar_location = "below"
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.im.color.add_colorbar(width=20)
fig1.fig.right[0].background_fill_alpha = 0.

display_select = pn.widgets.RadioButtonGroup(
    name="Display",
    value="Image",
    options=["Image", "Threshold", "Components"],
    button_type="primary",
)

threshold_slider = pn.widgets.FloatSlider(
    name="Threshold",
    value=0.5,
    start=0.,
    end=1.,
    step=0.01,
)

fig1.im.cds.data["image_rgba"] = [np.zeros(img1.shape, dtype=np.uint32)]
rgba_glyph = ImageRGBA(image="image_rgba")
rgba_renderer = fig1.fig.add_glyph(fig1.im.cds, rgba_glyph)


quad_source = ColumnDataSource(dict(
        left=[0],
        top=[0],
        right=[1],
        bottom=[0],
    ),
)
quad_glyph = Quad(top="top", right="right", bottom="bottom", left="left", fill_color="skyblue", line_color="white")


def _update_segmentation(*e):
    if display_select.value == "Image":
        fig1.update(img1)
        rgba_renderer.visible = False
        return

    threshold = threshold_slider.value
    mask = img1 < threshold


    bw = closing(mask, footprint_rectangle((3, 3)))
    bw = erosion(bw, footprint_rectangle((3, 3)))

    if display_select.value == "Threshold":
        fig1.update(bw.astype(np.float32))
        rgba_renderer.visible = False
        return

    fig1.update(img1)
    rgba_renderer.visible = True
    # remove artifacts connected to image border
    cleared = clear_border(bw)
    # label image regions
    label_image = label(cleared)
    # to make the background transparent, pass the value of `bg_label`,
    # and leave `bg_color` as `None` and `kind` as `overlay`
    image_label_overlay = label2rgb(label_image, bg_label=0, kind='overlay', bg_color=(0, 0, 0))
    alpha = ((image_label_overlay > 0).sum(axis=-1) > 0).astype(np.float64)[..., np.newaxis]
    image_label_overlay = np.concatenate((image_label_overlay, alpha), axis=-1)
    overlay_uint32 = (image_label_overlay * 255).astype(np.uint8).view(np.uint32).reshape(img1.shape)
    fig1.im.cds.data.update(image_rgba=[overlay_uint32])

    regions = regionprops(label_image)
    areas = tuple(r.feret_diameter_max for r in regions)
    num_bins = 20
    bins = np.linspace(min(areas), max(areas), num_bins)
    hist, edges = np.histogram(areas, density=False, bins=bins)
    quad_source.data.update(
        top=hist, left=edges[:-1], right=edges[1:], bottom=[0] * len(hist)
    )


threshold_slider.param.watch(_update_segmentation, "value_throttled")
display_select.param.watch(_update_segmentation, "value")

fig2 = figure(title='Histogram', tools="xwheel_zoom,reset")
fig2.frame_height = frame_height
fig2.frame_width = int(fig2.frame_height * (350 / 250))
fig2.background_fill_alpha = 0.
fig2.border_fill_color = None
fig2.x_range.range_padding = 0.
fig2.y_range.range_padding = 0.
fig2.x_range.start = 0
fig2.x_range.end = 200
fig2.xaxis.axis_label = "Diameter (px)"
fig2.yaxis.axis_label = "Count"


quad_renderer = fig2.add_glyph(quad_source, quad_glyph)

# num_pts = 255
# num_bins = 30

# span_cds = ColumnDataSource(dict(x=[(vmin + vmax) / 2]))
# span = VSpan(x="x", line_width=2, line_color="#000000")
# span_renderer = fig2.add_glyph(span_cds, span)
# span_renderer.visible = False
fig1._toolbar.append(display_select)

pn.Row(
    fig1.layout,
    pn.layout.HSpacer(max_width=50),
    pn.Column(
        threshold_slider,
        pn.pane.Bokeh(fig2),
    ),
    align="center",
).servable("connected-components")
