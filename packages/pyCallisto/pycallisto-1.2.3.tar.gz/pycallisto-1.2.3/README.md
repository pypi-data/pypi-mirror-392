# pyCallisto

## What's New in Version 1.2.3

### New Features
- **GOES X-ray Flux Overlay**: New `spectrogramWithGOES()` function to overlay GOES satellite X-ray data on spectrograms
- **Enhanced Spectrogram Control**: Added `blevel` (background level) and `vmax` (maximum value) parameters for better visualization control

### Improvements
- Added `beautifulsoup4` and `scipy` to core dependencies for better out-of-the-box functionality
- Optional dependencies for GOES integration
- Improved Windows compatibility

---

pyCallisto is an image processing and data analysis Python library developed for e-CALLISTO data (http://www.e-callisto.org/). This library can be used to process data obtained using various solar radio spectrometers available around the globe.

## Installation

### Basic Installation
For core functionality (spectrogram visualization, time/frequency slicing, light curves):

```bash
pip install pyCallisto
```

### Installation with GOES Support
For GOES X-ray flux overlay capabilities:

```bash
pip install pyCallisto[goes]
```

### Full Installation
For all features:

```bash
pip install pyCallisto[all]
```

**⚠️ Important for Windows Users:**
- **Python 3.9-3.11 recommended** for best compatibility
- **Python 3.12+**: Some dependencies may fail to compile. Use the basic installation and install optional dependencies individually if needed
- If you encounter compilation errors, consider using a conda environment or installing Visual Studio Build Tools

### Alternative: Manual Dependency Installation
If you encounter issues with optional dependencies:

```bash
pip install pyCallisto
# Then install only what you need:
pip install sunpy  # For GOES features
```

## Prerequisites and Dependencies

### Core Dependencies (automatically installed)
- Python 3.7 or higher
- numpy
- matplotlib
- astropy
- beautifulsoup4
- scipy

### Optional Dependencies (for GOES integration)
Install with `pip install pyCallisto[goes]`:
- sunpy
- drms
- zeep
- lxml
- h5netcdf
- h5py
- cdflib
- reproject
- mpl-animators

## Features

- **Spectrogram Visualization**: Generate spectrograms from FITS files with customizable colormaps and parameters
- **Time and Frequency Slicing**: Extract specific time ranges and frequency bands from observations
- **Light Curve Analysis**: Create mean light curves by collapsing data along time axis
- **Spectrum Analysis**: Generate frequency spectra for specific time instances
- **GOES Integration**: Overlay GOES X-ray flux data on spectrograms for comprehensive solar event analysis
- **Background Subtraction**: Automated background estimation and removal
- **Universal Plot**: Combined visualization of spectrogram, light curve, and spectrum
- **File Concatenation**: Merge multiple FITS files along time axis for extended observations

## Troubleshooting

### Module Not Found Error
If you get `ModuleNotFoundError: No module named 'pyCallisto'`:
1. Ensure you're using the correct Python environment
2. Reinstall: `pip uninstall pyCallisto && pip install pyCallisto`

### Import Errors for GOES Features
If you get import errors when using `spectrogramWithGOES()`:
```bash
pip install pyCallisto[goes]
```

### Compilation Errors on Windows (Python 3.12+)
1. Use Python 3.9-3.11 instead, or
2. Install basic version and skip optional dependencies:
   ```bash
   pip install pyCallisto
   ```

### Visual Studio Build Tools Error
If you see "Microsoft Visual C++ 14.0 or greater is required":
1. Download [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/)
2. Install "Desktop development with C++"
3. Retry installation

For more help, please open an issue on [GitHub](https://github.com/ravipawase/pyCallisto/issues).

## Quick Start

### GOES Spectrogram Overlay

Overlay GOES X-ray flux data on your spectrogram:

```python
import matplotlib.pyplot as plt

# After loading and processing your data use this function at the end

joined_bg_subtracted.spectrogramWithGOES(    #joined_bg_subtracted is just a variable name
    tstart="2024-07-16 13:05",
    tend="2024-07-16 14:34",
    satellite_number=16,    
    xtick=5,
    save_path='spectrogram_with_goes_overlay_2024-07-16.png'
)
plt.show()
```

### Adjusting Spectrogram Parameters

Control dynamic range and background levels:

```python
# Use blevel to adjust background level
# Use vmax to set maximum value for color scaling
obj.spectrogram(blevel=10, vmax=20) #Example
```

## Contributors

**Mr. Ravindra Pawase**  
Data Scientist  
Cummins Inc.  
Pune-411 004, India

**Dr. K. Sasikumar Raja**  
Assistant Professor  
Indian Institute of Astrophysics  
II Block, Koramangala, Bengaluru-560 034, India

**Mr. Mrutyunjaya Muduli**  
B.E. Computer Science and Engineering  
Department of Computer Science and Engineering  
HKBK College of Engineering  
22/1, Opposite Manyata Tech Park, Nagavara, Bengaluru-560 045, India

## Feedback

For feedback, queries, or feature requests, please contact:
- ravi.pawase@gmail.com
- sasikumarraja@gmail.com
- mudulimrutyunjaya42@gmail.com

## Citation

If you find pyCallisto useful in your work, we appreciate acknowledgment. We recommend using the following citation:

"This work makes use of the pyCallisto library, which is available at https://github.com/ravipawase/pyCallisto"
