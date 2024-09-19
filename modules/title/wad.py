# "modules/title/wad.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import os
import pathlib
from random import randint
import libWiiPy


def handle_wad_add(args):
    input_path = pathlib.Path(args.input)
    content_path = pathlib.Path(args.content)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if not content_path.exists():
        raise FileNotFoundError(content_path)

    wad_file = open(input_path, 'rb')
    title = libWiiPy.title.Title()
    title.load_wad(wad_file.read())
    wad_file.close()

    content_file = open(content_path, 'rb')
    content_data = content_file.read()
    content_file.close()

    # Prepare the CID so it's ready when we go to add this content to the WAD.
    # We need to both validate that this is a real CID, and also that it isn't already taken by another content.
    if args.cid is not None:
        if len(args.cid) != 8:
            raise ValueError("The provided Content ID is invalid!")
        target_cid = int(args.cid, 16)
        for record in title.content.content_records:
            if target_cid == record.content_id:
                raise ValueError("The provided Content ID is already being used by this title!")
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
                raise ValueError("The provided content type is invalid!")
    else:
        target_type = libWiiPy.title.ContentType.NORMAL

    # Call add_content to add our new content with the set parameters.
    title.add_content(content_data, target_cid, target_type)

    out_file = open(output_path, 'wb')
    out_file.write(title.dump_wad())
    out_file.close()

    print(f"Successfully added new content with Content ID \"{target_cid:08X}\" and type \"{target_type.name}\"!")


