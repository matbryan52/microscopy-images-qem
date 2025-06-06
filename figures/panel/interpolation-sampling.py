import pathlib
rootdir = pathlib.Path(__file__).parent.parent
import panel as pn
import numpy as np
import skimage.io as skio
from libertem_ui.applications.line_profile import sampling_tool

pn.extension('floatpanel')

img = skio.imread(rootdir / "noisy.png", as_gray=True)
row, getter = sampling_tool(img, fig_kwargs=dict(title="Image"))

fig1 = row[0][-1]
fig1.object.background_fill_alpha = 0.
fig1.object.border_fill_color = None
fig1.object.right[0].background_fill_alpha = 0.
fig2 = row[1][-1].object
fig2.background_fill_alpha = 0.
fig2.border_fill_color = None
row.insert(1, pn.layout.HSpacer(max_width=50))

custom_style = {
    'font-size': "18px",
    'color': "#575279",
    'font-family': 'Pier Sans, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", Segoe UI Symbol, "Noto Color Emoji"',
}
row[0][0][1][0].styles = custom_style
row[-1][0][0].styles = custom_style

row.align="center"
row.sizing_mode="stretch_both"
row.servable("interpolation-sampling")
