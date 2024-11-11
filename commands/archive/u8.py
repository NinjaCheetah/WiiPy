# "commands/archive/u8.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy
from modules.core import fatal_error


def handle_u8_pack(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    try:
        u8_data = libWiiPy.archive.pack_u8(input_path)
    except ValueError:
        fatal_error(f"The specified input file/folder \"{input_path}\" does not exist!")

    out_file = open(output_path, "wb")
    out_file.write(u8_data)
    out_file.close()

    print("U8 archive packed!")


def handle_u8_unpack(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if not input_path.exists():
        fatal_error(f"The specified input file \"{input_path}\" does not exist!")

    u8_data = open(input_path, "rb").read()

    # Output path is deliberately not checked in any way because libWiiPy already has those checks, and it's easier
    # and cleaner to only have one component doing all the checks.
    libWiiPy.archive.extract_u8(u8_data, str(output_path))

    print("U8 archive unpacked!")
