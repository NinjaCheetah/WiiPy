# "commands/archive/lz77.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy
from modules.core import fatal_error


def handle_lz77_compress(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(input_path.name + ".lz77")

    if not input_path.exists():
        fatal_error(f"The specified file \"{input_path}\" does not exist!")

    lz77_data = input_path.read_bytes()
    data = libWiiPy.archive.compress_lz77(lz77_data)
    output_path.write_bytes(data)

    print("LZ77 file compressed!")


def handle_lz77_decompress(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(input_path.name + ".out")

    if not input_path.exists():
        fatal_error(f"The specified file \"{input_path}\" does not exist!")

    lz77_data = input_path.read_bytes()
    data = libWiiPy.archive.decompress_lz77(lz77_data)
    output_path.write_bytes(data)

    print("LZ77 file decompressed!")

