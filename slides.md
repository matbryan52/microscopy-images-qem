---
marp: true
theme: rose-pine-dawn
math: mathjax
title: What is an image?
description: QEM 2025
author: Matthew Bryan
keywords: images,electron-microscopy
url: https://github.com/matbryan52/microscopy-images-qem
# paginate: true
---
<!-- <iframe src="http://localhost:8888" width="1000" height="600" frameBorder="0"></iframe> -->

![bg left:40% 60%](figures/qem.png)

# **What is an image?**

Matthew Bryan
*CEA-Leti, Grenoble, France*
[matthew.bryan@cea.fr](mailto:matthew.bryan@cea.fr)
GitHub: [@matbryan52](https://github.com/matbryan52)

---

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
<figcaption style="text-align: right"><a href="https://krvarshney.github.io">krvarshney.github.io</a></figcaption>
</figure>

---

## Images

Most generally, an Image is a visual representation of some object or scene

- In most contexts two-dimensional, though not just
- An image point in optics refers to the point where all light rays from a single point on an object intersect
- Recording the light along the plane of these intersection points forms a complete image of the object

---

##  Photography

Projection of focused light onto a surface has been known for millenia

- *Camera Obscura*

But a method of recording the patterns in that light was not found until the early 1800s

---

##  Analog images - Film

Recording light in chemical reactions

- Light- (or electron-) sensitive coatings that transform when *exposed*
- Sensitivity determined by (chemical) reaction rate (temperature, wavelength etc.)
- "Resolution" determined by average particle size - randomly distributed!
  - In practice film is extremely densely coated

---

## Digital images

Recording light with numbers

- Measure intensity electrically (conversion to charge, voltage), then *digitize* the analog signal to a numerical value
- Discrete sampling of the wavefront, usually onto a 2D grid
  - Some rays are lost, multiple rays combine into one sample point
- A digital image could be represented as a long table of `[position, intensity]`
  - If the order is constant and the grid regular then `position` is unecessary.

---

## Pixels

A *pixel* is an **el**ement of a **pi**cture

- Represents a single sample from the wavefront that was recorded
- And voxels, , calibrations

---

## Colour images, and more

* Colour or multi-channel images (filters in photography linked to EELS)

---

<a name='digital-images'></a>

# **Images as digital information**

![bg right:50% 70%](figures/pixellated-atoms.png)

---

# Images as digital information

- Memory layout, numerical types
- File formats (PNG, tiff, jpeg, proprietary formats), compression, encoding, headers
- Multi-image data, stacks, 4D-STEM
- Useful tools to work with images
- Useful libraries to load images in Python
- Conventions for coordinate systems

---

# Visualising images

- Colourmaps, perceptual uniformity :smile:
- Colour spaces
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
