# "commands/nand/emunand.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import math
import pathlib
import libWiiPy
from modules.core import fatal_error


def handle_emunand_info(args):
    emunand = libWiiPy.nand.EmuNAND(args.emunand)
    # Basic info.
    print(f"EmuNAND Info")
    print(f"  Path: {str(emunand.emunand_root.absolute())}")
    is_vwii = False
    try:
        tmd = emunand.get_title_tmd("0000000100000002")
        is_vwii = bool(tmd.vwii)
        print(f"  System Menu Version: {libWiiPy.title.title_ver_dec_to_standard(tmd.title_version, '0000000100000002',
                                                                                 vwii=is_vwii)}")
    except FileNotFoundError:
        print(f"  System Menu Version: None")
    settings_path = emunand.title_dir.joinpath("00000001", "00000002", "data", "setting.txt")
    if settings_path.exists():
        settings = libWiiPy.nand.SettingTxt()
        settings.load(settings_path.read_bytes())
        print(f"  System Region: {settings.area}")
    else:
        print(f"  System Region: N/A")
    if is_vwii:
        print(f"  Type: vWii")
    else:
        print(f"  Type: Wii")
    categories = emunand.get_installed_titles()
    installed_count = 0
    for category in categories:
        if category.type != "00010000":
            for _ in category.titles:
                installed_count += 1
    print(f"  Installed Titles: {installed_count}")
    total_size = sum(file.stat().st_size for file in emunand.emunand_root.rglob('*'))
    total_size_blocks = math.ceil(total_size / 131072)
    print(f"  Space Used: {total_size_blocks} blocks ({round(total_size / 1048576, 2)} MB)")
    print("")

    installed_ioses = []
    installed_titles = []
    disc_titles = []
    for category in categories:
        if category.type == "00000001":
            ioses = []
            for title in category.titles:
                if title != "00000002":
                    ioses.append(int(title, 16))
            ioses.sort()
            installed_ioses = [f"00000001{i:08X}".upper() for i in ioses]
        elif category.type != "00010000":
            for title in category.titles:
                installed_titles.append(f"{category.type}{title}".upper())
        elif category.type == "00010000":
            for title in category.titles:
                if title != "48415A41":
                    disc_titles.append(f"{category.type}{title}".upper())

    print(f"System Titles:")
    for ios in installed_ioses:
        if ios[8:] in ["00000100", "00000101", "00000200", "00000201"]:
            if ios[8:] == "00000100":
                print(f"  BC ({ios.upper()})")
            elif ios[8:] == "00000101":
                print(f"  MIOS ({ios.upper()})")
            elif ios[8:] == "00000200":
                print(f"  BC-NAND ({ios.upper()})")
            elif ios[8:] == "00000201":
                print(f"  BC-WFS ({ios.upper()})")
            tmd = emunand.get_title_tmd(ios)
            print(f"    Version: {tmd.title_version}")
        else:
            print(f"  IOS{int(ios[-2:], 16)} ({ios.upper()})")
            tmd = emunand.get_title_tmd(ios)
            print(f"    Version: {tmd.title_version} ({tmd.title_version_converted})")
    print("")

    print(f"Installed Titles:")
    missing_ioses = []
    for title in installed_titles:
        ascii_tid = ""
        try:
            ascii_tid = (bytes.fromhex(title[8:].replace("00", "30"))).decode("ascii")
        except UnicodeDecodeError:
            pass
        if ascii_tid.isalnum():
            print(f"  {title.upper()} ({ascii_tid})")
        else:
            print(f"  {title.upper()}")
        tmd = emunand.get_title_tmd(f"{title}")
        print(f"    Version: {tmd.title_version}")
        print(f"    Required IOS: IOS{int(tmd.ios_tid[-2:], 16)} ({tmd.ios_tid.upper()})", end="", flush=True)
        if tmd.ios_tid.upper() not in installed_ioses:
            print(" *")
            if tmd.ios_tid not in missing_ioses:
                missing_ioses.append(tmd.ios_tid)
        else:
            print("")
    print("")

    if disc_titles:
        print(f"Save data was found for the following disc titles:")
        for disc in disc_titles:
            ascii_tid = ""
            try:
                ascii_tid = (bytes.fromhex(disc[8:].replace("00", "30"))).decode("ascii")
            except UnicodeDecodeError:
                pass
            if ascii_tid.isalnum():
                print(f"  {disc.upper()} ({ascii_tid})")
            else:
                print(f"  {disc.upper()}")
        print("")
    if missing_ioses:
        print(f"Some titles installed are missing their required IOS. These missing IOSes are marked with a * in the "
              f"title list above. If these IOSes are not installed, the titles requiring them will not launch. The "
              f"IOSes required but not installed are:")
        for missing in missing_ioses:
            print(f"  IOS{int(missing[-2:], 16)} ({missing.upper()})")
        print("Missing IOSes can be automatically installed using the install-missing command.")


