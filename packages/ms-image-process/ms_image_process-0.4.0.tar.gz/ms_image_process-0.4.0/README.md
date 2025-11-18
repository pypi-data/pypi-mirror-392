# MS Image Process

A simple and command-line tool for resizing, scaling, and grayscale conversion of images.

## Features

- Resize images to specific dimensions
- Scale images by a factor
- Convert images to grayscale
- Adjust image brightness and contrast
- Rotate images by 90°, 180°, or 270°
- Auto-orient images based on EXIF data
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

- `--width WIDTH`, `-w`       Set the output image width (maintains aspect ratio)
- `--height HEIGHT`, `-h`     Set the output image height (maintains aspect ratio)
- `--scale SCALE`, `-s`       Scale the image by a factor (e.g., 0.5 for 50% size)
- `--grayscale`, `-g`         Convert the image to grayscale
- `--brightness FACTOR`, `-b` Adjust image brightness (default: 1.0)
- `--contrast FACTOR`, `-c`   Adjust image contrast (default: 1.0)
- `--rotate DEGREES`, `-r`    Rotate image (90, 180, or 270 degrees clockwise)

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

Resize an image to 1200px width, adjust brightness and contrast, and rotate it 180 degrees:
```bash
ms-image input.jpg output.jpg --width 1200 --brightness 1.1 --contrast 1.2 --rotate 180
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
