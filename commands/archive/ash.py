# "commands/archive/ash.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_ash_compress(args):
    print("Compression is not implemented yet.")


def handle_ash_decompress(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(input_path.name + ".arc")

    # These default to 9 and 11, respectively, so we can always read them.
    sym_tree_bits = args.sym_bits
    dist_tree_bits = args.dist_bits

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    ash_data = input_path.read_bytes()
    # Decompress ASH file using the provided symbol/distance tree widths.
    ash_decompressed = libWiiPy.archive.decompress_ash(ash_data, sym_tree_bits=sym_tree_bits,
                                                       dist_tree_bits=dist_tree_bits)
    output_path.write_bytes(ash_decompressed)

    print("ASH file decompressed!")
