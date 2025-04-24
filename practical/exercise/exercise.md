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

The objective is to carry out STEM imaging measurements of a sample of gold nanoparticles using on a simulated microscope suffering from severe sample drift. Imaging quickly to mitigate the drift leads to poor signal-to-noise ratio images, while slowy scanning too large an area adds distortion as the sample drifts during a scan.

There are multiple approaches to measure the particles and acquire enough data to display a particle size distribution.

## Simulator

The simulator reproduces ADF-STEM imaging on a sample of nanoparticles which are drifting through the field of view. The simulator can be created like so:

```python
import numpy as np
from qem_practical.simulator import STEMImageSimulator

sim_data = np.load("data/particles.npz")
simulator = STEMImageSimulator(**sim_data)
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

## Exercises

### 1 - Detect, image and measure particles without drift

Create the simulator with argument `drift_speed=0.` to disable drifting. This means we can treat the survey image as *static* and measure any particle within the field of view without distortion or tracking.

- From a survey image taken at a long dwell time locate all of the particles in the field of view using a peak-finding or similar approach
- For some of the detected particles run a detailed STEM scan of each and display the high-resolution images on the same figure
- For each high-resolution image segment the particle from the background and measure its properties (e.g. diameter, circumference, area, circularity). Try to express the measurements in *nanometres* rather than pixels based on the information you have about each scan.
- Plot the distributions of the above values as histograms.

### 2 - Estimate the drift rate and direction

Create a simulator with a random drift speed `drift_speed="random"`. The survey image will now change over time as particles move through the field of view. The drift rate will be approximately constant while the drift direction slowly changes over time.

- Create a survey image with a short dwell time
- Identify a cluster of particles to scan in detail
- Scan the particles repeatedly and estimate the drift vector between successive frames
- Plot the drift vector over time and compare it to the simulator's true drift curve