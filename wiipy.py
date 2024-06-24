# "wiipy.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import argparse
from importlib.metadata import version

from modules.wad import *
from modules.nus import *
from modules.u8 import *
from modules.ash import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WiiPy is a simple command line tool to manage file formats used by the Wii.")
    parser.add_argument("--version", action="version",
                        version=f"WiiPy v1.0.0, based on libWiiPy v{version('libWiiPy')} (from branch \'main\')")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    wad_parser = subparsers.add_parser("wad", help="pack/unpack a WAD file",
                                       description="pack/unpack a WAD file")
    wad_parser.set_defaults(func=handle_wad)
    wad_group = wad_parser.add_mutually_exclusive_group(required=True)
    wad_group.add_argument("-p", "--pack", help="pack a directory to a WAD file", action="store_true")
    wad_group.add_argument("-u", "--unpack", help="unpack a WAD file to a directory", action="store_true")
    wad_parser.add_argument("input", metavar="IN", type=str, help="input file")
    wad_parser.add_argument("output", metavar="OUT", type=str, help="output file")

    nus_parser = subparsers.add_parser("nus", help="download a title from the NUS",
                                       description="download a title from the NUS")
    nus_parser.set_defaults(func=handle_nus)
    nus_parser.add_argument("tid", metavar="TID", type=str, help="Title ID to download")
    nus_parser.add_argument("-v", "--version", metavar="VERSION", type=int,
                            help="version to download (optional)")

    u8_parser = subparsers.add_parser("u8", help="pack/unpack a U8 archive",
                                      description="pack/unpack a U8 archive")
    u8_parser.set_defaults(func=handle_u8)
    u8_group = u8_parser.add_mutually_exclusive_group(required=True)
    u8_group.add_argument("-p", "--pack", help="pack a directory to a U8 archive", action="store_true")
    u8_group.add_argument("-u", "--unpack", help="unpack a U8 archive to a directory", action="store_true")
    u8_parser.add_argument("input", metavar="IN", type=str, help="input file")
    u8_parser.add_argument("output", metavar="OUT", type=str, help="output file")

    ash_parser = subparsers.add_parser("ash", help="compress/decompress an ASH file",
                                       description="compress/decompress an ASH file")
    ash_parser.set_defaults(func=handle_ash)
    ash_group = ash_parser.add_mutually_exclusive_group(required=True)
    ash_group.add_argument("-c", "--compress", help="compress a file into an ASH file", action="store_true")
    ash_group.add_argument("-d", "--decompress", help="decompress an ASH file", action="store_true")
    ash_parser.add_argument("input", metavar="IN", type=str, help="input file")
    ash_parser.add_argument("output", metavar="OUT", type=str, help="output file")
    ash_parser.add_argument("--sym-bits", metavar="SYM_BITS", type=int,
                            help="number of bits in each symbol tree leaf (default: 9)", default=9)
    ash_parser.add_argument("--dist-bits", metavar="DIST_BITS", type=int,
                            help="number of bits in each distance tree leaf (default: 11)", default=11)

    args = parser.parse_args()

    args.func(args)
