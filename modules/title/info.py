# "modules/title/info.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def _print_tmd_info(tmd: libWiiPy.title.TMD):
    # Get all important keys from the TMD and print them out nicely.
    print("Title Info")
    print(f"  Title ID: {tmd.title_id}")
    # This type of version number really only applies to the System Menu and IOS.
    if tmd.title_id[:8] == "00000001":
        print(f"  Title Version: {tmd.title_version} ({tmd.title_version_converted})")
    else:
        print(f"  Title Version: {tmd.title_version}")
    if tmd.ios_tid == "0000000000000000":
        print(f"  IOS Version: N/A")
    else:
        print(f"  Required IOS: IOS{int(tmd.ios_tid[-2:], 16)} ({tmd.ios_tid})")
    print(f"  Region: {tmd.get_title_region()}")
    print(f"  Title Type: {tmd.get_title_type()}")
    print(f"  vWii Title: {bool(tmd.vwii)}")
    print(f"  DVD Video Access: {tmd.get_access_right(tmd.AccessFlags.DVD_VIDEO)}")
    print(f"  AHB Access: {tmd.get_access_right(tmd.AccessFlags.AHB)}")
    print(f"  Fakesigned: {tmd.get_is_fakesigned()}")
    # Iterate over the content and print their details.
    print("\nContent Info")
    print(f"Total Contents: {tmd.num_contents}")
    for content in tmd.content_records:
        print(f"  Content Index: {content.index}")
        print(f"    Content ID: " + f"{content.content_id:08X}".lower())
        print(f"    Content Type: {tmd.get_content_type(content.index)}")
        print(f"    Content Size: {content.content_size} bytes")
        print(f"    Content Hash: {content.content_hash.decode()}")


def handle_info(args):
    input_path = pathlib.Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if input_path.suffix.lower() == ".tmd":
        tmd = libWiiPy.title.TMD()
        tmd.load(open(input_path, "rb").read())
        _print_tmd_info(tmd)
    #elif input_path.suffix.lower() == ".tik":
    #    tik = libWiiPy.title.Ticket()
    #    tik.load(open(input_path, "rb").read())
    #elif input_path.suffix.lower() == ".wad":
    #    title = libWiiPy.title.Title()
    #    title.load_wad(open(input_path, "rb").read())
    else:
        raise TypeError("This does not appear to be a TMD, Ticket, or WAD! No info can be provided.")
