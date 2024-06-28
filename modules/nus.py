# "nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_nus(args):
    title_version = None
    file_path = None

    # Check if --version was passed, because it'll be None if it wasn't.
    if args.version is not None:
        try:
            title_version = int(args.version)
        except ValueError:
            print("Enter a valid integer for the Title Version.")
            return

    # If --output was passed, then save the file to the specified path (as long as it's valid).
    if args.output is not None:
        file_path = pathlib.Path(args.output)
        if not file_path.parent.exists() or not file_path.parent.is_dir():
            print("The specified output path does not exist!")
            return
        if file_path.suffix != ".wad":
            file_path = file_path.with_suffix(".wad")

    # libWiiPy accepts a title version of "None" and will just use the latest available version if it gets it.
    title = libWiiPy.title.download_title(args.tid, title_version)

    # If we haven't gotten a name yet, make one from the TID and version.
    if file_path is None:
        file_path = pathlib.Path(args.tid + "-v" + str(title.tmd.title_version) + ".wad")

    wad_file = open(file_path, "wb")
    wad_file.write(title.dump_wad())
    wad_file.close()

    print("Downloaded title with Title ID \"" + args.tid + "\"!")
