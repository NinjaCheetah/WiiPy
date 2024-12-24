# "commands/title/info.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import binascii
import pathlib
import re
import libWiiPy
from modules.core import fatal_error


def _print_tmd_info(tmd: libWiiPy.title.TMD, signed=None):
    # Get all important keys from the TMD and print them out nicely.
    print("Title Info")
    ascii_tid = ""
    try:
        ascii_tid = (bytes.fromhex(tmd.title_id[8:].replace("00", "30"))).decode("ascii")
    except UnicodeDecodeError:
        pass
    pattern = r"^[a-z0-9!@#$%^&*]{4}$"
    if re.fullmatch(pattern, ascii_tid, re.IGNORECASE):
        print(f"  Title ID: {tmd.title_id.upper()} ({ascii_tid})")
    else:
        print(f"  Title ID: {tmd.title_id.upper()}")
    # This type of version number really only applies to the System Menu and IOS.
    if tmd.title_id.startswith("00000001"):
        if tmd.title_id == "0000000100000001":
            print(f"  Title Version: {tmd.title_version} (boot2v{tmd.title_version})")
        else:
            print(f"  Title Version: {tmd.title_version} ({tmd.title_version_converted})")
    else:
        print(f"  Title Version: {tmd.title_version}")
    print(f"  TMD Version: {tmd.tmd_version}")
    # IOSes just have an all-zero TID, so don't bothering showing that.
    if tmd.ios_tid == "0000000000000000":
        print(f"  Required IOS: N/A")
    elif tmd.title_id == "0000000100000001":
        pass
    else:
        print(f"  Required IOS: IOS{int(tmd.ios_tid[-2:], 16)} ({tmd.ios_tid.upper()})")
    if tmd.signature_issuer.find("CP00000004") != -1:
        print(f"  Certificate: CP00000004 (Retail)")
        print(f"  Certificate Issuer: Root-CA00000001 (Retail)")
    elif tmd.signature_issuer.find("CP00000007") != -1:
        print(f"  Certificate: CP00000007 (Development)")
        print(f"  Certificate Issuer: Root-CA00000002 (Development)")
    elif tmd.signature_issuer.find("CP10000000") != -1:
        print(f"  Certificate: CP10000000 (Arcade)")
        print(f"  Certificate Issuer: Root-CA10000000 (Arcade)")
    else:
        print(f"  Certificate Info: {tmd.signature_issuer} (Unknown)")
    if tmd.title_id == "0000000100000002":
        match tmd.title_version_converted[-1:]:
            case "U":
                region = "USA"
            case "E":
                region = "EUR"
            case "J":
                region = "JPN"
            case "K":
                region = "KOR"
            case _:
                region = "None"
    elif tmd.get_title_type() == "System":
        region = "None"
    else:
        region = tmd.get_title_region()
    print(f"  Region: {region}")
    print(f"  Title Type: {tmd.get_title_type()}")
    print(f"  vWii Title: {bool(tmd.vwii)}")
    print(f"  DVD Video Access: {tmd.get_access_right(tmd.AccessFlags.DVD_VIDEO)}")
    print(f"  AHB Access: {tmd.get_access_right(tmd.AccessFlags.AHB)}")
    if signed is not None:
        print(f"  Signed: {signed}")
    print(f"  Fakesigned: {tmd.get_is_fakesigned()}")
    # Iterate over the content and print their details.
    print("\nContent Info")
    print(f"  Total Contents: {tmd.num_contents}")
    print(f"  Boot Content Index: {tmd.boot_index}")
    print("  Content Records:")
    for content in tmd.content_records:
        print(f"    Content Index: {content.index}")
        print(f"      Content ID: " + f"{content.content_id:08X}".lower())
        print(f"      Content Type: {tmd.get_content_type(content.index)}")
        print(f"      Content Size: {content.content_size} bytes")
        print(f"      Content Hash: {content.content_hash.decode()}")


