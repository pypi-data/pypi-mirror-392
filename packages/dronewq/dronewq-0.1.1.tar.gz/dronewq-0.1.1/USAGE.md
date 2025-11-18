# DroneWQ Usage Guide

This document provides detailed usage examples and best practices for the DroneWQ package.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration](#configuration)
3. [Processing Pipeline](#processing-pipeline)
4. [Water Quality Algorithms](#water-quality-algorithms)
5. [Georeferencing and Mosaicking](#georeferencing-and-mosaicking)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Install from PyPI
pip install dronewq

# Or install from source
git clone https://github.com/aewindle110/DroneWQ.git
cd DroneWQ
pip install -e .
```

### Import the Package

```python
import dronewq
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

## Configuration

### Setting Up Your Project Directory

DroneWQ requires a specific folder structure for organizing your MicaSense images:

```
<main_directory>/
    ├── panel/              # Calibrated reflectance panel images
    ├── raw_sky_imgs/       # Sky calibration images
    ├── raw_water_imgs/     # Water images from flight
    └── align_img/          # One image capture for alignment (5 .tif files)
```

### Configure Settings

The `configure()` function sets up all paths automatically:

```python
# Configure the main directory
dronewq.configure(main_dir="/path/to/your/main_directory")

# Access configured paths
print(dronewq.settings.main_dir)           # Main directory path
print(dronewq.settings.raw_water_dir)      # Raw water images directory
print(dronewq.settings.raw_sky_dir)        # Raw sky images directory
print(dronewq.settings.panel_dir)          # Panel images directory
print(dronewq.settings.lt_dir)             # Radiance (Lt) images directory
print(dronewq.settings.lw_dir)             # Water-leaving radiance (Lw) directory
print(dronewq.settings.rrs_dir)            # Remote sensing reflectance (Rrs) directory
print(dronewq.settings.masked_rrs_dir)     # Masked Rrs directory
```

### Extract Metadata

Extract metadata from your MicaSense images:

```python
from micasense import imageset

# Load image set
img_set = imageset.ImageSet.from_directory(dronewq.settings.raw_water_dir)

# Extract and save metadata
dronewq.write_metadata_csv(
    img_set=img_set,
    csv_output_path=dronewq.settings.main_dir
)

# Load metadata into a DataFrame
metadata = pd.read_csv(dronewq.settings.metadata)
print(metadata.head())
print(metadata.columns)  # View available metadata columns
```

## Processing Pipeline

### Step 1: Raw Imagery to Radiance (Lt)

The processing pipeline begins by converting raw pixel values to radiance. This is handled automatically by `process_raw_to_rrs()`.

### Step 2: Water-Leaving Radiance (Lw)

Choose a method to remove sky reflection:

#### Mobley Rho Method (Default, Recommended)

Uses Mobley's rho parameter to estimate sky reflection:

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",
    ed_method="dls_ed",
    num_workers=4
)
```

**When to use:** Most general purpose applications, works well in varied conditions.

#### Hedley Method

Uses the Hochberg/Hedley approach with NIR-based glint correction:

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="hedley_method",
    random_n=10,  # Number of random images for ambient NIR calculation
    ed_method="dls_ed",
    num_workers=4
)
```

**When to use:** When you have strong NIR signal and want NIR-based correction.

#### Black Pixel Method

Assumes black pixel (no water-leaving radiance) in NIR:

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="blackpixel_method",
    ed_method="dls_ed",
    num_workers=4
)
```

**When to use:** Clear Case 1 waters where NIR can be assumed zero.

### Step 3: Downwelling Irradiance (Ed)

Choose a method to normalize by downwelling irradiance:

#### DLS Method (Default)

Uses the Downwelling Light Sensor data:

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",
    ed_method="dls_ed",  # Default
    num_workers=4
)
```

**When to use:** When you have good DLS sensor data.

#### Panel Method

Uses calibrated reflectance panel measurements:

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",
    ed_method="panel_ed",
    num_workers=4
)
```

**When to use:** When panel measurements are available and well-calibrated.

#### DLS Corrected by Panel

Uses DLS data corrected by panel measurements:

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",
    ed_method="dls_and_panel_ed",
    num_workers=4
)
```

**When to use:** Best accuracy when both DLS and panel data are available.

### Step 4: Pixel Masking (Optional)

Mask pixels containing sun glint, shadows, or adjacent vegetation:

#### Threshold Masking

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",
    ed_method="dls_ed",
    mask_pixels=True,
    pixel_masking_method="value_threshold",
    nir_threshold=0.01,      # NIR threshold for glint/land masking
    green_threshold=0.005,   # Green threshold for shadow masking
    num_workers=4
)
```

**Parameter tuning:**
- `nir_threshold`: Increase if glint is not being masked (default: 0.01)
- `green_threshold`: Adjust based on shadow conditions (default: 0.005)

#### Standard Deviation Masking

```python
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",
    ed_method="dls_ed",
    mask_pixels=True,
    pixel_masking_method="std_threshold",
    mask_std_factor=1,  # Standard deviation factor for masking
    num_workers=4
)
```

### Complete Processing Example

```python
# Complete processing pipeline
dronewq.process_raw_to_rrs(
    output_csv_path=dronewq.settings.metadata,
    lw_method="mobley_rho_method",      # Sky reflection removal
    ed_method="dls_ed",                 # Irradiance normalization
    mask_pixels=True,                   # Apply masking
    pixel_masking_method="value_threshold",
    nir_threshold=0.01,                 # Adjust based on your data
    green_threshold=0.005,
    overwrite_lt_lw=False,              # Don't overwrite existing files
    clean_intermediates=True,           # Remove intermediate files
    num_workers=4                       # Parallel processing
)
```

## Water Quality Algorithms

### Chlorophyll-a Algorithms

DroneWQ provides several chlorophyll-a retrieval algorithms:

#### Gitelson (Recommended for Coastal Waters)

Best for Case 2 (coastal) waters:

```python
# Using the batch processing function
dronewq.save_wq_imgs(
    wq_alg="chl_gitelson",
    num_workers=4
)

