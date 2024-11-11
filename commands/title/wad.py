# "commands/title/wad.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
from random import randint
import libWiiPy
from modules.core import fatal_error


def handle_wad_add(args):
    input_path = pathlib.Path(args.input)
    content_path = pathlib.Path(args.content)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        fatal_error(f"The specified WAD file \"{input_path}\" does not exist!")
    if not content_path.exists():
        fatal_error(f"The specified content file \"{content_path}\" does not exist!")

    title = libWiiPy.title.Title()
    title.load_wad(input_path.read_bytes())
    content_data = content_path.read_bytes()

    # Prepare the CID so it's ready when we go to add this content to the WAD.
    # We need to both validate that this is a real CID, and also that it isn't already taken by another content.
    if args.cid is not None:
        if len(args.cid) != 8:
            fatal_error("The specified Content ID is not valid!")
        target_cid = int(args.cid, 16)
        for record in title.content.content_records:
            if target_cid == record.content_id:
                fatal_error("The specified Content ID is already in use by this title!")
        print(f"Using provided Content ID \"{target_cid:08X}\".")
    # If we weren't given a CID, then we need to randomly assign one, and ensure it isn't being used.
    else:
        used_cids = []
        for record in title.content.content_records:
            used_cids.append(record.content_id)
        target_cid = randint(0, 0x000000FF)
        while target_cid in used_cids:
            target_cid = randint(0, 0x000000FF)
        print(f"Using randomly assigned Content ID \"{target_cid:08X}\" since none were provided.")

    # Get the type of the new content.
    if args.type is not None:
        match str.lower(args.type):
            case "normal":
                target_type = libWiiPy.title.ContentType.NORMAL
            case "shared":
                target_type = libWiiPy.title.ContentType.SHARED
            case "dlc":
                target_type = libWiiPy.title.ContentType.DLC
            case _:
                fatal_error(f"The provided content type \"{args.type}\" is not valid!")
    else:
        target_type = libWiiPy.title.ContentType.NORMAL

    # Call add_content to add our new content with the set parameters.
    title.add_content(content_data, target_cid, target_type)

    # Auto fakesign because we've edited the title.
    title.fakesign()
    output_path.write_bytes(title.dump_wad())

    print(f"Successfully added new content with Content ID \"{target_cid:08X}\" and type \"{target_type.name}\"!")


def handle_wad_convert(args):
    input_path = pathlib.Path(args.input)
    if args.dev:
        target = "development"
    elif args.retail:
        target = "retail"
    elif args.vwii:
        target = "vWii"
    else:
        fatal_error("No valid encryption target was specified!")

    if args.output is None:
        match target:
            case "development":
                output_path = pathlib.Path(input_path.stem + "_dev" + input_path.suffix)
            case "retail":
                output_path = pathlib.Path(input_path.stem + "_retail" + input_path.suffix)
            case "vWii":
                output_path = pathlib.Path(input_path.stem + "_vWii" + input_path.suffix)
            case _:
                fatal_error("No valid encryption target was specified!")
    else:
        output_path = pathlib.Path(args.output)

    if not input_path.exists():
        fatal_error(f"The specified WAD file \"{input_path}\" does not exist!")

    title = libWiiPy.title.Title()
    title.load_wad(input_path.read_bytes())
    # First, verify that this WAD isn't already the type we're trying to convert to.
    if title.ticket.is_dev and target == "development":
        fatal_error("This is already a development WAD!")
    elif not title.ticket.is_dev and not title.tmd.vwii and target == "retail":
        fatal_error("This is already a retail WAD!")
    elif not title.ticket.is_dev and title.tmd.vwii and target == "vWii":
        fatal_error("This is already a vWii WAD!")
    # Get the current type to display later.
    if title.ticket.is_dev:
        source = "development"
    elif title.tmd.vwii:
        source = "vWii"
    else:
        source = "retail"
    # Extract the Title Key so it can be re-encrypted with the correct key later.
    title_key = title.ticket.get_title_key()
    title_key_new = None
    if target == "development":
        # Set the development signature info.
        title.ticket.signature_issuer = "Root-CA00000002-XS00000006" + title.ticket.signature_issuer[26:]
        title.tmd.signature_issuer = "Root-CA00000002-CP00000007" + title.tmd.signature_issuer[26:]
        # Re-encrypt the title key with the dev key, and set that in the Ticket.
        title_key_new = libWiiPy.title.encrypt_title_key(title_key, 0, title.ticket.title_id, True)
        title.ticket.common_key_index = 0
    else:
        # Set the retail signature info.
        title.ticket.signature_issuer = "Root-CA00000001-XS00000003" + title.ticket.signature_issuer[26:]
        title.tmd.signature_issuer = "Root-CA00000001-CP00000004" + title.tmd.signature_issuer[26:]
        if target == "retail":
            title_key_new = libWiiPy.title.encrypt_title_key(title_key, 0, title.ticket.title_id, False)
            title.ticket.common_key_index = 0
        elif target == "vWii":
            title_key_new = libWiiPy.title.encrypt_title_key(title_key, 2, title.ticket.title_id, False)
            title.ticket.common_key_index = 2
    title.ticket.title_key_enc = title_key_new
    title.fakesign()
    output_path.write_bytes(title.dump_wad())
    print(f"Successfully converted {source} WAD to {target} WAD \"{output_path.name}\"!")


