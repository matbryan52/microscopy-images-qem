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
- Sampling
- Image visualisation
- Images and geometry
- Image filtering
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

##  Photography

Projection of focused light onto a surface has been known for millenia
<figure>
<figcaption style="text-align: right; font-size: 14px"><a href="https://phydemo.app/ray-optics">phydemo.app/ray-optics</a></figcaption>
<iframe src="https://phydemo.app/ray-optics/simulator/#XQAAAAK9AwAAAAAAAABEKcrGU8hqLFnpmU9ERVKNO2ePj8XJTmUUQxTk4wzV-JNF7iYGUdpNImZrFI4NxHx54TObf8pGDW-uQ4iap450XQ9ZVVKbKtN20qJCDFJNe8-mqfMcT87wzYH9Ou79hCfVvnw4dhPOEuFF0Rx4r7BB7OZDCsU0PezMis4qwCmewxlKsoC9CM_odt0YKk_d-cAFVqKYysrwSKIlJ7xKAVSJHXsxVU3Q04fejsyFGYsyFHx2xUxycuBI3FkvduJB0XqcpUeYjsMJ56so0-k4_QYO_1deXlj0-sJeaap7OVFRY8jcYzK6rrr_9hyeTWd-9zBm8LOwtnLKQ5FltVjSDiRn47d03FiH2LGzzyVTj9omFLn9UKKaK1jDApoOjELWpoe83S174wchKt7Xqe3QnqMlgvKPA-VoHRUWDD_AU1O2hs6gNWt_HRqajYBR2c2uBzmJIfxZi4n4jfecmMEmfvdWNgppPZb_F0DVoNJiTozpoKmLUkc3D2U705hd7JVrX_YMBpb22g7vHFN9uCLRb_L6un22puZWxIvzIxi2BUA-crJanK2f47GMV1A7W9bW-EipR1PuwzWvJk7VTP7Abj41I0MaMcz5LZwmh3PBgRQhA_GW8WAgNZLY3Ong9j_78-Uq" width="1100" height="400" frameBorder="0"></iframe>
</figure>
But a reliable method to record the patterns in light was not found until the early 1800s

---

##  Analog images - Film

<!-- _class: columns2 -->

Recording light in chemical reactions

- Light- (or electron-) sensitive coatings that transform when *exposed*
- Sensitivity determined by (chemical) reaction rate (temperature, wavelength etc.)
- "Resolution" determined by average particle size - randomly distributed!
  - In practice film is extremely densely coated

<iframe src="http://localhost:9091/film" width="700" height="500" frameBorder="0"></iframe>

---

##  Analog images (Aside)

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

## Colour images

A colour image is a set of images of the same wavefront, each acquired with a different spectral response. They sample the wave intensity in both space and wavelength.

- We are most familiar with <span style="color:red">Red</span><span style="color:green">Green</span><span style="color:blue">Blue</span> (<span style="color:red">R</span><span style="color:green">G</span><span style="color:blue">B</span>) images
- These are usually made with a pre-sensor Bayer filter
- The three colour *channels* overlap

The values from pixels are split into <span style="color:red">R</span>, <span style="color:green">G</span>, and <span style="color:blue">B</span> intensity images according to their filter.

These are recombined in the ratio necessary to reproduce what a human would see.

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

<figure>
<iframe src="https://phydemo.app/ray-optics/simulator/#XQAAAAI0BAAAAAAAAABFqcrGU8hqLFnpmU9ERVKNPZUF_UC06pYFGJ1gc_njnHAQ6BXGzId4JbUgUJrFgoJPTEfFehDrsbY8BwMqBZV8NrKKRSvAA9m43y39zcRl8lCzeUCyA3x4JnD674GPMtaoWVPEsjpMieHf5R7ApLoHn4OT8kVTDY_qbD8TnXNH001ocSc0CuNO4GUNRfg3-TXXvciAO7U4VXCmTBlKekTTHeZ7v9qpXgVE3_3P5uUJV3U4tEwkZSq2ufbpx2G4bpSJzftHQd6Vne8PCSLFL72fZaPqFlwMrIBOrVRs5gW4Pzee7MHoaUFGURN0NOuL-PX1h3a-CdL17EIxSnfXjoVem4qvDREyGudvHQcZe6sEM63z_9JtnQmu7bkGsOWqXIYB1dP24Oo0IN_t15sHrbnTgY-HgyscTxmcoQfFWFzGxna-5fIzc9mQuLlyVmNDSstbSZ7r7E8OmMHzO7wjCyj7DtKATreXCXjgGTJc7UHtvma7qv19oG6FWERghMSrw5GnYy4KRbkzok_o1yBQvUcSTbZ48ts2xD8ZOh7haf5sBhR4S02dPUzZYczT1C-zf9K7Bwu1TayHhwchJkyaooEpchZ8WqTThaAWHcFR20mk8OCbzy0fQL1rUDdFK4w35iFUNhNcDmlaORJYPI_FYY58NtVcqOrxKa-WWECbCw--b4Buiu_bX5n0vFduk1CiKeLi_yUxtRSzVxHF59rw-CXTHVi-VlrKDcZYJ28rqf3mR5uoFXbRI8axTVpIkfyJ4YPmTZ73Kc7S9LficG6cky5-X2zfdbGv_Ncua1WUfHWcqbfCsU0NyJ5kUap2P_QSy4sn9QxpS--36RKnMjcvsVZMwdisjNH4_XK6UA" width="1100" height="600" frameBorder="0"></iframe>
<figcaption style="text-align: right; font-size: 14px"><a href="https://phydemo.app/ray-optics">phydemo.app/ray-optics</a></figcaption>
</figure>

---

<a name='digital-images'></a>

# **Images as digital information**

![bg right:50% 70%](figures/pixellated-atoms.png)

---

# Images as digital information

- Memory layout, numerical types
- Math on images
- File formats (PNG, tiff, jpeg, proprietary formats), compression, encoding, headers
- Multi-image data, stacks, 4D-STEM
- Useful tools to work with images
- Useful libraries to load images in Python
- Conventions for coordinate systems

---

# Visualising images

- Colourmaps, perceptual uniformity :smile:
- Colour spaces, alpha
- Brightness, Contrast, Gamma, Logarithmic colour
- Complex images and representations
- Phase unwrapping / periodicity in images

---

# Images and sampling

- Pixel size (all rays down to one point)
- Sampling (nyquist limit etc)
- Fourier transforms of images, aliasing
- Moirés
- Image interpolation
- "Sub-pixel" methods / upsampling

---

# Geometric transforms of images

- Hierarchy up to affine
- Non-affine transforms
- Polar transforms
- Distortion correction

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