# Or apply directly to arrays
rrs_red = ...  # Red band Rrs
rrs_rededge = ...  # Red edge band Rrs
chl = dronewq.chl_gitelson(rrs_red, rrs_rededge)
```

**Algorithm details:**
- Gitelson et al. 2007
- Formula: `chl = 59.826 * (Rrs_rededge / Rrs_red) - 17.546`
- Units: mg m⁻³

#### Hu (Low Chlorophyll Concentrations)

For clear waters with low chlorophyll (<0.15 mg m⁻³):

```python
dronewq.save_wq_imgs(
    wq_alg="chl_hu",
    num_workers=4
)

# Or apply directly
rrs_blue = ...  # Blue band Rrs
rrs_green = ...  # Green band Rrs
rrs_red = ...    # Red band Rrs
chl = dronewq.chl_hu(rrs_blue, rrs_green, rrs_red)
```

**Algorithm details:**
- Hu et al. 2012
- Uses color index (CI) three-band reflectance difference
- Recommended for: chlorophyll < 0.15 mg m⁻³

#### OCx (Higher Chlorophyll Concentrations)

For waters with higher chlorophyll (>0.2 mg m⁻³):

```python
dronewq.save_wq_imgs(
    wq_alg="chl_ocx",
    num_workers=4
)

# Or apply directly
rrs_blue = ...   # Blue band Rrs
rrs_green = ...  # Green band Rrs
chl = dronewq.chl_ocx(rrs_blue, rrs_green)
```

**Algorithm details:**
- O'Reilly et al. 1998
- Fourth-order polynomial relationship
- Uses Landsat 8 OC2 coefficients
- Recommended for: chlorophyll > 0.2 mg m⁻³

#### Blended Hu-OCx (NASA Standard)

Combines Hu and OCx algorithms with blending:

```python
dronewq.save_wq_imgs(
    wq_alg="chl_hu_ocx",
    num_workers=4
)

# Or apply directly
rrs_blue = ...   # Blue band Rrs
rrs_green = ...  # Green band Rrs
rrs_red = ...    # Red band Rrs
chl = dronewq.chl_hu_ocx(rrs_blue, rrs_green, rrs_red)
```

**Algorithm details:**
- Blends Hu (CI) and OCx algorithms
- Transitions smoothly between methods
- Used in NASA ocean color products

### Total Suspended Matter (TSM)

#### Nechad Algorithm

```python
dronewq.save_wq_imgs(
    wq_alg="nechad_tsm",
    num_workers=4
)

