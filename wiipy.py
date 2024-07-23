# "wiipy.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import argparse
from importlib.metadata import version

from modules.archive.ash import *
from modules.archive.u8 import *
from modules.title.fakesign import *
from modules.title.nus import *
from modules.title.wad import *

if __name__ == "__main__":
    # Main argument parser.
    parser = argparse.ArgumentParser(
        description="WiiPy is a simple command line tool to manage file formats used by the Wii.")
    parser.add_argument("--version", action="version",
                        version=f"WiiPy v1.2.2, based on libWiiPy v{version('libWiiPy')} (from branch \'main\')")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Argument parser for the ASH subcommand.
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

    # Argument parser for the fakesign subcommand.
    fakesign_parser = subparsers.add_parser("fakesign", help="fakesigns a TMD, Ticket, or WAD (trucha bug)",
                                            description="fakesigns a TMD, Ticket, or WAD (trucha bug)")
    fakesign_parser.set_defaults(func=handle_fakesign)
    fakesign_parser.add_argument("input", metavar="IN", type=str, help="input file")
    fakesign_parser.add_argument("output", metavar="OUT", type=str, help="output file")

    # Argument parser for the NUS subcommand.
    nus_parser = subparsers.add_parser("nus", help="download data from the NUS",
                                       description="download from the NUS")
    nus_subparsers = nus_parser.add_subparsers(dest="subcommand", required=True)
    # Title NUS subcommand.
    nus_title_parser = nus_subparsers.add_parser("title", help="download a title from the NUS",
                                                 description="download a title from the NUS")
    nus_title_parser.set_defaults(func=handle_nus_title)
    nus_title_parser.add_argument("tid", metavar="TID", type=str, help="Title ID to download")
    nus_title_parser.add_argument("-v", "--version", metavar="VERSION", type=int,
                                  help="version to download (optional)")
    nus_title_out_group_label = nus_title_parser.add_argument_group(title="output types (required)")
    nus_title_out_group = nus_title_out_group_label.add_mutually_exclusive_group(required=True)
    nus_title_out_group.add_argument("-o", "--output", metavar="OUT", type=str,
                                     help="download the title to a folder")
    nus_title_out_group.add_argument("-w", "--wad", metavar="WAD", type=str,
                                     help="pack a wad with the provided name")
    nus_title_parser.add_argument("--wii", help="use original Wii NUS instead of the Wii U servers",
                                  action="store_true")
    # Content NUS subcommand.
    nus_content_parser = nus_subparsers.add_parser("content", help="download a specific content from the NUS",
                                                   description="download a specific content from the NUS")
    nus_content_parser.set_defaults(func=handle_nus_content)
    nus_content_parser.add_argument("tid", metavar="TID", type=str, help="Title ID the content belongs to")
    nus_content_parser.add_argument("cid", metavar="CID", type=str,
                                    help="Content ID to download (in \"000000xx\" format)")
    nus_content_parser.add_argument("-v", "--version", metavar="VERSION", type=int,
                                    help="version this content belongs to (required for decryption)")
    nus_content_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                    help="path to download the content to (optional)")
    nus_content_parser.add_argument("-d", "--decrypt", action="store_true", help="decrypt this content")

    # Argument parser for the U8 subcommand.
    u8_parser = subparsers.add_parser("u8", help="pack/unpack a U8 archive",
                                      description="pack/unpack a U8 archive")
    u8_parser.set_defaults(func=handle_u8)
    u8_group = u8_parser.add_mutually_exclusive_group(required=True)
    u8_group.add_argument("-p", "--pack", help="pack a directory to a U8 archive", action="store_true")
    u8_group.add_argument("-u", "--unpack", help="unpack a U8 archive to a directory", action="store_true")
    u8_parser.add_argument("input", metavar="IN", type=str, help="input file")
    u8_parser.add_argument("output", metavar="OUT", type=str, help="output file")

    # Argument parser for the WAD subcommand.
    wad_parser = subparsers.add_parser("wad", help="pack/unpack a WAD file",
                                       description="pack/unpack a WAD file")
    wad_parser.set_defaults(func=handle_wad)
    wad_group = wad_parser.add_mutually_exclusive_group(required=True)
    wad_group.add_argument("-p", "--pack", help="pack a directory to a WAD file", action="store_true")
    wad_group.add_argument("-u", "--unpack", help="unpack a WAD file to a directory", action="store_true")
    wad_parser.add_argument("input", metavar="IN", type=str, help="input file")
    wad_parser.add_argument("output", metavar="OUT", type=str, help="output file")
    wad_parser.add_argument("--fakesign", help="fakesign the TMD and Ticket (trucha bug)",
                            action="store_true")

    # Parse all the args, and call the appropriate function with all of those args if a valid subcommand was passed.
    args = parser.parse_args()
    args.func(args)
