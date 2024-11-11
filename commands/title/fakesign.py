# "commands/title/fakesign.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy
from modules.core import fatal_error


def handle_fakesign(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        fatal_error(f"The specified input file \"{input_path}\" does not exist!")

    if input_path.suffix.lower() == ".tmd":
        tmd = libWiiPy.title.TMD()
        tmd.load(open(input_path, "rb").read())
        tmd.fakesign()
        open(output_path, "wb").write(tmd.dump())
        print("TMD fakesigned successfully!")
    elif input_path.suffix.lower() == ".tik":
        tik = libWiiPy.title.Ticket()
        tik.load(open(input_path, "rb").read())
        tik.fakesign()
        open(output_path, "wb").write(tik.dump())
        print("Ticket fakesigned successfully!")
    elif input_path.suffix.lower() == ".wad":
        title = libWiiPy.title.Title()
        title.load_wad(open(input_path, "rb").read())
        title.fakesign()
        open(output_path, "wb").write(title.dump_wad())
        print("WAD fakesigned successfully!")
    else:
        fatal_error("The provided file does not appear to be a TMD, Ticket, or WAD and cannot be fakesigned!")
