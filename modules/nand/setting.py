# "modules/nand/setting.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_setting_decrypt(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(input_path.stem + "_dec" + input_path.suffix)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    # Load and decrypt the provided file.
    setting = libWiiPy.nand.SettingTxt()
    setting.load(open(input_path, "rb").read())
    # Write out the decrypted data.
    open(output_path, "w").write(setting.dump_decrypted())
    print("Successfully decrypted setting.txt!")


def handle_setting_encrypt(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path("setting.txt")

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    # Load and encrypt the provided file.
    setting = libWiiPy.nand.SettingTxt()
    setting.load_decrypted(open(input_path, "r").read())
    # Write out the encrypted data.
    open(output_path, "wb").write(setting.dump())
    print("Successfully encrypted setting.txt!")


def handle_setting_gen(args):
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
    print(f"Successfully created setting.txt for console with serial number {args.serno}!")
