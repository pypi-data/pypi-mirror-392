import inspect
import shutil
from datetime import datetime
from pathlib import Path

from matplotlib import colormaps

import importlib.resources as pkg_resources
import click

import ratisbona_utils
import ratisbona_utils.colors.good_palettes as good_palettes
from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.colors import (
    parse_gimp_palette,
    to_gimp_palette,
    palette_generators,
    Palette,
    rgb_to_hex, to_gimp_gradient, rgb_to_normalized,
)
from ratisbona_utils.colors.palette_generators import matplotlib_colormap_to_palette
from ratisbona_utils.colors.serde_json_palette import to_json, from_json
from ratisbona_utils.io import errprint
from ratisbona_utils.terminals.vt100 import color_block


def do_display_palette(palette) -> None:
    for color, name, colortype in zip(
        palette.colors, palette.color_names, palette.color_types
    ):
        #displaycolor = rgb_to_hex(color) if colortype == "rgb" else str(color)
        block = color_block(color)
        print(f"{block}", end="")


def display_named_colors(palette: Palette) -> None:
    for color, name, colortype in zip(
        palette.colors, palette.color_names, palette.color_types
    ):
        displaycolor = rgb_to_hex(color) if colortype == "rgb" else str(color)
        block = color_block(color)
        print(f"{block} {name} {displaycolor}")


@click.group()
def palette_cli():
    errprint(blue_dosbox("Ratisbona Palette CLI"))

@palette_cli.command()
@click.argument(
    "palette_json",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
)
def incorporate(palette_json: Path):
    """
    Incorporate a palette JSON file into the good_palettes module.
    """
    with pkg_resources.files(ratisbona_utils.colors.resources) as resource_path:
        shutil.copy(palette_json, resource_path / palette_json.name)


@click.command("parse-gimp")
@click.argument(
    "gimp_palette_file",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True),
    required=False,
    default=None,
)
def gimp_palette_parser(gimp_palette_file: Path, output: Path | None):
    """
    Parse a GIMP palette file and print the palette object.
    """
    palette_str = gimp_palette_file.read_text()
    gimp_palette = parse_gimp_palette(palette_str)
    json_text = to_json(gimp_palette)
    if output:
        output.write_text(json_text)
    else:
        print(json_text)


@palette_cli.command("write-gimp")
@click.argument(
    "native_palette",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True),
    required=False,
    default=None,
)
def gimp_palette_writer(native_palette: Path, output: Path | None):
    """
    Write a GIMP palette file from a palette object.
    """
    palette_json = native_palette.read_text()
    palette = from_json(palette_json)
    gimp_palette = to_gimp_palette(palette)
    if output:
        output.write_text(gimp_palette)
    else:
        print(gimp_palette)


def identifier_to_palettename(identifier: str) -> str:
    return identifier.replace("_PALETTE", "").replace("_", "-").lower()


def _palettes_dict():
    identifiers = dir(good_palettes)
    palettes = list(filter(lambda identifier: identifier.endswith("_PALETTE"), identifiers))
    palette_names = (map(identifier_to_palettename, palettes))
    palette_instances = (map(lambda identifier: getattr(good_palettes, identifier), palettes))
    return dict(zip(palette_names, palette_instances))

def _resource_palettes():
    palettes = {}
    with pkg_resources.path(ratisbona_utils.colors.resources, '') as resource_path:
        for file in resource_path.iterdir():
            if file.suffix == '.json':
                palette = from_json(file.read_text())
                palettes[palette.name.lower()] = palette
    return palettes


PALETTES = dict(**_palettes_dict(), **_resource_palettes())

@palette_cli.command("writeout-builtin")
@click.argument("palette_name", type=click.Choice(PALETTES))
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True),
    required=False,
    default=None,
)
def writeout_builtin_palette(palette_name: str, output: Path | None):
    """
    Write a builtin palette to a file.
    """
    palette = PALETTES[palette_name]
    json_str = to_json(palette)
    do_display_palette(palette)
    if output:
        output.write_text(json_str)
    else:
        print(json_str)

