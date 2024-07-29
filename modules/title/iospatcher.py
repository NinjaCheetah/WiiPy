# "modules/title/iospatcher.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def patch_fakesigning(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying fakesigning patch... ", end="", flush=True)
    count = ios_patcher.patch_fakesigning()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def patch_es_identify(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying ES_Identify access patch... ", end="", flush=True)
    count = ios_patcher.patch_es_identify()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def patch_nand_access(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying /dev/flash access patch... ", end="", flush=True)
    count = ios_patcher.patch_nand_access()
    if count == 1:
        print(f"{count} patch applied")
    else:
        print(f"{count} patches applied")
    return count


def patch_version_downgrading(ios_patcher: libWiiPy.title.IOSPatcher) -> int:
    print("Applying version downgrading patch... ", end="", flush=True)
    count = ios_patcher.patch_version_downgrading()
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

    if args.slot is not None:
        slot = args.slot
        if 3 <= slot <= 255:
            tid = title.tmd.title_id[:-2] + f"{slot:02X}"
            title.set_title_id(tid)

    ios_patcher = libWiiPy.title.IOSPatcher()
    ios_patcher.load(title)

    if args.all is True:
        patch_count += patch_fakesigning(ios_patcher)
        patch_count += patch_es_identify(ios_patcher)
        patch_count += patch_nand_access(ios_patcher)
        patch_count += patch_version_downgrading(ios_patcher)
    else:
        if args.fakesigning is True:
            patch_count += patch_fakesigning(ios_patcher)
        if args.es_identify is True:
            patch_count += patch_es_identify(ios_patcher)
        if args.nand_access is True:
            patch_count += patch_nand_access(ios_patcher)
        if args.version_downgrading is True:
            patch_count += patch_version_downgrading(ios_patcher)

    print(f"\nTotal patches applied: {patch_count}")

    if patch_count == 0 and args.version is None and args.slot is None:
        raise ValueError("No patches were applied! Please select patches to apply, and ensure that selected patches are"
                         " compatible with this IOS.")

    if patch_count > 0 or args.version is not None or args.slot is not None:
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
