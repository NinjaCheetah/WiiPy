# "modules/title/emunand.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_emunand_title(args):
    emunand = libWiiPy.title.EmuNAND(args.emunand)
    if args.skip_hash:
        skip_hash = True
    else:
        skip_hash = False

    # Code for if the --install argument was passed.
    if args.install:
        input_path = pathlib.Path(args.install)

        if not input_path.exists():
            raise FileNotFoundError(input_path)

        if input_path.is_dir():
            wad_files = list(input_path.glob("*.[wW][aA][dD]"))
            if not wad_files:
                raise FileNotFoundError("No WAD files were found in the provided input directory!")
            wad_count = 0
            for wad in wad_files:
                title = libWiiPy.title.Title()
                title.load_wad(open(wad, "rb").read())
                try:
                    emunand.install_title(title, skip_hash=skip_hash)
                    wad_count += 1
                except ValueError:
                    print(f"WAD {wad} could not be installed!")
            print(f"Successfully installed {wad_count} WAD(s) to EmuNAND!")
        else:
            title = libWiiPy.title.Title()
            title.load_wad(open(input_path, "rb").read())
            emunand.install_title(title, skip_hash=skip_hash)
            print("Successfully installed WAD to EmuNAND!")

    # Code for if the --uninstall argument was passed.
    elif args.uninstall:
        input_str = args.uninstall
        if pathlib.Path(input_str).exists():
            title = libWiiPy.title.Title()
            title.load_wad(open(pathlib.Path(input_str), "rb").read())
            target_tid = title.tmd.title_id
        else:
            target_tid = args.install

        if len(target_tid) != 16:
            raise ValueError("Invalid Title ID! Title IDs must be 16 characters long.")

        emunand.uninstall_title(target_tid)

        print("Title uninstalled from EmuNAND!")
