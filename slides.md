---
marp: true
theme: rose-pine-dawn
math: mathjax
title: What is an image?
description: QEM 2025
author: Matthew Bryan
keywords: images,electron-microscopy
url: https://github.com/matbryan52/microscopy-images-qem
---

![bg left:40% 60%](figures/qem.png)

# **What is an image?**

Matthew Bryan
*CEA-Leti, Grenoble, France*
[matthew.bryan@cea.fr](mailto:matthew.bryan@cea.fr)
GitHub: [@matbryan52](https://github.com/matbryan52)

---
<!-- paginate: true -->

# Preamble

Microscopy lets us see, for a time

<hr>

An image lets us look again

---
<!-- _class: columns2 -->
<style scoped>
/* Set the image and text to inline elements */
img, span {
    display: inline;
    vertical-align: middle;
}
</style>
# Who I am

Matthew Bryan<br />
[@matbryan52](https://github.com/matbryan52) on GitHub
![width:300px align:center](figures/me.jpg)

**Research Software Engineer**<br />
![w:150 h:auto](figures/cea-leti.png)  Grenoble :fr:  Alps :mountain_snow:
<br>

Not really a Microscopist!
<br>

Background:

- chemical engineering
- image processing
- computer vision

---
<!-- _class: columns2 -->
<style scoped>

h1 {
  column-span: all;
}

</style>
# Content

- [Images and Photographs](#photographs-images)
- [Digital Images](#digital-images)
- [Image visualisation](#visualising-images)
- [Sampling](#sampling)
- [Images and geometry](#transforms)
- [Image filtering](#filtering)
- Image enhancement
- Image segmentation

---

<!-- _class: columns2 -->

<a name='photographs-images'></a>

<br/><br/>
# **Images and Photographs**

<figure>
<img src="https://krvarshney.github.io/kush_varshney.png" width=500px/>
<figcaption style="text-align: right; font-size: 16px"><a href="https://krvarshney.github.io">krvarshney.github.io</a></figcaption>
</figure>

---

## Images

Most generally, an Image is a visual representation of an object or scene

- In most contexts two-dimensional, though not only
- An image point in optics refers to the point where all light rays from a single point on an object intersect
- Recording the light along the plane of these intersection points forms a complete image of the object

---

####  Photography

Projection of focused light onto a surface has been known for millenia, but we lacked a reliable method to record the light until the early 1800s. (<a href="https://phydemo.app/ray-optics">phydemo.app</a>)
<!-- <figure>
<figcaption style="text-align: right; font-size: 16px"></figcaption> -->
<iframe src="https://phydemo.app/ray-optics/simulator/#XQAAAALBAwAAAAAAAABEKcrGU8hqLFnpmU9ERVKNO2ePj8XJTmUUQxTk4wzV-JNF7iYGUdpNImZrFI4NxHx54TObf8pGDW-uQ4iap450XQ9ZVVKbKtN20qJCDFJNe8-mqfMcT87wzYH9Ou79hCfVvnw4dhPOEuFF0Rx4r7BB7OZDCsU0PezMis4qwCmewxlKsoC9CM_odt0YKk_d-cAFhL0L3ZrUi53iJMnw9s0MJGjkLjam0Ix-joTjlCegfAvvhnzHwcEQeRzORinD_wddSLfyiobAMXi1jwiIhr6DL-aSP0XiuNABDRMNXIYLoTOOng3jGtlgmLU9w4rHaXx7HGw7YmcHCchyVxVuPzq5npRjjNU-YkEfZfqyOkHN_Y7r92UOtkiuEUg5vxBjPy227B_HecckbPwSRIsQjiSvGAjMlvYJBL9qpvZiUwTD2m_U5ZcoJno-4grK8JCsT7za9EO28ite3JT8BD_vYUxu7kbKRPIS_CGO9tr7M1dgU86eNbZrSuu-0wEEDRW18h0xzubHXkj6bIXYHrc90Z87N2NvwDfTavCRlQ5ch18BC0mtpSBBkkeIKRq9UbFUVnCaB81zLBcpzU0ukqR_W4Y7nfORg0_oqCS4ihrLphFoc2OlzEXiH1NMdcPFbN__3FksYg" width="1100px" height="450px" frameBorder="0"></iframe>

---

##  Analogue images - Film

<!-- _class: columns2 -->

Recording light in chemical reactions

- Light- (or electron-) sensitive coatings that transform when *exposed*
- Sensitivity determined by (chemical) reaction rate (temperature, wavelength etc.)
- "Resolution" determined by average particle size - randomly distributed!
  - In practice film is extremely densely coated

<span style="text-align: right">Micrograph of film grain</span>
<figure>
<iframe src="http://localhost:9091/film-particles" width="560" height="450" frameBorder="0"></iframe>
<figcaption style="text-align: right; font-size: 20px"><a href="https://www.photomacrography.net/forum/viewtopic.php?t=26857">photomacrography.net</a></figcaption>
</figure>

---

##  Analogue images (Aside)

Any light-reacting chemistry could record a photograph, even photosynthesis

<figure>
<figcaption style="text-align: right; font-size: 20px"><a href="https://www.youtube.com/watch?v=-qETedzsFIE">YouTube @AppliedScience</a></figcaption>
<p float="left">
  <img src="figures/geranium-lens.png" height="400" />
  <img src="figures/geranium-leaf.png" height="400" /> 
</p>
</figure>

---

## Digital images

Recording light with numbers

- Measure local intensity electrically (conversion to charge, voltage), then *digitize* the analog signal to a numerical value
- Discrete sampling of the wavefront, usually onto a 2D grid
- At the most basic, a digital image is a list of numbers representing recorded *values*, and a way to structure these numbers into a shape we can interpret

---

## Rays to Image

![w:auto h:550](figures/digital-sensor.svg)

---

## Pixels

A *pixel* is an **el**ement of a **pi**cture

- Represents a single intensity from the wavefront that was recorded

By extension, a *voxel* is an **el**ement of a **vo**lume, in 3D

---

## Image calibrations

Digital images are discrete, both in space and value

- Position within a digital image is via index coordinate like `[3, 5]`, not dimension `[0.2 cm, 0.8 cm]`.
- Intensity is typically recorded as an integer value like `530`, not a physical quantity like $3.2\: W\cdot m^{-2}$

Interpretation of digital images in physical units requires a *calibration*, accounting for (amongst others):

- Pixel size, spacing, shape
- Sensor response, readout characteristics


---

<!-- _class: columns2 -->

<style scoped>h2 { position: absolute; top: 5%; }</style>

## Colour images

A colour image is a set of images of the same wavefront, each sampling part of the full spectrum.

- We are most familiar with <span style="color:red">Red</span><span style="color:green">Green</span><span style="color:blue">Blue</span> (<span style="color:red">R</span><span style="color:green">G</span><span style="color:blue">B</span>) images
- These are usually made with a pre-sensor Bayer filter, which samples colour differently in adjacent pixels
- The values from pixels are split into <span style="color:red">R</span>, <span style="color:green">G</span>, and <span style="color:blue">B</span> intensity images.
- The three signals are spatially offset

When recombined intelligently, most images are represented without any artifacts, despite the offset

<figure>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Bayer_pattern_on_sensor.svg/1920px-Bayer_pattern_on_sensor.svg.png" width=500px/>
<figcaption style="text-align: right; font-size: 16px"><a href="https://en.wikipedia.org/wiki/Bayer_filter#/media/File:Bayer_pattern_on_sensor.svg">Bayer-filter, Wiki - Cburnett</a></figcaption>
</figure>

---

## Spectral images

These are a logical extension of colour images, where each sub-image or *channel* represents a well-defined band of wavelength or energy.
- In contrast to colour images, spectral channels don't typically overlap in energy
- We usually cannot sample both spatially and spectrally simultenously, so we either create images channel-by-channel (EFTEM), or position-by-position (STEM-EELS)

---

<iframe src="https://phydemo.app/ray-optics/simulator/#XQAAAAJ3BAAAAAAAAABFqcrGU8hqLFnpmU9ERVKNPZUF_UC06pYFGJ1gc_njnHAQ6BXGzId4JbUgUJrFgoJPTEfFuZOf0bY8BwMqBZV8NrKKRSvAA9m43y39zcRl8lCzeUCyA3x4JnD674GPMtaoWVPEsjpMieHf5R7ApLoHn4OT8kVTDY_qbD8TnXNH001ocSc0CuNO4GUNRfg3-TXXvciAO7U4VXCmTBlKekTTHeZ7v9qpXgVE3_3P5izYztOABQ9ckBVyf0aRCV3Fxaw8iNtxBKTec7AoIRcS6A0Gao83hicekSdKAwwKEPRMEfv7yz6z0npCdqa05f_ldJ2sD9zAmePmysK6CDqseNMJzsZVj9Yi81Q9s6g-U4anGUhpb5SOYLmlrTX5WLNHeozEso50HhMbmuzgOkrGt0iZPCl8qv8R0Xi5_j9zO4QxiramoGqakP2EGKBo_6mC0h-jlUWS3sDpH77QS3xAG9raZWWFIK3ZoTV_z5_hnB-bujE-nFa4DGaUwB5GvejlwA9HpvDZGrfDuxKL-vAa5YaJ3PeklKyimXGLK5tMqg3KgtcpyS2wF8Q0Gsi4HitjNOMMKCTt6U0bICx4vJ3SROXOgT254PoUDTqj4Q1nXBbJuCTnKA8j8bJsVEBhie1Q3c7G-WSytXp046csH6mnwcW6IvoWXD4f5wLwPcllUrHFjyqhzsO6JCZqZhPC9yf3GnkKrSciS-0NCPZyOCzA42B6wNb0I9sIAzRcrw2oZuuM6RSrfM0tyRKlkwvTGWCky63zIgu9g4396i4sowkpFR93FrP-w1Crem3TqntFxxgxOkKOs-HvoC2J01hhmuQnvLcrDsJkubZ9XCnFVmMsKA9PXaYpuFbA4pR02lToD8l0J6n38__o_I8o" style="position:fixed; top:5%; left:5%; width:90%; height:90%; border:none; margin:0; padding:0; overflow:hidden; z-index:999999;"></iframe>

---

<a name='digital-images'></a>

# **Images as digital information**

![bg right:50% 70%](figures/pixellated-atoms.png)

---

## Arrays of numbers

Computers store numbers as sequences of binary digits, which we interpret according to convention.

- An image is no more than a 1D list of numbers to a computer, there is no intrinsic 2D data structure in a computer's memory.
- The 1D data can be ordered row-by-row, or column-by-column, according to hardware and convention
  - This has implications for processing, as memory is **slow** - reading a whole row could be much faster than reading a whole column, or vice-versa.

---

<style scoped>h2 { position: absolute; top: 5%; }</style>

## Memory layout

![w:100% h:450](figures/memory-layout.svg)

This becomes very important for >2D data, it pays to store data in a way which
matches the processing being done (whole images, or one pixel from many images?).

---

<style scoped>
table {
  font-size: 20px;
}
</style>
## Number types

There are many conventions for storing numbers, here are some common ones in images:

|                  | Name      | Size (bits) | Min          | Max        | Example usage |
| ---------------- | --------- | ----------- | ------------ | ---------- | ---------- |
| Binary           | `bool`      | 8           | 0            | 1          | Masking pixels |
| Unsigned Integer | `uint8`     | 8           | 0            | 255        | Raw data |
|                  | `uint16`    | 16          | 0            | 65,535      | Raw data |
| Integer          | `int16`     | 16          | \-32,768      | 32,767      | Background-subtraction |
|                  | `int32`     | 32          | \-2,147,483,648 | 2,147,483,647 | Computation |
| Floating         | `float32`   | 32          | \-3.40E+38   | \-3.40E+38 | Computation |
|                  | `float64`   | 64          | \-1.70E+308  | 1.70E+308  | Computation |
| Complex          | `complex64` | 64          | \-3.40E+38   | \-3.40E+38 | Waves, FFT |

---

## Number types - Uses

Most camera sensors generate raw data as unsigned integers (8-, 16- or more bits). When we begin to transform raw data we usually need to convert its type to hold our results correctly.

---

## Number types - Notes

- Digital numbers are stored in a fixed amount of space - exceeding the min or max for a type can cause "wrapping", e.g. `200_uint8 + 100_uint8 = 44_uint8`.
  - The range for `uint8` is 256, so `200 + 100 = 300` becomes `300 mod 256 = 44`.
* The size of the number is the space it requires in memory, and on disk
  - Often the larger the number type, the slower operations with that type are
* Floating point numbers have variable precision, i.e. they can represent very large or very small values, but are poor when trying to represent both at once
  - For example `324,000 + 0.0055 = 324,000` not `324,000.0055`
  - Be careful with electron wavelength and camera lengths!
* Complex numbers are stored as a pair of floating numbers representing real and imaginary parts, there is no native complex number format

---

<style scoped>h2 { position: absolute; top: 5%; }</style>
## Image math

<iframe src="http://localhost:9091/image-math" width="1150" height="700" frameBorder="0"></iframe>

---

## Coordinate system conventions

Depending on the tool or language you use, image coordinate systems can vary

- Most use matrix notation for indexing `[row, column]`
* Python and C-inspired languages are **0-indexed**
  - i.e. `image[5, 3]` means "6th row, 4rd column"
* MATLAB is **1-indexed**:
  - `image[5, 3]` means "5th row, 3rd column"
* Most place `y == 0` at the "top" when displayed, with positive "down"
  - This matches matrix notation, but is opposite to convention for axes / graphs
  - Implies a change of direction for rotations (clockwise not anticlockwise!)

---

## Multi-image data, stacks, 4D-STEM

![w:100% h:100%](figures/image-sizes.svg)

Tomography acquisitions can an add an extra `[tilt]` dimension to the above!

---

<!-- _class: columns2 -->

## Sparse images

In very low dose conditions (or with EDX), most image pixels contain a zero value. This is good use case for *sparse* images.

- Store only non-zero values
- Can achieve enormous space saving
- Many operations `f(a, 0) == {0, a}` so remove wasted computation
- Simplest strategy is store coordinates + values, but more intelligent schemes exist (e.g. CSR)

![w:100% h:550](figures/sparse-matrix.svg)

---

## Image file formats

Images can be stored in many ways, depending on how they are used

- `.jpg`, `.png`, `.gif`: colour RGB `uint8` images, compressed for small file size, open anywhere without special software, not for raw data
* `.tif`: a general-purpose image format, can hold most number types and shapes
  - TIFF files with strange data (floating point) may need special software
  - Can hold additional metadata (e.g. calibrations), can be compressed
* Proprietary formats like `.dm3/4`, `.mib`, `.emd`, `.blo`: specific to a certain camera or software, not always readable elsewhere
* General *array* formats: `.mat`, `.npy`, `.hdf5`, `.zarr`: flexible, can be compressed, can hold stacks / nD data and metadata, need compatible code/software

---

## Image software

Useful software packages to work with images in microscopy

---

<style scoped>h3 { position: absolute; top: 3%; }</style>

<!-- _class: columns2 -->
### Fiji ([imagej.net](https://imagej.net/software/fiji/))

Widely used in scientific imaging, many plugins

![w:475px](figures/imagej.png)

Calibrations, stacks, measurements, math, segmentation...

![h:600px](figures/imagej-fig.svg)

---

<style scoped>h3 { position: absolute; top: 7%; }</style>

<!-- _class: columns2 -->
### Napari ([napari.org](https://napari.org/))
Multi-D data viewer, annotations

Python-based, easy to add analysis

![w:600px](https://napari.org/stable/_images/sphx_glr_vortex_001.png)

![w:600px](https://napari.org/stable/_images/sphx_glr_labels3d_001.png)

Good support for 3D volumes

---

<style scoped>
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>

### Gatan Digital Micrograph ([gatan.com](https://www.gatan.com/installation-instructions))
Well-known, feature-rich GUI even when using the free license

Python scripting enables any analysis with GMS display

![bg right:60% 95%](figures/gms.png)

---

## Python tools for images

The Python scientific ecosystem is vast - once an image is loaded as array data, typically under `numpy`, it can be interpreted in myriad ways

---

`scipy-ndimage` ([docs.scipy.org](https://docs.scipy.org/doc/scipy/reference/ndimage.html))

- Low-level tools for images (e.g. convolve, interpolate, measurements)

`scikit-image` / `skimage` ([scikit-image.org](https://scikit-image.org/))

- High-level tools for images (e.g. resizing, alignment, segmentation, filtering)

![bg right:50% 80%](figures/scipy-skimage.svg)

---
<!-- _class: columns2 -->

`Pillow` \[Python Imaging Library\] ([pillow.readthedocs.io](https://pillow.readthedocs.io/en/stable/))

- Graphics-focused, colour images, drawing, compositing

```python
# Pillow imports as PIL
from PIL import Image, ImageDraw

image = Image.open("image.png")
draw = ImageDraw.Draw(image)
draw.text((50, 50), "Text")
```
<br>

`imageio` ([imageio.readthedocs.io](https://imageio.readthedocs.io/en/stable/))

- Reading and writing many image formats and videos

```python
import imageio.v3 as iio

frames = np.stack(
  [iio.imread(f"{x}.jpg") for x in range(n)],
)
iio.imwrite("test.gif", frames, fps=10)
```

---

`matplotlib` ([matplotlib.org](https://matplotlib.org/stable/))

- General plotting library, but will `load` images, or display them on axes
- Good for combining images with results + annotations

![bg right:50% 95%](figures/diff.png)

---

<a name='visualising-images'></a>

# **Visualising images**

![bg right:50% 90%](figures/cross-grating.png)

---

## Data → Screen colour

Scientific cameras produce images of intensity as unsigned integers, typically, and screens display `uint8` RGB colour (24-bit colour). This requires us to map from data to screen for display.

- <span style="color:red">R</span> = <span style="color:green">G</span> = <span style="color:blue">B</span> in a colour image displays as colourless **Grey**
  - Screens can only display 256 levels of pure grey intensity
  - If the data are more than 8-bit, need to sacrifice detail or clip the data range
- We can use artificial colour to achieve more on-screen contrast, known as a *lookup table* or *colormap*, of which there are many choices for different applications.

The choice of colormap or data transformation for display can massively influence how the data are perceived.

---
<style scoped>h3 { position: absolute; top: 3%; }</style>
### Brightness + Contrast
<iframe src="http://localhost:9091/colour-map" width="1150" height="650" frameBorder="0"></iframe>

<!-- Interactive figure of brightness, contrast, clip, gamma transform

Maybe a coloured line / scatter plot of the mapping ?

Interactive colourmap figure with some symmetric data, too -->

---

## Dynamic range

In microscopy we frequently see data which span orders of magnitude in value, with detail at both the low and high-ends. A logarithmic transform is one way display such data on screen.

---
<style scoped>h3 { position: absolute; top: 3%; }</style>
### Gamma + Logarithmic colour
<iframe src="http://localhost:9091/gamma-log" width="1150" height="650" frameBorder="0"></iframe>

---

## Perceptual uniformity

Colourmaps are critical to how we interpret visual data. It is important to recognize
when a feature we see is from the data or from the map.

- Perceptually uniformity means a $\Delta$ in the data displays as the same *visual* $\Delta$ to our eyes, no matter where in the range of mapped values it is
  - No one range of values changes "faster" than another
- Non-uniform colourmaps can create visual boundaries which do not exist in the data, or hide true boundaries.

This is a well-studied problem, and uniform colourmaps are available for many applications. See the [colorcet.holoviz.org](https://colorcet.holoviz.org/) page or [Kovesi (2015)](https://arxiv.org/pdf/1509.03700) for good examples.

---

<iframe src="http://localhost:9091/colour-uniformity" width="1150" height="650" frameBorder="0"></iframe>

---
<style scoped>
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>
## Colour blindness

Certain colour blindness forms are experienced in 1-5% of the population (biased towards males). Choice of colourmap can hugely impact the perception of data for these populations.

- In particular try to *avoid* using <span style="color:red">Red</span>–<span style="color:green">Green</span> to draw distinctions

[davidmathlogic.com/colorblind](https://davidmathlogic.com/colorblind) is a simple overview.

![height:240 center](figures/cblind.svg)

---

## Transparency (Alpha)

Digital images can also be combined using transparency, often called *alpha*. This allows overlaying one information atop another. Transparency can apply on a per-pixel basis so can be used to convey information itself.

---

## Complex and 2D-vector images

Complex numbers cannot be directly displayed, we need to choose how to map the real and imaginary part onto an intensity image.

- A typical example in microscopy is electron holography, where the reconstructed wavefront is complex
  - The `abs()` of the wave represents its amplitude
  - The `angle()` of the wave displays its phase

<!-- phase unwrapping -->

---

<iframe src="http://localhost:9091/complex-image" width="1150" height="650" frameBorder="0"></iframe>

---

<a name='sampling'></a>

# **Sampling**

![bg right:50% 70%](figures/pixellated-atoms.png)

---

- Pixel size (all rays down to one point)
- Sampling (nyquist limit etc)
- Fourier transforms of images, aliasing
- Moirés
- Image interpolation
- "Sub-pixel" methods / upsampling

---

<a name='transforms'></a>

# **Images and Geometry**

![bg right:50% 90%](./figures/skimage-transform.png)

---
<style scoped>
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>
# Geometric transforms of images

The information in an image exists on a coordinate grid. We can map the same data to a new grid using a *transform*

![height:350 center](figures/transform.svg)

---
<style scoped>
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>
## Resizing

The simplest transform is resizing - `(0, 0)` remains static, all other values are moved onto a larger or smaller grid

Missing values are added via *interpolation* (upscaling), multiple values are merged using *averaging* (downscaling)

![height:350 center](figures/resize.svg)

---

## Matrix transforms

Uniform transformations can be represented as a matrix multiplication that applies to the coordinate grid. These can be chained arbitrarily to acheive a range of effects.

<br>

| $\begin{bmatrix}s_x & 0 & 0 \\0 & s_y & 0 \\0 & 0 & 1 \\\end{bmatrix}$ | $\begin{bmatrix}\cos{\theta} & -\sin{\theta} & 0 \\\sin{\theta} & \cos{\theta} & 0 \\0 & 0 & 1 \\\end{bmatrix}$ | $\begin{bmatrix}1 & 0 & 0 \\0 & -1 & 0 \\0 & 0 & 1 \\\end{bmatrix}$ | $\begin{bmatrix}1 & \lambda & 0 \\0 & 1 & 0 \\0 & 0 & 1 \\\end{bmatrix}$ | $\begin{bmatrix}1 & 0 & t_x \\0 & 1 & t_y \\0 & 0 & 1 \\\end{bmatrix}$ |
| :--------------: | :-------: | :---------: | :----------: | :--------: |
| Scaling $x$ + $y$ | Rotation by $\theta$ | Flip-$y$ | Shear $x$ | Shift $x$ + $y$ |

<br>

A uniform resize operation is the scaling matrix multiplication with $s_x = s_y$

---

Figures of different transforms on an image

centreforcities.org

---
<style scoped>h2 { position: absolute; top: 3%; }</style>
## Non-uniform transforms

When an imaging system is heavily distorted, a simple matrix transformation may not be enough. In this case a non-uniform transform can be applied to correct local displacements.

<iframe src="http://localhost:9091/transform-nonuniform" width="1150" height="600" frameBorder="0"></iframe>


---
<style scoped>h2 { position: absolute; top: 3%; }</style>
## Polar image transform

Some image signals, e.g. diffraction patterns, can be better-interpreted in polar coordinates $(r, \theta)$ rather than Cartesian $(x, y)$.

<iframe src="http://localhost:9091/warp-polar" width="1150" height="600" frameBorder="0"></iframe>

---

<a name='filtering'></a>

# **Image Filtering**

![bg right:50% 90%](./figures/skimage-transform.png)

---

---

# Image filters

- 2D Convolution as a process
- Simple filters (blur, edge)
- Non-convolutional filters (median etc)
- Filtering of images in frequency space
  - Clean power spectrum
  - Low-pass, High-pass
  - Selective Bragg filter
  -

---

# Image segmentation

- Thresholding (auto-threshold detection)
- Operations on binary images (erode, dilate etc)
- Labelled images, measures on labelled regions
- Basic segmentation algorithms
- "Machine learning" segmentation

---

# Image alignment / pattern matching

- Image correlation / autocorrelation
- Common alignment tools and approaches
- Image difference metrics

---

# Image restoration

- Binning
- Denoising
  - BM(3D), Noise2Noise etc
- Inpainting

---

# Extra topics

A bit more physics ??

- PSF
- STEM scan patterns ?
- GPA
- Phase Reconstruction (holo etc)
- Distortion correction