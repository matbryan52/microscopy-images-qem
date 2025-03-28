---
marp: true
theme: rose-pine-dawn
paginate: true
# backgroundImage: url('https://marp.app/assets/hero-background.svg')
---
<!-- <iframe src="http://localhost:8888" width="1000" height="600" frameBorder="0"></iframe> -->

# Image / Photograph / Frame

- History of photography, emulsions, resolution, sensivity
- Digital images, pixels, voxels, intensity / counts, calibrations
- Colour or multi-channel images (filters in photography linked to EELS)

---

# Images as binary information

- Memory layout, numerical types
- File formats (PNG, tiff, jpeg, proprietary formats), compression, encoding, headers
- Multi-image data, stacks, 4D-STEM
- Useful tools to work with images
- Useful libraries to load images in Python
- Conventions for coordinate systems

---

# Visualising images

- Colourmaps, perceptual uniformity
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
