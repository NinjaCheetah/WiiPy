# "commands/title/ciosbuild.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import io
import os
import xml.etree.ElementTree as ET
import pathlib
import libWiiPy
from modules.core import fatal_error


def build_cios(args):
    base_path = pathlib.Path(args.base)
    map_path = pathlib.Path(args.map)
    if args.modules:
        modules_path = pathlib.Path(args.modules)
    else:
        modules_path = pathlib.Path(os.getcwd())
    output_path = pathlib.Path(args.output)

    if not base_path.exists():
        fatal_error(f"The specified base IOS file \"{base_path}\" does not exist!")
    if not map_path.exists():
        fatal_error(f"The specified cIOS map file \"{map_path}\" does not exist!")
    if not modules_path.exists():
        fatal_error(f"The specified cIOS modules directory \"{modules_path}\" does not exist!")

    title = libWiiPy.title.Title()
    title.load_wad(open(base_path, 'rb').read())

    cios_tree = ET.parse(map_path)
    cios_root = cios_tree.getroot()

    # Iterate over all <ciosgroup> tags to find the cIOS that was requested, and return an error if it doesn't match
    # any of the groups in the provided map.
    target_cios = None
    for child in cios_root:
        cios = child.get("name")
        if args.cios_ver == cios:
            target_cios = child
            break
    if target_cios is None:
        fatal_error(f"The target cIOS \"{args.cios_ver}\" could not be found in the provided map!")

    # Iterate over all bases in the target cIOS to find a base that matches the provided WAD. If one is found, ensure
    # that the version of the base in the map matches the version of the IOS WAD.
    target_base = None
    provided_base = int(title.tmd.title_id[-2:], 16)
    for child in target_cios:
        base = int(child.get("ios"))
        if base == provided_base:
            target_base = child
            break
    if target_base is None:
        fatal_error(f"The provided base (IOS{provided_base}) doesn't match any bases found in the provided map!")
    base_version = int(target_base.get("version"))
    if title.tmd.title_version != base_version:
        fatal_error(f"The provided base (IOS{provided_base} v{title.tmd.title_version}) doesn't match the required "
                    f"version (v{base_version})!")
    print(f"Building cIOS \"{args.cios_ver}\" from base IOS{target_base.get('ios')} v{base_version}...")

    # We're ready to begin building the cIOS now. Find all the <content> tags that have <patch> tags, and then apply
    # the patches listed in them to the content.
    print("Patching existing modules...")
    for content in target_base.findall("content"):
        patches = content.findall("patch")
        if patches:
            cid = int(content.get("id"), 16)
            dec_content = title.get_content_by_cid(cid)
            content_index = title.content.get_index_from_cid(cid)
            with io.BytesIO(dec_content) as content_data:
                for patch in patches:
                    # Read patch info from the map. This requires some conversion since ciosmap files seem to use a
                    # comma-separated list of bytes.
                    offset = int(patch.get("offset"), 16)
                    original_data = b''
                    original_data_map = patch.get("originalbytes").split(",")
                    for byte in original_data_map:
                        original_data += bytes.fromhex(byte[2:])
                    new_data = b''
                    new_data_map = patch.get("newbytes").split(",")
                    for byte in new_data_map:
                        new_data += bytes.fromhex(byte[2:])
                    # Seek to the target offset and apply the patches. One last sanity check to ensure this
                    # original data exists.
                    if original_data in dec_content:
                        content_data.seek(offset)
                        content_data.write(new_data)
                    else:
                        fatal_error("An error occurred while patching! Please make sure your base IOS is valid.")
                content_data.seek(0x0)
                dec_content = content_data.read()
            # Set the content in the title to the newly-patched content, and set the type to normal.
            title.set_content(dec_content, content_index, content_type=libWiiPy.title.ContentType.NORMAL)

    # Next phase of cIOS building is to add the required extra modules.
    print("Adding required additional modules...")
    for content in target_base.findall("content"):
        target_module = content.get("module")
        if target_module is not None:
            target_index = int(content.get("tmdmoduleid"), 16)
            # The cIOS map supplies a Content ID to use for each additional module.
            cid = int(content.get("id"), 16)
            target_path = modules_path.joinpath(target_module + ".app")
            if not target_path.exists():
                fatal_error(f"A required module \"{target_module}\" could not be found!")
            # Check where this module belongs. If it's -1, add it to the end. If it's any other value, this module needs
            # to go at the index specified.
            new_module = target_path.read_bytes()
            if target_index == -1:
                title.add_content(new_module, cid, libWiiPy.title.ContentType.NORMAL)
            else:
                existing_module = title.get_content_by_index(target_index)
                existing_cid = title.content.content_records[target_index].content_id
                existing_type = title.content.content_records[target_index].content_type
                title.set_content(new_module, target_index, cid, libWiiPy.title.ContentType.NORMAL)
                title.add_content(existing_module, existing_cid, existing_type)

    # Last cIOS building step, we need to set the slot and version.
    slot = args.slot
    if 3 <= slot <= 255:
        tid = title.tmd.title_id[:-2] + f"{slot:02X}"
        title.set_title_id(tid)
    else:
        fatal_error(f"The specified slot \"{slot}\" is not valid!")
    try:
        title.set_title_version(args.version)
    except ValueError:
        fatal_error(f"The specified version \"{args.version}\" is not valid!")
    print(f"Set cIOS slot to \"{slot}\" and cIOS version to \"{args.version}\"!")

    # If this is a vWii cIOS, then we need to re-encrypt it with the Wii Common key so that it's installable from
    # within Wii mode.
    title_key_dec = title.ticket.get_title_key()
    title_key_common = libWiiPy.title.encrypt_title_key(title_key_dec, 0, title.tmd.title_id)
    title.ticket.title_key_enc = title_key_common
    title.ticket.common_key_index = 0

    # Ensure the WAD is fakesigned.
    title.fakesign()

    # Write the new cIOS to the specified output path.
    output_path.write_bytes(title.dump_wad())

    print(f"Successfully built cIOS \"{args.cios_ver}\"!")
