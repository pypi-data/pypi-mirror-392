# czi2ometiff

`czi2ometiff` is a Python tool for converting **Zeiss CZI** microscopy files into **OME-TIFF**, a widely used open standard for bioimaging data.  
It provides a simple, reliable interface for extracting image data, channel names, and pixel sizes from CZI files and exporting them into high-quality OME-TIFF files.

## Features

- **Easy to use** — convert a CZI file to OME-TIFF with a single function call.
- **Automatic metadata extraction**:
  - Channel names (from CZI metadata if available)
  - Pixel sizes in X, Y, and Z (converted to micrometers)
- **Flexible output** — works with multi-channel and multi-Z images.
- **OME-TIFF pyramids** — optional downsampled pyramid levels for fast viewing in tools like QuPath, OMERO, and napari.
- **Built on numpy2ometiff** — leverages robust OME-TIFF writing from the `numpy2ometiff` library.

## Installation

Install directly via pip:

```bash
pip install czi2ometiff
```

## Example Usage

```python
from czi2ometiff import convert_czi_to_ometiff

# Input CZI file
input_file = "example_image.czi"

# Optional: specify output path
output_file = "example_image.ome.tiff"

# Convert to OME-TIFF
output_path = convert_czi_to_ometiff(
    input_path=input_file,
    output_path=output_file,   # Optional—defaults to input filename with .ome.tiff
    downsample_count=8          # Number of pyramid levels
)

print("Saved OME-TIFF:", output_path)
```

## How It Works

`czi2ometiff` automatically:

1. **Reads the CZI file** using `czifile`
2. **Extracts image data** as a NumPy array  
3. **Detects channel names** from CZI metadata  
4. **Extracts pixel sizes** (stored in meters in CZI; converted to micrometers)
5. **Reformats data** into the (Z, C, Y, X) layout expected by OME-TIFF
6. **Writes the final OME-TIFF** using the `numpy2ometiff.write_ome_tiff()` function

All required metadata is set for compatibility with standard bioimaging software.

## Contributing

Contributions are welcome!  
If you'd like to add features, improve metadata parsing, or enhance compatibility with other CZI variants:

1. Fork the repository  
2. Create a feature branch  
3. Submit a pull request  

For major changes, please open an issue first to discuss your ideas.

## License

This project is licensed under the BSD 3-Clause License — see the [LICENSE](LICENSE) file for details.