def handle_wad_pack(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    # Make sure input path both exists and is a directory. Separate checks because this provides more relevant
    # errors than just a NotADirectoryError if the actual issue is that there's nothing at all.
    if not input_path.exists():
        fatal_error(f"The specified input directory \"{input_path}\" does not exist!")
    if not input_path.is_dir():
        fatal_error(f"The specified input path \"{input_path}\" is not a directory!")

    # Get a list of all files ending in .tmd, and then make sure that that list has *only* 1 entry. More than 1
    # means we can't pack a WAD because we couldn't really tell which TMD is intended for this WAD.
    tmd_list = list(input_path.glob('*.[tT][mM][dD]'))
    if len(tmd_list) > 1:
        fatal_error("More than one TMD file was found! Only one TMD can be packed into a WAD.")
    elif len(tmd_list) == 0:
        fatal_error("No TMD file was found! Cannot pack WAD.")
    tmd_file = pathlib.Path(tmd_list[0])

    # Repeat the same process as above for all .tik files.
    ticket_list = list(input_path.glob('*.[tT][iI][kK]'))
    if len(ticket_list) > 1:
        fatal_error("More than one Ticket file was found! Only one Ticket can be packed into a WAD.")
    elif len(ticket_list) == 0:
        fatal_error("No Ticket file was found! Cannot pack WAD.")
    ticket_file = pathlib.Path(ticket_list[0])

    # And one more time for all .cert files.
    cert_list = list(input_path.glob('*.[cC][eE][rR][tT]'))
    if len(cert_list) > 1:
        fatal_error("More than one certificate file was found! Only one certificate can be packed into a WAD.")
    elif len(cert_list) == 0:
        fatal_error("No certificate file was found! Cannot pack WAD.")
    cert_file = pathlib.Path(cert_list[0])

    # Make sure that there's at least one content to pack.
    content_files = list(input_path.glob("*.[aA][pP][pP]"))
    if not content_files:
        fatal_error("No content files were found! Cannot pack WAD.")

    # Open the output file, and load all the component files that we've now verified we have into a libWiiPy Title()
    # object.
    title = libWiiPy.title.Title()
    title.load_tmd(tmd_file.read_bytes())
    title.load_ticket(ticket_file.read_bytes())
    title.wad.set_cert_data(cert_file.read_bytes())
    # Footers are not super common and are not required, so we don't care about one existing until we get to
    # the step where we'd pack it.
    footer_file = pathlib.Path(list(input_path.glob("*.[fF][oO][oO][tT][eE][rR]"))[0])
    if footer_file.exists():
        title.wad.set_meta_data(footer_file.read_bytes())
    # Method to ensure that the title's content records match between the TMD() and ContentRegion() objects.
    title.load_content_records()
    # Sort the contents based on the records. May still be kinda hacky.
    content_indices = []
    for record in title.content.content_records:
        content_indices.append(record.index)
    content_files_ordered = []
    for _ in content_files:
        content_files_ordered.append(None)
    for index in range(len(content_files)):
        target_index = content_indices.index(int(content_files[index].stem, 16))
        content_files_ordered[target_index] = content_files[index]
    # Iterate over every file in the content_files list, and set them in the Title().
    for index in range(title.content.num_contents):
        dec_content = content_files_ordered[index].read_bytes()
        title.set_content(dec_content, index)

    # Fakesign the TMD and Ticket using the trucha bug, if enabled. This is built-in in libWiiPy v0.4.1+.
    if args.fakesign:
        title.fakesign()
    output_path.write_bytes(title.dump_wad())

    print("WAD file packed!")


def handle_wad_remove(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        fatal_error(f"The specified WAD file \"{input_path}\" does not exist!")

    title = libWiiPy.title.Title()
    title.load_wad(input_path.read_bytes())

    # TODO: see if this implementation is problematic now
    if args.index is not None:
        # List indices in the title, and ensure that the target content index exists.
        valid_indices = []
        for record in title.content.content_records:
            valid_indices.append(record.index)
        if args.index not in valid_indices:
            fatal_error("The specified content index could not be found in this title!")
        title.content.remove_content_by_index(args.index)
        # Auto fakesign because we've edited the title.
        title.fakesign()
        output_path.write_bytes(title.dump_wad())
        print(f"Removed content at content index {args.index}!")

    elif args.cid is not None:
        if len(args.cid) != 8:
            fatal_error("The specified Content ID is not valid!")
        target_cid = int(args.cid, 16)
        # List Contents IDs in the title, and ensure that the target Content ID exists.
        valid_ids = []
        for record in title.content.content_records:
            valid_ids.append(record.content_id)
        if target_cid not in valid_ids:
            fatal_error("The specified Content ID could not be found in this title!")
        title.content.remove_content_by_cid(target_cid)
        # Auto fakesign because we've edited the title.
        title.fakesign()
        output_path.write_bytes(title.dump_wad())
        print(f"Removed content with Content ID \"{target_cid:08X}\"!")


def handle_wad_set(args):
    input_path = pathlib.Path(args.input)
    content_path = pathlib.Path(args.content)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        fatal_error(f"The specified WAD file \"{input_path}\" does not exist!")
    if not content_path.exists():
        fatal_error(f"The specified content file \"{content_path}\" does not exist!")

    title = libWiiPy.title.Title()
    title.load_wad(input_path.read_bytes())
    content_data = content_path.read_bytes()

    # Get the new type of the content, if one was specified.
    if args.type is not None:
        match str.lower(args.type):
            case "normal":
                target_type = libWiiPy.title.ContentType.NORMAL
            case "shared":
                target_type = libWiiPy.title.ContentType.SHARED
            case "dlc":
                target_type = libWiiPy.title.ContentType.DLC
            case _:
                fatal_error(f"The provided content type \"{args.type}\" is not valid!\"")
    else:
        target_type = None

    if args.index is not None:
        # If we're replacing based on the index, then make sure the specified index exists.
        existing_indices = []
        for record in title.content.content_records:
            existing_indices.append(record.index)
        if args.index not in existing_indices:
            fatal_error("The specified index could not be found in this title!")
        if target_type:
            title.set_content(content_data, args.index, content_type=target_type)
        else:
            title.set_content(content_data, args.index)
        # Auto fakesign because we've edited the title.
        title.fakesign()
        output_path.write_bytes(title.dump_wad())
        print(f"Replaced content at content index {args.index}!")


    elif args.cid is not None:
        # If we're replacing based on the CID, then make sure the specified CID is valid and exists.
        if len(args.cid) != 8:
            fatal_error("The specified Content ID is not valid!")
        target_cid = int(args.cid, 16)
        existing_cids = []
        for record in title.content.content_records:
            existing_cids.append(record.content_id)
        if target_cid not in existing_cids:
            fatal_error("The specified Content ID could not be found in this title!")
        target_index = title.content.get_index_from_cid(target_cid)
        if target_type:
            title.set_content(content_data, target_index, content_type=target_type)
        else:
            title.set_content(content_data, target_index)
        # Auto fakesign because we've edited the title.
        title.fakesign()
        output_path.write_bytes(title.dump_wad())
        print(f"Replaced content with Content ID \"{target_cid:08X}\"!")


def handle_wad_unpack(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if not input_path.exists():
        fatal_error(f"The specified WAD file \"{input_path}\" does not exist!")
    # Check if the output path already exists, and if it does, ensure that it is both a directory and empty.
    if output_path.exists():
        if output_path.is_file():
            fatal_error(f"A file already exists with the provided output directory name!")
    else:
        output_path.mkdir()

    # Step through each component of a WAD and dump it to a file.
    title = libWiiPy.title.Title()
    title.load_wad(input_path.read_bytes())

    cert_name = title.tmd.title_id + ".cert"
    output_path.joinpath(cert_name).write_bytes(title.wad.get_cert_data())

    tmd_name = title.tmd.title_id + ".tmd"
    output_path.joinpath(tmd_name).write_bytes(title.wad.get_tmd_data())

    ticket_name = title.tmd.title_id + ".tik"
    output_path.joinpath(ticket_name).write_bytes(title.wad.get_ticket_data())

    meta_name = title.tmd.title_id + ".footer"
    output_path.joinpath(meta_name).write_bytes(title.wad.get_meta_data())

    # Skip validating hashes if -s/--skip-hash was passed.
    if args.skip_hash:
        skip_hash = True
    else:
        skip_hash = False

    for content_file in range(0, title.tmd.num_contents):
        content_index = title.content.content_records[content_file].index
        content_file_name = f"{content_index:08X}".lower() + ".app"
        output_path.joinpath(content_file_name).write_bytes(title.get_content_by_index(content_file, skip_hash))

    print("WAD file unpacked!")