GENERATORS = ["cielch_based_rgb_palette", "hsv_based_rgb_palette" ]


@palette_cli.command("writeout-generated")
@click.argument("generator", type=click.Choice(GENERATORS + [map for map in colormaps]))
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True),
    required=False,
    default=None,
)
@click.option(
    "--hue-steps",
    "-n",
    type=int,
    required=False,
    default=16,
)
@click.option(
    "--lightness",
    "-l",
    type=float,
    required=False,
    default=50,
)
@click.option(
    "--chroma",
    "-c",
    type=float,
    required=False,
    default=50,
)
@click.option(
    "--saturation",
    "-s",
    type=float,
    required=False,
    default=1,
)
@click.option(
    "--value",
    "-v",
    type=float,
    required=False,
    default=1,
)
def writeout_generated_palette(
    generator, output: Path | None, hue_steps, lightness, chroma, saturation, value
):
    """
    Write a generated palette to a file.

    Args:
        generator:
        output:
        hue_steps:
        lightness:
        chroma:
        saturation:
        value:

    Returns:
    """
    provided_args = {
        "hue_steps": hue_steps,
        "lightness": lightness,
        "chroma": chroma,
        "saturation": saturation,
        "value": value,
    }
    if generator in GENERATORS:
        palette = getattr(palette_generators, generator)
    elif generator in colormaps:
        def palette(hue_steps: int):
            return matplotlib_colormap_to_palette(hue_steps, generator)
    else:
        raise ValueError(f"Unknown generator {generator}")


    signature = inspect.signature(palette)
    valid_args = {
        key: value
        for key, value in provided_args.items()
        if key in signature.parameters
    }
    bound_args = signature.bind_partial(**valid_args)
    rgb_colors = palette(**bound_args.arguments)
    palette = Palette(
        name=f"{generator}_palette",
        description=f"Generated with {generator}",
        author="palette_cli",
        creation_date=datetime.now(),
        color_names=[""] * len(rgb_colors),
        color_types=["rgb"] * len(rgb_colors),
        colors=rgb_colors,
    )
    json_str = to_json(palette)
    do_display_palette(palette)
    if output:
        output.write_text(json_str)
    else:
        print(json_str)


@palette_cli.command("display")
@click.argument(
    "palette_file",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
)
def display_palette(palette_file: Path):
    """
    Display a palette file.
    """
    palette = from_json(palette_file.read_text())
    display_named_colors(palette)
    do_display_palette(palette)


@palette_cli.command("convert-to-gimp-gradient")
@click.argument(
    "palette_file", type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True)
)
@click.option(
    "--output-ggr-file",
    "-o",
    type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True),
    required=False,
    default=None,
)
def convert_to_gimp_gradient(palette_file: Path, output_ggr_file: Path):
    """
    Convert a palette file to a GIMP gradient file.
    """
    palette = from_json(palette_file.read_text())
    title = palette.name
    normalized_colors = [rgb_to_normalized(color) for color in palette.colors]
    gimp_gradient = to_gimp_gradient(title, normalized_colors)
    if output_ggr_file:
        output_ggr_file.write_text(gimp_gradient)
    else:
        print(gimp_gradient)


@palette_cli.command("parse-gimp")
@click.argument(
    "gimp_palette_file",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True),
    required=False,
    default=None,
)
def parse_gimp_palette_command(gimp_palette_file: Path, output: Path | None):
    """
    Parse a GIMP palette file and print the palette object.
    """
    palette_str = gimp_palette_file.read_text()
    gimp_palette = parse_gimp_palette(palette_str)
    display_named_colors(gimp_palette)
    do_display_palette(gimp_palette)
    json_text = to_json(gimp_palette)
    if output:
        output.write_text(json_text)
    else:
        print(json_text)