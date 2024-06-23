# "ash.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import os
import libWiiPy


def decompress_ash(in_file: str, out_file: str = None):
    if not os.path.isfile(in_file):
        raise FileNotFoundError(in_file)

    ash_file = open(in_file, "rb")
    ash_data = ash_file.read()
    ash_file.close()

    ash_decompressed = libWiiPy.archive.decompress_ash(ash_data)

    if out_file is None:
        out_file = in_file + ".arc"

    ash_out = open(out_file, "wb")
    ash_out.write(ash_decompressed)
    ash_out.close()