def handle_emunand_install_missing(args):
    # Get an index of all installed titles, and check their required IOSes. Then compare the required IOSes with the
    # installed IOSes, and build a list of IOSes we need to obtain.
    emunand = libWiiPy.nand.EmuNAND(args.emunand)
    if args.vwii:
        is_vwii = True
    else:
        # Try and detect a vWii System Menu, if one is installed, so that we get vWii IOSes if they're needed.
        try:
            tmd = emunand.get_title_tmd("0000000100000002")
            is_vwii = bool(tmd.vwii)
        except FileNotFoundError:
            is_vwii = False
    categories = emunand.get_installed_titles()
    installed_ioses = []
    installed_titles = []
    for category in categories:
        if category.type == "00000001":
            for title in category.titles:
                if title == "00000002":
                    installed_titles.append(f"{category.type}{title}")
                else:
                    installed_ioses.append(f"{category.type}{title}")
        elif category.type != "00010000":
            for title in category.titles:
                installed_titles.append(f"{category.type}{title}")
    missing = []
    for title in installed_titles:
        tmd = emunand.get_title_tmd(title)
        if tmd.ios_tid.upper() not in installed_ioses:
            if tmd.ios_tid not in missing:
                missing.append(int(tmd.ios_tid[8:], 16))
    missing.sort()
    if is_vwii:
        missing_ioses = [f"00000007{i:08X}" for i in missing]
    else:
        missing_ioses = [f"00000001{i:08X}" for i in missing]
    if not missing_ioses:
        print(f"All necessary IOSes are already installed!")
        return
    print(f"Missing IOSes:")
    for ios in missing_ioses:
        print(f"  IOS{int(ios[-2:], 16)} ({ios.upper()})")
    print("")
    # Download and then install each missing IOS to the EmuNAND.
    for ios in missing_ioses:
        print(f"Downloading IOS{int(ios[-2:], 16)} ({ios.upper()})...")
        title = libWiiPy.title.download_title(ios)
        print(f"  Installing IOS{int(ios[-2:], 16)} ({ios.upper()}) v{title.tmd.title_version}...")
        emunand.install_title(title)
        print(f"  Installed IOS{int(ios[-2:], 16)} ({ios.upper()}) v{title.tmd.title_version}!")
    print(f"\nAll missing IOSes have been installed!")


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
            fatal_error("The specified WAD file does not exist!")

        if input_path.is_dir():
            wad_files = list(input_path.glob("*.[wW][aA][dD]"))
            if not wad_files:
                fatal_error("No WAD files were found in the provided input directory!")
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
            title.load_wad(pathlib.Path(input_str).read_bytes())
            target_tid = title.tmd.title_id
        else:
            target_tid = input_str

        if len(target_tid) != 16:
            fatal_error("The provided Title ID is invalid! Title IDs must be 16 characters long.")

        emunand.uninstall_title(target_tid.lower())

        print("Title uninstalled from EmuNAND!")