# Or apply directly
rrs_red = ...  # Red band Rrs
tsm = dronewq.tsm_nechad(rrs_red)
```

**Algorithm details:**
- Nechad et al. 2010
- Formula: `TSM = (374.11 * Rrs_red / (1 - Rrs_red / 17.38)) + 1.61`
- Units: mg m⁻³

### Batch Processing

Process water quality images in batches:

```python
# Process first 100 images
dronewq.save_wq_imgs(
    wq_alg="chl_gitelson",
    start=0,
    count=100,
    num_workers=4
)

# Process next 100 images
dronewq.save_wq_imgs(
    wq_alg="chl_gitelson",
    start=100,
    count=100,
    num_workers=4
)
```

## Georeferencing and Mosaicking

### Extract Metadata

```python
# Load metadata
metadata = pd.read_csv(dronewq.settings.metadata)

# View flight parameters
print(f"Number of captures: {len(metadata)}")
print(f"Altitude range: {metadata['Altitude'].min():.1f} - {metadata['Altitude'].max():.1f} m")
print(f"Yaw range: {metadata['Yaw'].min():.1f} - {metadata['Yaw'].max():.1f} degrees")
```

### Compute Flight Lines

Automatically detect flight transects:

```python
flight_lines = dronewq.compute_flight_lines(
    captures_yaw=metadata['Yaw'].values,
    altitude=metadata['Altitude'].median(),  # Or use specific altitude
    pitch=0,  # Usually 0 for nadir viewing
    roll=0,   # Usually 0 for nadir viewing
    threshold=10  # Yaw angle threshold in degrees
)

print(f"Detected {len(flight_lines)} flight lines")
for i, line in enumerate(flight_lines):
    print(f"Line {i+1}: captures {line['start']}-{line['end']}, yaw={line['yaw']:.1f}°")
```

### Georeference Images

Georeference individual images using camera parameters:

```python
dronewq.georeference(
    metadata=metadata,
    input_dir=dronewq.settings.rrs_dir,  # Or masked_rrs_dir
    output_dir="/path/to/georeferenced/",
    lines=flight_lines,  # Use computed flight lines
    # Or specify manually:
    # altitude=metadata['Altitude'].median(),
    # yaw=metadata['Yaw'].median(),
    # pitch=0,
    # roll=0,
    num_workers=4
)
```

### Create Mosaic

Create an orthomosaic from georeferenced images:

```python
dronewq.mosaic(
    input_dir="/path/to/georeferenced/",
    output_path="/path/to/mosaic.tif",
    method="mean"  # Options: 'mean', 'median', 'max', 'min'
)
```

### Visualize Results

```python
import rasterio
import contextily as ctx
from dronewq.core.plot_map import plot_georeferenced_data

# Load mosaic
with rasterio.open("/path/to/mosaic.tif") as src:
    mosaic_data = src.read(1)
    transform = src.transform
    crs = src.crs

# Plot with basemap
fig, ax = plt.subplots(figsize=(12, 10))
plot_georeferenced_data(
    data=mosaic_data,
    transform=transform,
    crs=crs,
    ax=ax,
    cmap='viridis',
    vmin=0,
    vmax=50  # Adjust based on your data range
)
plt.title("Chlorophyll-a Mosaic (mg m⁻³)")
plt.colorbar(label="Chlorophyll-a (mg m⁻³)")
plt.show()
```

## Advanced Usage

### Loading and Visualizing Images

```python
# Load processed images and metadata
images, metadata = dronewq.retrieve_imgs_and_metadata(
    img_dir=dronewq.settings.rrs_dir,
    count=10,  # Load first 10 images
    start=0,
    altitude_cutoff=50  # Filter by minimum altitude
)

# Visualize first image
fig, axes = plt.subplots(1, 5, figsize=(15, 3))
band_names = ['Blue', 'Green', 'Red', 'Red Edge', 'NIR']

for i, (ax, band_name) in enumerate(zip(axes, band_names)):
    im = ax.imshow(images[0, i], cmap='viridis', vmin=0, vmax=0.02)
    ax.set_title(band_name)
    ax.axis('off')
    plt.colorbar(im, ax=ax)