def _print_ticket_info(ticket: libWiiPy.title.Ticket, signed=None):
    # Get all important keys from the TMD and print them out nicely.
    print(f"Ticket Info")
    ascii_tid = ""
    try:
        ascii_tid = str(bytes.fromhex(ticket.title_id.decode()[8:].replace("00", "30")).decode("ascii"))
    except UnicodeDecodeError or binascii.Error:
        pass
    pattern = r"^[a-z0-9!@#$%^&*]{4}$"
    if re.fullmatch(pattern, ascii_tid, re.IGNORECASE):
        print(f"  Title ID: {ticket.title_id.decode().upper()} ({ascii_tid})")
    else:
        print(f"  Title ID: {ticket.title_id.decode().upper()}")
    # This type of version number really only applies to the System Menu and IOS.
    if ticket.title_id.decode().startswith("00000001"):
        if ticket.title_id.decode() == "0000000100000001":
            print(f"  Title Version: {ticket.title_version} (boot2v{ticket.title_version})")
        else:
            print(f"  Title Version: {ticket.title_version} "
                  f"({libWiiPy.title.title_ver_dec_to_standard(ticket.title_version, ticket.title_id.decode())})")
    else:
        print(f"  Title Version: {ticket.title_version}")
    print(f"  Ticket Version: {ticket.ticket_version}")
    if ticket.signature_issuer.find("XS00000003") != -1:
        print(f"  Certificate: XS00000003 (Retail)")
        print(f"  Certificate Issuer: Root-CA00000001 (Retail)")
    elif ticket.signature_issuer.find("XS00000006") != -1:
        print(f"  Certificate: XS00000006 (Development)")
        print(f"  Certificate Issuer: Root-CA00000002 (Development)")
    else:
        print(f"  Certificate Info: {ticket.signature_issuer} (Unknown)")
    match ticket.common_key_index:
        case 0:
            if ticket.is_dev:
                key = "Common (Development)"
            else:
                key = "Common (Retail)"
        case 1:
            key = "Korean"
        case 2:
            key = "vWii"
        case _:
            key = "Unknown (Likely Common)"
    print(f"  Decryption Key: {key}")
    print(f"  Title Key (Encrypted): {binascii.hexlify(ticket.title_key_enc).decode()}")
    print(f"  Title Key (Decrypted): {binascii.hexlify(ticket.get_title_key()).decode()}")
    if signed is not None:
        print(f"  Signed: {signed}")
    print(f"  Fakesigned: {ticket.get_is_fakesigned()}")


def _print_wad_info(title: libWiiPy.title.Title):
    print(f"WAD Info")
    banner_data = title.get_content_by_index(0)
    banner_u8 = libWiiPy.archive.U8Archive()
    try:
        banner_u8.load(banner_data)
        if banner_u8.imet_header.magic != "":
            channel_title = banner_u8.imet_header.get_channel_names(banner_u8.imet_header.LocalizedTitles.TITLE_ENGLISH)
            print(f"  Channel Name: {channel_title}")
    except TypeError:
        pass
    match title.wad.wad_type:
        case "Is":
            print(f"  WAD Type: Standard Installable")
        case "ib":
            print(f"  WAD Type: boot2")
        case _:
            print(f"  WAD Type: Unknown ({title.wad.wad_type})")
    min_size_blocks = title.get_title_size_blocks()
    max_size_blocks = title.get_title_size_blocks(absolute=True)
    if min_size_blocks == max_size_blocks:
        print(f"  Installed Size: {min_size_blocks} blocks")
    else:
        print(f"  Installed Size: {min_size_blocks}-{max_size_blocks} blocks")
    min_size = round(title.get_title_size() / 1048576, 2)
    max_size = round(title.get_title_size(absolute=True) / 1048576, 2)
    if min_size == max_size:
        print(f"  Installed Size (MB): {min_size} MB")
    else:
        print(f"  Installed Size (MB): {min_size}-{max_size} MB")
    print(f"  Has Meta/Footer: {bool(title.wad.wad_meta_size)}")
    print(f"  Has CRL: {bool(title.wad.wad_crl_size)}")
    signed = title.get_is_signed()
    if signed:
        signing_str = "Valid (Unmodified)"
    elif title.get_is_fakesigned():
        signing_str = "Fakesigned"
    else:
        signing_str = "Invalid (Modified)"
    print(f"  Signing Status: {signing_str}")
    print("")
    _print_ticket_info(title.ticket, signed)
    print("")
    _print_tmd_info(title.tmd, signed)


def handle_info(args):
    input_path = pathlib.Path(args.input)

    if not input_path.exists():
        fatal_error(f"The specified input file \"{input_path}\" does not exist!")

    if (input_path.suffix.lower() == ".tmd" or input_path.name == "tmd.bin" or
            re.match("tmd.?[0-9]*", input_path.name)):
        tmd = libWiiPy.title.TMD()
        tmd.load(input_path.read_bytes())
        _print_tmd_info(tmd)
    elif input_path.suffix.lower() == ".tik" or input_path.name == "ticket.bin" or input_path.name == "cetk":
        tik = libWiiPy.title.Ticket()
        tik.load(input_path.read_bytes())
        _print_ticket_info(tik)
    elif input_path.suffix.lower() == ".wad":
        title = libWiiPy.title.Title()
        title.load_wad(input_path.read_bytes())
        _print_wad_info(title)
    else:
        # Try file types that have a matchable magic number if we can't tell the easy way.
        magic_number = open(input_path, "rb").read(8)
        if magic_number == b'\x00\x00\x00\x20\x49\x73\x00\x00' or magic_number == b'\x00\x00\x00\x20\x69\x62\x00\x00':
            title = libWiiPy.title.Title()
            title.load_wad(input_path.read_bytes())
            _print_wad_info(title)
            return
        else:
            fatal_error("This does not appear to be a supported file type! No info can be provided.")
