# "modules/title/emunand.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_emunand_title(args):
    emunand = libWiiPy.nand.EmuNAND(args.emunand)
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
            target_tid = input_str

        if len(target_tid) != 16:
            raise ValueError("Invalid Title ID! Title IDs must be 16 characters long.")

        emunand.uninstall_title(target_tid)

        print("Title uninstalled from EmuNAND!")


def handle_emunand_gensetting(args):
    # Validate the provided SN. It should be 2 or 3 letters followed by 9 numbers.
    if len(args.serno) != 11 and len(args.serno) != 12:
        raise ValueError("The provided Serial Number is not valid!")
    try:
        int(args.serno[-9:])
    except ValueError:
        raise ValueError("The provided Serial Number is not valid!")
    prefix = args.serno[:-9]
    # Detect the console revision based on the SN.
    match prefix[0].upper():
        case "L":
            revision = "RVL-001"
        case "K":
            revision = "RVL-101"
        case "H":
            revision = "RVL-201"
        case _:
            revision = "RVL-001"
    # Validate the region, and then validate the SN based on the region. USA has a two-letter prefix for a total length
    # of 11 characters, while other regions have a three-letter prefix for a total length of 12 characters.
    valid_regions = ["USA", "EUR", "JPN", "KOR"]
    if args.region not in valid_regions:
        raise ValueError("The provided region is not valid!")
    if len(prefix) == 2 and args.region != "USA":
        raise ValueError("The provided region does not match the provided Serial Number!")
    elif len(prefix) == 3 and args.region == "USA":
        raise ValueError("The provided region does not match the provided Serial Number!")
    # Get the values for VIDEO and GAME.
    video = ""
    game = ""
    match args.region:
        case "USA":
            video = "NTSC"
            game = "US"
        case "EUR":
            video = "PAL"
            game = "EU"
        case "JPN":
            video = "NTSC"
            game = "JP"
        case "KOR":
            video = "NTSC"
            game = "KR"
    # Create a new SettingTxt object and load the settings into it.
    setting = libWiiPy.nand.SettingTxt()
    setting.area = args.region
    setting.model = f"{revision}({args.region})"
    setting.dvd = 0
    setting.mpch = "0x7FFE"
    setting.code = prefix
    setting.serial_number = args.serno[-9:]
    setting.video = video
    setting.game = game
    # Write out the setting.txt file.
    open("setting.txt", "wb").write(setting.dump())
