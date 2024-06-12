# "u8.py" from libWiiPy-cli by NinjaCheetah
# https://github.com/NinjaCheetah/libWiiPy-cli

import os
import libWiiPy


def extract_u8_to_folder(in_file: str, out_folder: str):
    if not os.path.isfile(in_file):
        raise FileNotFoundError(in_file)

    u8_data = open(in_file, "rb").read()

    try:
        libWiiPy.archive.extract_u8(u8_data, out_folder)
    except ValueError:
        print("Specified output folder already exists!")


def pack_u8_from_folder(in_folder: str, out_file: str):
    try:
        u8_data = libWiiPy.archive.pack_u8(in_folder)
    except ValueError:
        print("Specified input file/folder does not exist!")
        return

    out_file = open(out_file, "wb")
    out_file.write(u8_data)
    out_file.close()
