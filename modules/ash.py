# "ash.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_ash(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if args.compress:
        print("Compression is not implemented yet.")

    elif args.decompress:
        sym_tree_bits = args.sym_bits
        dist_tree_bits = args.dist_bits

        if not input_path.exists():
            raise FileNotFoundError(input_path)

        ash_file = open(input_path, "rb")
        ash_data = ash_file.read()
        ash_file.close()

        ash_decompressed = libWiiPy.archive.decompress_ash(ash_data, sym_tree_bits=sym_tree_bits,
                                                           dist_tree_bits=dist_tree_bits)

        ash_out = open(output_path, "wb")
        ash_out.write(ash_decompressed)
        ash_out.close()

        print("ASH file decompressed!")