plt.tight_layout()
plt.show()
```

### Custom Processing

Process individual steps manually:

```python
# Step 1: Convert raw to radiance
dronewq.process_micasense_images(
    warp_img_dir=dronewq.settings.warp_img_dir,
    overwrite_lt_lw=False,
    sky=False
)

# Step 2: Apply sky reflection removal
dronewq.mobley_rho(num_workers=4)

# Step 3: Normalize by irradiance
dronewq.dls_ed(output_csv_path=dronewq.settings.metadata, num_workers=4)

# Step 4: Apply masking
dronewq.threshold_masking(
    nir_threshold=0.01,
    green_threshold=0.005,
    num_workers=4
)
```

### Working with Metadata

```python
# Load metadata
metadata = pd.read_csv(dronewq.settings.metadata)

# Filter by conditions
high_altitude = metadata[metadata['Altitude'] > 100]
low_altitude = metadata[metadata['Altitude'] < 50]

# Sort by timestamp
metadata['UTC-Time'] = pd.to_datetime(metadata['UTC-Time'])
metadata = metadata.sort_values('UTC-Time')

# Group by flight line
# (Assuming you have flight line identifiers in metadata)
flight_groups = metadata.groupby('flight_line')
```

### Performance Optimization

```python
# Adjust number of workers based on your CPU
import os
num_cores = os.cpu_count()
num_workers = min(num_cores, 8)  # Don't use all cores

# Process in smaller batches for large datasets
batch_size = 100
total_images = len(metadata)

for start_idx in range(0, total_images, batch_size):
    print(f"Processing batch {start_idx} to {start_idx + batch_size}")
    dronewq.save_wq_imgs(
        wq_alg="chl_gitelson",
        start=start_idx,
        count=batch_size,
        num_workers=num_workers
    )
```

## Troubleshooting

### Common Issues

#### 1. "Please set the main_dir path" Error

**Solution:** Configure the main directory first:
```python
dronewq.configure(main_dir="/path/to/your/main_directory")
```

#### 2. Glint Not Being Masked

**Solution:** Increase the NIR threshold:
```python
dronewq.process_raw_to_rrs(
    ...,
    nir_threshold=0.02,  # Increase from default 0.01
    ...
)
```

#### 3. Out of Memory Errors

**Solution:** Process in smaller batches:
```python
dronewq.save_wq_imgs(
    wq_alg="chl_gitelson",
    start=0,
    count=50,  # Smaller batch size
    num_workers=2  # Fewer workers
)
```

#### 4. Georeferencing Errors

**Solution:** Check your metadata columns and flight parameters:
```python
# Verify metadata has required columns
required_columns = ['Latitude', 'Longitude', 'Altitude', 'Yaw', 'Pitch', 'Roll']
for col in required_columns:
    if col not in metadata.columns:
        print(f"Warning: Missing column {col}")
```

#### 5. Poor Alignment

**Solution:** 
- Ensure `align_img/` contains a good reference image with features visible in all bands
- Try adjusting alignment parameters in `get_warp_matrix()` if processing manually

### Getting Help

- **Documentation**: https://dronewq.readthedocs.io/
- **Issues**: https://github.com/aewindle110/dronewq/issues
- **Sample Data**: [Zenodo DOI](https://doi.org/10.5281/zenodo.14018788)

## Best Practices

1. **Always check your data first**: Visualize raw images and metadata before processing
2. **Start with defaults**: Use default parameters first, then tune based on your data
3. **Validate results**: Compare processed Rrs with expected values for your water type
4. **Save intermediate results**: Set `clean_intermediates=False` initially to debug issues
5. **Document parameters**: Keep notes on which parameters worked best for your dataset
6. **Process in batches**: For large datasets, process in manageable batches
7. **Use appropriate algorithms**: Choose chlorophyll algorithms based on concentration ranges

## Citation

If you use DroneWQ in your research, please cite:

```
Windle, A. E., et al. (2024). DroneWQ: A Python library for measuring water quality 
with multispectral drone sensors. Zenodo. https://doi.org/10.5281/zenodo.14018788
```