def handle_wad_pack(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    # Make sure input path both exists and is a directory. Separate checks because this provides more relevant
    # errors than just a NotADirectoryError if the actual issue is that there's nothing at all.
    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if not input_path.is_dir():
        raise NotADirectoryError(input_path)

    # Get a list of all files ending in .tmd, and then make sure that that list has *only* 1 entry. More than 1
    # means we can't pack a WAD because we couldn't really tell which TMD is intended for this WAD.
    tmd_list = list(input_path.glob('*.[tT][mM][dD]'))
    if len(tmd_list) > 1:
        raise FileExistsError("More than one TMD file was found! Only one TMD can be packed into a WAD.")
    elif len(tmd_list) == 0:
        raise FileNotFoundError("No TMD file found! Cannot pack WAD.")
    else:
        tmd_file = tmd_list[0]

    # Repeat the same process as above for all .tik files.
    ticket_list = list(input_path.glob('*.[tT][iI][kK]'))
    if len(ticket_list) > 1:
        raise FileExistsError("More than one Ticket file was found! Only one Ticket can be packed into a WAD.")
    elif len(ticket_list) == 0:
        raise FileNotFoundError("No Ticket file found! Cannot pack WAD.")
    else:
        ticket_file = ticket_list[0]

    # And one more time for all .cert files.
    cert_list = list(input_path.glob('*.[cC][eE][rR][tT]'))
    if len(cert_list) > 1:
        raise FileExistsError("More than one certificate file was found! Only one certificate can be packed into a "
                              "WAD.")
    elif len(cert_list) == 0:
        raise FileNotFoundError("No certificate file found! Cannot pack WAD.")
    else:
        cert_file = cert_list[0]

    # Make sure that there's at least one content to pack.
    content_files = list(input_path.glob("*.[aA][pP][pP]"))
    if not content_files:
        raise FileNotFoundError("No contents found! Cannot pack WAD.")

    # Semi-hacky sorting method, but it works. Should maybe be changed eventually.
    content_files_ordered = []
    for index in range(len(content_files)):
        content_files_ordered.append(None)
    for content_file in content_files:
        content_index = int(content_file.stem, 16)
        content_files_ordered[content_index] = content_file

    # Open the output file, and load all the component files that we've now verified we have into a libWiiPy Title()
    # object.
    with open(output_path, "wb") as output_path:
        title = libWiiPy.title.Title()

        title.load_tmd(open(tmd_file, "rb").read())
        title.load_ticket(open(ticket_file, "rb").read())
        title.wad.set_cert_data(open(cert_file, "rb").read())
        # Footers are not super common and are not required, so we don't care about one existing until we get to
        # the step where we'd pack it.
        footer_file = list(input_path.glob("*.[fF][oO][oO][tT][eE][rR]"))[0]
        if footer_file.exists():
            title.wad.set_meta_data(open(footer_file, "rb").read())
        # Method to ensure that the title's content records match between the TMD() and ContentRegion() objects.
        title.load_content_records()

        # Iterate over every file in the content_files list, and set them in the Title().
        for record in title.content.content_records:
            index = title.content.content_records.index(record)
            dec_content = open(content_files_ordered[index], "rb").read()
            title.set_content(dec_content, index)

        # Fakesign the TMD and Ticket using the trucha bug, if enabled. This is built-in in libWiiPy v0.4.1+.
        if args.fakesign:
            title.fakesign()

        output_path.write(title.dump_wad())

    print("WAD file packed!")


def handle_wad_remove(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    wad_file = open(input_path, 'rb')
    title = libWiiPy.title.Title()
    title.load_wad(wad_file.read())
    wad_file.close()

    if args.index is not None:
        # List indices in the title, and ensure that the target content index exists.
        valid_indices = []
        for record in title.content.content_records:
            valid_indices.append(record.index)
        if args.index not in valid_indices:
            raise ValueError("The provided content index could not be found in this title!")
        title.content.remove_content_by_index(args.index)
        out_file = open(output_path, 'wb')
        out_file.write(title.dump_wad())
        out_file.close()
        print(f"Removed content at content index {args.index}!")

    elif args.cid is not None:
        if len(args.cid) != 8:
            raise ValueError("The provided Content ID is invalid!")
        target_cid = int(args.cid, 16)
        # List Contents IDs in the title, and ensure that the target Content ID exists.
        valid_ids = []
        for record in title.content.content_records:
            valid_ids.append(record.content_id)
        if target_cid not in valid_ids:
            raise ValueError("The provided Content ID could not be found in this title!")
        title.content.remove_content_by_cid(target_cid)
        out_file = open(output_path, 'wb')
        out_file.write(title.dump_wad())
        out_file.close()
        print(f"Removed content with Content ID \"{target_cid:08X}\"!")


def handle_wad_set(args):
    input_path = pathlib.Path(args.input)
    content_path = pathlib.Path(args.content)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(input_path)
    if not content_path.exists():
        raise FileNotFoundError(content_path)

    title = libWiiPy.title.Title()
    title.load_wad(open(input_path, "rb").read())

    content_data = open(content_path, "rb").read()

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
                raise ValueError("The provided content type is invalid!")
    else:
        target_type = None

    if args.index is not None:
        # If we're replacing based on the index, then make sure the specified index exists.
        existing_indices = []
        for record in title.content.content_records:
            existing_indices.append(record.index)
        if args.index not in existing_indices:
            raise ValueError("The provided index could not be found in this title!")
        if target_type:
            title.set_content(content_data, args.index, content_type=target_type)
        else:
            title.set_content(content_data, args.index)
        open(output_path, "wb").write(title.dump_wad())
        print(f"Replaced content at content index {args.index}!")


    elif args.cid is not None:
        # If we're replacing based on the CID, then make sure the specified CID is valid and exists.
        if len(args.cid) != 8:
            raise ValueError("The provided Content ID is invalid!")
        target_cid = int(args.cid, 16)
        existing_cids = []
        for record in title.content.content_records:
            existing_cids.append(record.content_id)
        if target_cid not in existing_cids:
            raise ValueError("The provided Content ID could not be found in this title!")
        target_index = title.content.get_index_from_cid(target_cid)
        if target_type:
            title.set_content(content_data, target_index, content_type=target_type)
        else:
            title.set_content(content_data, target_index)
        open(output_path, "wb").write(title.dump_wad())
        print(f"Replaced content with Content ID \"{target_cid:08X}\"!")


def handle_wad_unpack(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(input_path)
    # Check if the output path already exists, and if it does, ensure that it is both a directory and empty.
    if output_path.exists():
        # if output_path.is_dir() and next(os.scandir(output_path), None):
        #    raise ValueError("Output folder is not empty!")
        if output_path.is_file():
            raise ValueError("A file already exists with the provided directory name!")
    else:
        os.mkdir(output_path)

    # Step through each component of a WAD and dump it to a file.
    with open(args.input, "rb") as wad_file:
        title = libWiiPy.title.Title()
        title.load_wad(wad_file.read())

        cert_name = title.tmd.title_id + ".cert"
        cert_out = open(output_path.joinpath(cert_name), "wb")
        cert_out.write(title.wad.get_cert_data())
        cert_out.close()

        tmd_name = title.tmd.title_id + ".tmd"
        tmd_out = open(output_path.joinpath(tmd_name), "wb")
        tmd_out.write(title.wad.get_tmd_data())
        tmd_out.close()

        ticket_name = title.tmd.title_id + ".tik"
        ticket_out = open(output_path.joinpath(ticket_name), "wb")
        ticket_out.write(title.wad.get_ticket_data())
        ticket_out.close()

        meta_name = title.tmd.title_id + ".footer"
        meta_out = open(output_path.joinpath(meta_name), "wb")
        meta_out.write(title.wad.get_meta_data())
        meta_out.close()

        # Skip validating hashes if -s/--skip-hash was passed.
        if args.skip_hash:
            skip_hash = True
        else:
            skip_hash = False

        for content_file in range(0, title.tmd.num_contents):
            content_file_name = f"{content_file:08X}".lower() + ".app"
            content_out = open(output_path.joinpath(content_file_name), "wb")
            content_out.write(title.get_content_by_index(content_file, skip_hash))
            content_out.close()

    print("WAD file unpacked!")
