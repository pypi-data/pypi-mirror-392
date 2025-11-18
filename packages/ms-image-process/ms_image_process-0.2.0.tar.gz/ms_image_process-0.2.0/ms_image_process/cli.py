from PIL import Image, ImageEnhance
import os


def process_image(
        input_path: str,
        output_path: str,
        width: int,
        height: int,
        scale: float,
        grayscale: bool = False,
        brightness: float = 1.0,
        contrast: float = 1.0,
):
    """
    Processes an image with resizing, grayscale, and compression.
    :param input_path: input image path
    :param output_path: output image path
    :param width: image width
    :param height: image height
    :param scale: scaling factor
    :param grayscale: grayscale image
    :param brightness: brightness factor
    :param contrast: contrast factor
    """
    try:
        with Image.open(input_path) as img:
            print(f'Processing image {input_path}')

            # handle brightness
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
                print(f'adjusted brightness to {brightness}.')

            # handle contrast
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
                print(f'adjusted contrast to {contrast}.')

            # handle converting to grayscale
            if grayscale:
                img = img.convert('L')
                print('converted to grayscale.')

            # handle resizing
            original_width, original_height = img.size
            new_width, new_height = original_width, original_height

            if scale:
                new_width = int(new_width * scale)
                new_height = int(new_height * scale)
            elif width:
                new_width = width
                new_height = int(new_height * width / original_width)
            elif height:
                new_height = height
                new_width = int(new_width * height / original_height)

            if (new_width, new_height) != (original_width, original_height):
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f'resized to {new_width}x{new_height}.')

            # handle saving
            # get the file extension
            extension = os.path.splitext(input_path)[1].lower()

            save_options: dict = {'optimize': True}
            if extension in ['.jpg', '.jpeg']:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                save_options['quality'] = 90

            img.save(output_path, **save_options)
            print(f'successfully saved image to {output_path}')

    except FileNotFoundError:
        print(f'Error: Input file not found at \"{input_path}\"')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


import click


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option('--width', '-w', type=int, help='The target width in pixels.')
@click.option('--height', '-h', type=int, help='The target height in pixels.')
@click.option('--scale', '-s', type=float, help='The scaling factor (e.g. 0.5 for 50%).')
@click.option('--grayscale', '-g', is_flag=True, help='Convert the image to grayscale.')
@click.option('--brightness', '-b', type=float, default=1.0, help='Adjust the brightness.')
@click.option('--contrast', '-c', type=float, default=1.0, help='Adjust the contrast.')
def main(
        input_path: str,
        output_path: str,
        width: int,
        height: int,
        scale: float,
        grayscale: bool,
        brightness: float,
        contrast: float,
):
    """
    A simple CLI tool for processing images.

    Example:
    ms-image input.jpg output.png --scale 0.5 --grayscale
    """
    resize_options = [width, height, scale]
    if sum(1 for option in resize_options if option is not None) > 1:
        raise click.UsageError('Only one of --width, --height, or --scale can be specified.')

    process_image(
        input_path,
        output_path,
        width,
        height,
        scale,
        grayscale,
        brightness,
        contrast,
    )


if __name__ == '__main__':
    main()
