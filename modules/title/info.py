# "modules/title/info.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import binascii
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
    print(f"  TMD Version: {tmd.tmd_version}")
    # IOSes just have an all-zero TID, so don't bothering showing that.
    if tmd.ios_tid == "0000000000000000":
        print(f"  Required IOS: N/A")
    else:
        print(f"  Required IOS: IOS{int(tmd.ios_tid[-2:], 16)} ({tmd.ios_tid})")
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
    elif tmd.title_id[:8] == "00000001":
        region = "None"
    else:
        region = tmd.get_title_region()
    print(f"  Region: {region}")
    print(f"  Title Type: {tmd.get_title_type()}")
    print(f"  vWii Title: {bool(tmd.vwii)}")
    print(f"  DVD Video Access: {tmd.get_access_right(tmd.AccessFlags.DVD_VIDEO)}")
    print(f"  AHB Access: {tmd.get_access_right(tmd.AccessFlags.AHB)}")
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


def _print_ticket_info(ticket: libWiiPy.title.Ticket):
    # Get all important keys from the TMD and print them out nicely.
    print(f"Ticket Info")
    print(f"  Title ID: {ticket.title_id.decode()}")
    # This type of version number really only applies to the System Menu and IOS.
    if ticket.title_id.decode()[:8] == "00000001":
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
            key = "Common"
        case 1:
            key = "Korean"
        case 2:
            key = "vWii"
        case _:
            key = "Unknown (Likely Common)"
    print(f"  Decryption Key: {key}")
    print(f"  Title Key (Encrypted): {binascii.hexlify(ticket.title_key_enc).decode()}")
    print(f"  Title Key (Decrypted): {binascii.hexlify(ticket.get_title_key()).decode()}")


def _print_wad_info(title: libWiiPy.title.Title):
    print(f"WAD Info")
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
    print("")
    _print_ticket_info(title.ticket)
    print("")
    _print_tmd_info(title.tmd)


def handle_info(args):
    input_path = pathlib.Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if input_path.suffix.lower() == ".tmd":
        tmd = libWiiPy.title.TMD()
        tmd.load(open(input_path, "rb").read())
        _print_tmd_info(tmd)
    elif input_path.suffix.lower() == ".tik":
        tik = libWiiPy.title.Ticket()
        tik.load(open(input_path, "rb").read())
        _print_ticket_info(tik)
    elif input_path.suffix.lower() == ".wad":
        title = libWiiPy.title.Title()
        title.load_wad(open(input_path, "rb").read())
        _print_wad_info(title)
    else:
        raise TypeError("This does not appear to be a TMD, Ticket, or WAD! No info can be provided.")
