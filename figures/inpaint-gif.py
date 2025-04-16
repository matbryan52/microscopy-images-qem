from imageio.v3 import imread, imwrite
import pathlib
rootdir = pathlib.Path(__file__).parent

original = imread(rootdir / "noisy-beamstop.png")
painted = imread(rootdir / "noisy-beamstop_cleanup.png")[..., :3]

imwrite(
    rootdir / "inpainting.gif", [original, painted], loop=0, fps=0.85,
)
