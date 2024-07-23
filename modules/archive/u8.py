# "modules/archive/u8.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_u8(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    # Code for if the --pack argument was passed.
    if args.pack:
        try:
            u8_data = libWiiPy.archive.pack_u8(input_path)
        except ValueError:
            print("Error: Specified input file/folder does not exist!")
            return

        out_file = open(output_path, "wb")
        out_file.write(u8_data)
        out_file.close()

        print("U8 archive packed!")

    # Code for if the --unpack argument was passed.
    elif args.unpack:
        if not input_path.exists():
            raise FileNotFoundError(args.input)

        u8_data = open(input_path, "rb").read()

        # Output path is deliberately not checked in any way because libWiiPy already has those checks, and it's easier
        # and cleaner to only have one component doing all the checks.
        libWiiPy.archive.extract_u8(u8_data, str(output_path))

        print("U8 archive unpacked!")
