# MS Image Process

A simple and command-line tool for resizing, scaling, and grayscale conversion of images.

## Features

- Resize images to specific dimensions
- Scale images by a factor
- Convert images to grayscale
- Simple command-line interface

## Installation

1. Ensure you have Python 3.8 or higher installed
2. Install the package using pip:
   ```bash
   pip install ms-image
   ```

## Usage

```bash
ms-image input.jpg output.png [OPTIONS]
```

### Options

- `--width WIDTH`       Set the output image width (maintains aspect ratio)
- `--height HEIGHT`     Set the output image height (maintains aspect ratio)
- `--scale SCALE`       Scale the image by a factor (e.g., 0.5 for 50% size)
- `--grayscale`         Convert the image to grayscale

### Examples

Resize an image to 800px width (maintaining aspect ratio):
```bash
ms-image input.jpg output.jpg --width 800
```

Scale an image to 50% of its original size:
```bash
ms-image input.jpg output.jpg --scale 0.5
```

Convert an image to grayscale and scale it to 50% of its original size:
```bash
ms-image input.jpg output.jpg --grayscale --scale 0.5
```

## Dependencies

- Python 3.8+
- Pillow >= 12.0.0
- Click >= 8.3.1

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
Keep in mind that this is intended to be a simple and easy to use CLI tool without any complex features.
