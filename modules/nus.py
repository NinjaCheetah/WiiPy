# "nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import os
import pathlib
import libWiiPy


def handle_nus_title(args):
    title_version = None
    wad_file = None
    output_dir = None
    can_decrypt = False
    tid = args.tid
    if args.wii:
        wiiu_nus_enabled = False
    else:
        wiiu_nus_enabled = True

    # Check if --version was passed, because it'll be None if it wasn't.
    if args.version is not None:
        try:
            title_version = int(args.version)
        except ValueError:
            print("Enter a valid integer for the Title Version.")
            return

    # If --wad was passed, check to make sure the path is okay.
    if args.wad is not None:
        wad_file = pathlib.Path(args.wad)
        if wad_file.suffix != ".wad":
            wad_file = wad_file.with_suffix(".wad")

    # If --output was passed, make sure the directory either doesn't exist or is empty.
    if args.output is not None:
        output_dir = pathlib.Path(args.output)
        if output_dir.exists():
            if output_dir.is_dir() and next(os.scandir(output_dir), None):
                raise ValueError("Output folder is not empty!")
            elif output_dir.is_file():
                raise ValueError("A file already exists with the provided directory name!")
        else:
            os.mkdir(output_dir)

    # Download the title from the NUS. This is done "manually" (as opposed to using download_title()) so that we can
    # provide verbose output.
    title = libWiiPy.title.Title()

    # Announce the title being downloaded, and the version if applicable.
    if title_version is not None:
        print("Downloading title " + tid + " v" + str(title_version) + ", please wait...")
    else:
        print("Downloading title " + tid + " vLatest, please wait...")
    print(" - Downloading and parsing TMD...")
    # Download a specific TMD version if a version was specified, otherwise just download the latest TMD.
    if title_version is not None:
        title.load_tmd(libWiiPy.title.download_tmd(tid, title_version, wiiu_endpoint=wiiu_nus_enabled))
    else:
        title.load_tmd(libWiiPy.title.download_tmd(tid, wiiu_endpoint=wiiu_nus_enabled))
        title_version = title.tmd.title_version
    # Write out the TMD to a file.
    if output_dir is not None:
        tmd_out = open(output_dir.joinpath("tmd." + str(title_version)), "wb")
        tmd_out.write(title.tmd.dump())
        tmd_out.close()

    # Download the ticket, if we can.
    print(" - Downloading and parsing Ticket...")
    try:
        title.load_ticket(libWiiPy.title.download_ticket(tid, wiiu_endpoint=wiiu_nus_enabled))
        can_decrypt = True
        if output_dir is not None:
            ticket_out = open(output_dir.joinpath("tik"), "wb")
            ticket_out.write(title.ticket.dump())
            ticket_out.close()
    except ValueError:
        # If libWiiPy returns an error, then no ticket is available. Log this, and disable options requiring a
        # ticket so that they aren't attempted later.
        print("  - No Ticket is available!")
        if wad_file is not None and output_dir is None:
            print("--wad was passed, but this title cannot be packed into a WAD!")
            return

    # Load the content records from the TMD, and begin iterating over the records.
    title.load_content_records()
    content_list = []
    for content in range(len(title.tmd.content_records)):
        # Generate the content file name by converting the Content ID to hex and then removing the 0x.
        content_file_name = hex(title.tmd.content_records[content].content_id)[2:]
        while len(content_file_name) < 8:
            content_file_name = "0" + content_file_name
        print(" - Downloading content " + str(content + 1) + " of " +
              str(len(title.tmd.content_records)) + " (Content ID: " +
              str(title.tmd.content_records[content].content_id) + ", Size: " +
              str(title.tmd.content_records[content].content_size) + " bytes)...")
        content_list.append(libWiiPy.title.download_content(tid, title.tmd.content_records[content].content_id,
                                                            wiiu_endpoint=wiiu_nus_enabled))
        print("   - Done!")
        # If we're supposed to be outputting to a folder, then write these files out.
        if output_dir is not None:
            enc_content_out = open(output_dir.joinpath(content_file_name), "wb")
            enc_content_out.write(content_list[content])
            enc_content_out.close()
    title.content.content_list = content_list

    # Try to decrypt the contents for this title if a ticket was available.
    if can_decrypt is True and output_dir is not None:
        for content in range(len(title.tmd.content_records)):
            print(" - Decrypting content " + str(content + 1) + " of " + str(len(title.tmd.content_records)) +
                  " (Content ID: " + str(title.tmd.content_records[content].content_id) + ")...")
            dec_content = title.get_content_by_index(content)
            content_file_name = hex(title.tmd.content_records[content].content_id)[2:]
            while len(content_file_name) < 8:
                content_file_name = "0" + content_file_name
            content_file_name = content_file_name + ".app"
            dec_content_out = open(output_dir.joinpath(content_file_name), "wb")
            dec_content_out.write(dec_content)
            dec_content_out.close()
    else:
        print("Title has no Ticket, so content will not be decrypted!")

    # If --wad was passed, pack a WAD and output that.
    if wad_file is not None:
        # Get the WAD certificate chain.
        print(" - Building certificate...")
        title.wad.set_cert_data(libWiiPy.title.download_cert(wiiu_endpoint=wiiu_nus_enabled))
        # Ensure that the path ends in .wad, and add that if it doesn't.
        print("Packing WAD...")
        if wad_file.suffix != ".wad":
            wad_file = wad_file.with_suffix(".wad")
        # Have libWiiPy dump the WAD, and write that data out.
        file = open(wad_file, "wb")
        file.write(title.dump_wad())
        file.close()

    print("Downloaded title with Title ID \"" + args.tid + "\"!")
