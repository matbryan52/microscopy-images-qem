import panel as pn
import numpy as np
from libertem_ui.figure import ApertureFigure

pn.extension('codeeditor', 'floatpanel')


img1 = (np.linalg.norm(np.mgrid[-200: 200, -300: 300], axis=0) < 100).astype(np.float32)
img2 = np.roll(img1, (-50, 80), axis=(0, 1))

fig1 = (
    ApertureFigure
    .new(
        {
            "Image 1": img1,
            "Image 2": img2,
        },
        title='Inputs'
    )
)
fig1.fig.background_fill_alpha = 0.
fig1.fig.border_fill_color = None
fig1.fig.right[0].background_fill_alpha = 0.
fig2 = (
    ApertureFigure
    .new(
        img1 + img2,
        title='Output'
    )
)    
fig2.fig.background_fill_alpha = 0.
fig2.fig.border_fill_color = None
fig2.fig.right[0].background_fill_alpha = 0.

py_code = """def do_math(img1, img2):
    return img1 + img2
"""
editor = pn.widgets.CodeEditor(
    value=py_code,
    sizing_mode='stretch_width',
    language='python',
    height=125,
    on_keyup=True,
    stylesheets=["""
.ace_editor{
    font-size: 18px;
}
"""],
    margin=(20, 5, 5, 5),
)
button = pn.widgets.Button(
    name="RUN",
    button_type="success",
)
error_text = pn.widgets.StaticText(
    value="",
)

def run_callback(*e):
    try:
        locals_dict = {}
        exec(editor.value, globals(), locals_dict)
        do_math = locals_dict["do_math"]
        result = do_math(img1, img2)
        if not isinstance(result, np.ndarray):
            raise RuntimeError()
        if result.ndim != 2:
            raise RuntimeError()
        fig2.update(result)
        button.button_type="success"
        error_text.value = ""
    except Exception as ex:
        error_text.value = str(ex)
        button.button_type="danger"

button.on_click(run_callback)
fig2._toolbar.append(button)
fig2._toolbar.append(error_text)

pn.Column(
    editor,
    pn.Row(
        fig1.layout,
        fig2.layout,
    )
).servable("image-math")
