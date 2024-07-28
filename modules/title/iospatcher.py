# "modules/title/iospatcher.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_iospatch(args):
    input_path = pathlib.Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    title = libWiiPy.title.Title()
    title.load_wad(open(input_path, "rb").read())

    tid = title.tmd.title_id
    if tid[:8] != "00000001" or tid[8:] == "00000001" or tid[8:] == "00000002":
        raise ValueError("This WAD does not appear to contain an IOS! Patching cannot continue.")

    patches_applied = False

    if args.version is not None:
        title.set_title_version(args.version)
        patches_applied = True

    if args.slot is not None:
        slot = args.slot
        if 3 <= slot <= 255:
            tid = title.tmd.title_id[:-2] + f"{slot:02X}"
            title.set_title_id(tid)
        patches_applied = True

    ios_patcher = libWiiPy.title.IOSPatcher()
    ios_patcher.load(title)

    if args.all is True:
        ios_patcher.patch_all()
        patches_applied = True
    else:
        if args.fakesigning is True:
            ios_patcher.patch_fakesigning()
            patches_applied = True
        if args.es_identify is True:
            ios_patcher.patch_es_identify()
            patches_applied = True
        if args.nand_access is True:
            ios_patcher.patch_nand_access()
            patches_applied = True
        if args.version_patch is True:
            ios_patcher.patch_version_patch()
            patches_applied = True

    if not patches_applied:
        raise ValueError("No patches were selected! Please select patches to apply.")

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
