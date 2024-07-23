# "modules/archive/ash.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_ash(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    # Code for if --compress was passed.
    # ASH compression has not been implemented in libWiiPy yet, but it'll be filled in here when it has.
    if args.compress:
        print("Compression is not implemented yet.")

    # Code for if --decompress was passed.
    elif args.decompress:
        # These default to 9 and 11, respectively, so we can always read them.
        sym_tree_bits = args.sym_bits
        dist_tree_bits = args.dist_bits

        if not input_path.exists():
            raise FileNotFoundError(input_path)

        ash_file = open(input_path, "rb")
        ash_data = ash_file.read()
        ash_file.close()

        # Decompress ASH file using the provided symbol/distance tree widths.
        ash_decompressed = libWiiPy.archive.decompress_ash(ash_data, sym_tree_bits=sym_tree_bits,
                                                           dist_tree_bits=dist_tree_bits)

        ash_out = open(output_path, "wb")
        ash_out.write(ash_decompressed)
        ash_out.close()

        print("ASH file decompressed!")
