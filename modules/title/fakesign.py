# "modules/title/fakesign.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_fakesign(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

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
        raise TypeError("This does not appear to be a TMD, Ticket, or WAD! Cannot fakesign.")
