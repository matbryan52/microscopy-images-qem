# QEM 2025 Practical Session

This document describes the practical session for QEM2025 related to image processing.

## Setup

From a terminal activate the `conda` environment using:

```bash
conda activate TP_AI
```

Then update the course materials using

```bash
tp-update
```

## Objective

The objective is to carry out measurements on a sample of gold nanoparticles using STEM imaging on a simulated microscope suffering from severe sample drift. Imaging quickly to mitigate the drift leads to poor signal-to-noise ratio images, while scanning too large an area slowy adds distortion as the sample drifts during a scan.

There are multiple approaches to measure the particles and acquire enough data to display a particle size distribution.

## Simulator

The simulator reproduces ADF-STEM imaging on a sample of nanoparticles which are drifting through the field of view. The simulator can be created like so:

```python
import numpy as np
from qem_practical.simulator import STEMImageSimulator

sim_data = np.load("data/particles.npz")
image = sim_data["data"]
extent = sim_data["extent"]
simulator = STEMImageSimulator(image, extent, current=1., drift_speed=0.1)
```

The simulator object has two user-facing methods:

```python
survey_image = simulator.survey_image(dwell_time=1e-6)  # seconds
```

where `survey_image` is always a `512x512` numpy array image of the field of view.

Secondly:

```python
scan_image = simulator.scan(
    centre=(219, 307),  # centre of the scan grid in pixel coordinates of the survey image
    scan_shape=(64, 64),  # scan grid shape-YX
    scan_step=0.1,  # scan grid stepsize in nm
    dwell_time=1e-6,
)
```

where `scan_image` is a numpy array of size `scan_shape` scanned around `centre`.

A helper for the survey image coordinate system is also available at 

```python
survey_def = simulator.survey
```

with properties:

```python
(sy, sx) = survey_def.scaling  #  scaling of the survey field of view in nm / pixel
(ey, ex) = survey_def.extent  # shape of the survey field of view in nm
```

and methods

```python
(ny, nx) = survey_def.to_continuous((py, px))  # convert from pixels to nanometres
(py, px) = survey_def.to_pixels((ny, nx))  # convert from nanometres to pixels
```

There is also a UI version of the simulator which will launch in a web browser with:

```python
simulator.show()
```
