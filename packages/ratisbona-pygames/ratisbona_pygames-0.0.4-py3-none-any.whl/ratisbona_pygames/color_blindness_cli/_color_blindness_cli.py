import click
from pathlib import Path
from PIL import Image

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.colors.simple_color import rgb_to_colorblindness, lms_colorblindness_d, lms_colorblindness_p, lms_colorblindness_t


@click.group
def color_blindness_cli():
    blue_dosbox("Color Blindness Image Transformer")


@color_blindness_cli.command
@click.argument("inputfile", type=click.Path(exists=True, path_type=Path))
def transform_image(inputfile: Path):
    """
    Transforms the given image file by converting it to RGB mode (if necessary) and
    applying a color blindness adjustment function to each pixel.

    The output files will be named like the input file but with _deuteranopia, _protanopia, or _tritanopia
    appended to the filename.

    Args:
        inputfile (Path): Path to the input image file. The file must exist and
            meet the path type constraints specified.
    """

    # PIL: Read image, convert to rgb if necessary and apply blindness function to every pixel.

    # Read the image from the file.
    image = Image.open(inputfile)

    # Transform to RGB-Palette, if necessary
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Iterate over the three blindness-types
    for blindness_type, transformation in (
            ("deuteranopia", lms_colorblindness_d),
            ("protanopia", lms_colorblindness_p),
            ("tritanopia", lms_colorblindness_t)
    ):

        # Iterate over all the pixels and apply the blindness function to each pixel.
        new_image = Image.new("RGB", image.size)
        for x in range(image.width):
            for y in range(image.height):
                r, g, b = image.getpixel((x, y))
                R, G, B = rgb_to_colorblindness((r,g,b), transformation)
                new_image.putpixel((x, y), (R, G, B))
        # save image as .jpg
        new_image.save(inputfile.with_name(f"{inputfile.stem}_{blindness_type}.jpg"))




