# "modules/title/nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import hashlib
import pathlib
import binascii
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
            if output_dir.is_file():
                raise ValueError("A file already exists with the provided directory name!")
        else:
            output_dir.mkdir()

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
        output_dir.joinpath("tmd." + str(title_version)).write_bytes(title.tmd.dump())

    # Download the ticket, if we can.
    print(" - Downloading and parsing Ticket...")
    try:
        title.load_ticket(libWiiPy.title.download_ticket(tid, wiiu_endpoint=wiiu_nus_enabled))
        can_decrypt = True
        if output_dir is not None:
            output_dir.joinpath("tik").write_bytes(title.ticket.dump())
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
            output_dir.joinpath(content_file_name).write_bytes(content_list[content])
    title.content.content_list = content_list

    # Try to decrypt the contents for this title if a ticket was available.
    if output_dir is not None:
        if can_decrypt is True:
            for content in range(len(title.tmd.content_records)):
                print(" - Decrypting content " + str(content + 1) + " of " + str(len(title.tmd.content_records)) +
                      " (Content ID: " + str(title.tmd.content_records[content].content_id) + ")...")
                dec_content = title.get_content_by_index(content)
                content_file_name = f"{title.tmd.content_records[content].content_id:08X}".lower() + ".app"
                output_dir.joinpath(content_file_name).write_bytes(dec_content)
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
        pathlib.Path(wad_file).write_bytes(title.dump_wad())

    print("Downloaded title with Title ID \"" + args.tid + "\"!")


def handle_nus_content(args):
    tid = args.tid
    cid = args.cid
    version = args.version
    if args.decrypt:
        decrypt_content = True
    else:
        decrypt_content = False

    # Only accepting the 000000xx format because it's the one that would be most commonly known, rather than using the
    # actual integer that the hex Content ID translates to.
    try:
        content_id = int.from_bytes(binascii.unhexlify(cid))
    except binascii.Error:
        raise ValueError("Invalid Content ID! Content ID must be in format \"000000xx\"!")

    # Use the supplied output path if one was specified, otherwise generate one using the Content ID.
    if args.output is None:
        content_file_name = f"{content_id:08X}".lower()
        output_path = pathlib.Path(content_file_name)
    else:
        output_path = pathlib.Path(args.output)

    # Try to download the content, and catch the ValueError libWiiPy will throw if it can't be found.
    print("Downloading content with Content ID " + cid + "...")
    try:
        content_data = libWiiPy.title.download_content(tid, content_id)
    except ValueError:
        raise ValueError("The Title ID or Content ID you specified could not be found!")

    if decrypt_content is True:
        # Ensure that a version was supplied, because we need the matching TMD for decryption to work.
        if version is None:
            print("You must specify the version that the requested content belongs to for decryption!")
            return

        output_path = output_path.with_suffix(".app")
        tmd = libWiiPy.title.TMD()
        tmd.load(libWiiPy.title.download_tmd(tid, version))
        # Try to get a Ticket for the title, if a common one is available.
        try:
            ticket = libWiiPy.title.Ticket()
            ticket.load(libWiiPy.title.download_ticket(tid, wiiu_endpoint=True))
        except ValueError:
            print("No Ticket is available! Content cannot be decrypted!")
            return

        content_hash = 'gggggggggggggggggggggggggggggggggggggggg'
        content_size = 0
        content_index = 0
        for record in tmd.content_records:
            if record.content_id == content_id:
                content_hash = record.content_hash.decode()
                content_size = record.content_size
                content_index = record.index

        # If the default hash never changed, then a content record matching the downloaded content couldn't be found,
        # which most likely means that the wrong version was specified.
        if content_hash == 'gggggggggggggggggggggggggggggggggggggggg':
            print("Content was not found in the TMD from the specified version! Content cannot be decrypted!")
            return

        # Manually decrypt the content and verify its hash, which is what libWiiPy's get_content() methods do. We just
        # can't really use that here because that require setting up a lot more of the title than is necessary.
        content_dec = libWiiPy.title.decrypt_content(content_data, ticket.get_title_key(), content_index, content_size)
        content_dec_hash = hashlib.sha1(content_dec).hexdigest()
        if content_hash != content_dec_hash:
            raise ValueError("The decrypted content provided does not match the record at the provided index. \n"
                             "Expected hash is: {}\n".format(content_hash) +
                             "Actual hash is: {}".format(content_dec_hash))
        output_path.write_bytes(content_dec)
    else:
        output_path.write_bytes(content_data)

    print(f"Downloaded content with Content ID \"{cid}\"!")


def handle_nus_tmd(args):
    tid = args.tid

    # Check if --version was passed, because it'll be None if it wasn't.
    if args.version is not None:
        try:
            version = int(args.version)
        except ValueError:
            raise ValueError("Enter a valid integer for the TMD Version.")
    else:
        version = None

    # Use the supplied output path if one was specified, otherwise generate one using the Title ID.
    if args.output is None:
        output_path = pathlib.Path(tid + ".tmd")
    else:
        output_path = pathlib.Path(args.output)

    # Try to download the TMD, and catch the ValueError libWiiPy will throw if it can't be found.
    print(f"Downloading TMD for title {tid}...")
    try:
        tmd_data = libWiiPy.title.download_tmd(tid, version)
    except ValueError:
        raise ValueError("The Title ID or version you specified could not be found!")

    output_path.write_bytes(tmd_data)

    print(f"Downloaded TMD for title \"{tid}\"!")
