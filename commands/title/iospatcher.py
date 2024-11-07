# "commands/title/iospatcher.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def _patch_fakesigning(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying fakesigning patch... ", end="", flush=True)
    count = ios_patcher.patch_fakesigning()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def _patch_es_identify(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying ES_Identify access patch... ", end="", flush=True)
    count = ios_patcher.patch_es_identify()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def _patch_nand_access(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying /dev/flash access patch... ", end="", flush=True)
    count = ios_patcher.patch_nand_access()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def _patch_version_downgrading(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying version downgrading patch... ", end="", flush=True)
    count = ios_patcher.patch_version_downgrading()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def _patch_drive_inquiry(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("\n/!\\ WARNING! /!\\\n"
          "This drive inquiry patch is experimental, and may introduce unexpected side effects on some consoles.\n")
    print("Applying drive inquiry patch... ", end="", flush=True)
    count = ios_patcher.patch_drive_inquiry()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def handle_iospatch(args):
    input_path = pathlib.Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    title = libWiiPy.title.Title()
    title.load_wad(open(input_path, "rb").read())

    tid = title.tmd.title_id
    if tid[:8] != "00000001" or tid[8:] == "00000001" or tid[8:] == "00000002":
        raise ValueError("This WAD does not appear to contain an IOS! Patching cannot continue.")

    patch_count = 0

    if args.version is not None:
        title.set_title_version(args.version)
        print(f"Title version set to {args.version}!")

    if args.slot is not None:
        slot = args.slot
        if 3 <= slot <= 255:
            tid = title.tmd.title_id[:-2] + f"{slot:02X}"
            title.set_title_id(tid)
            print(f"IOS slot set to {slot}!")

    ios_patcher = libWiiPy.title.IOSPatcher()
    ios_patcher.load(title)

    if args.all is True:
        patch_count += _patch_fakesigning(ios_patcher)
        patch_count += _patch_es_identify(ios_patcher)
        patch_count += _patch_nand_access(ios_patcher)
        patch_count += _patch_version_downgrading(ios_patcher)
    else:
        if args.fakesigning is True:
            patch_count += _patch_fakesigning(ios_patcher)
        if args.es_identify is True:
            patch_count += _patch_es_identify(ios_patcher)
        if args.nand_access is True:
            patch_count += _patch_nand_access(ios_patcher)
        if args.version_downgrading is True:
            patch_count += _patch_version_downgrading(ios_patcher)
        if args.drive_inquiry is True:
            patch_count += _patch_drive_inquiry(ios_patcher)

    print(f"\nTotal patches applied: {patch_count}")

    if patch_count == 0 and args.version is None and args.slot is None:
        raise ValueError("No patches were applied! Please select patches to apply, and ensure that selected patches are"
                         " compatible with this IOS.")

    if patch_count > 0 or args.version is not None or args.slot is not None:
        # Set patched content to non-shared if that argument was passed.
        if args.no_shared:
            ios_patcher.title.content.content_records[ios_patcher.es_module_index].content_type = 1
            if ios_patcher.dip_module_index != -1:
                ios_patcher.title.content.content_records[ios_patcher.dip_module_index].content_type = 1

        ios_patcher.title.fakesign()  # Signature is broken anyway, so fakesign for maximum installation openings
        if args.output is not None:
            output_path = pathlib.Path(args.output)
            output_file = open(output_path, "wb")
            output_file.write(ios_patcher.title.dump_wad())
            output_file.close()
        else:
            output_file = open(input_path, "wb")
            output_file.write(ios_patcher.title.dump_wad())
            output_file.close()

    print("IOS successfully patched!")
