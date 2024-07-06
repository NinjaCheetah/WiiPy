# "nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_nus(args):
    title_version = None
    file_path = None
    tid = args.tid
    if args.wii:
        use_wiiu_servers = False
    else:
        use_wiiu_servers = True
    if args.verbose:
        verbose = True
    else:
        verbose = False

    # Check if --version was passed, because it'll be None if it wasn't.
    if args.version is not None:
        try:
            title_version = int(args.version)
        except ValueError:
            print("Enter a valid integer for the Title Version.")
            return

    # If --output was passed, then save the file to the specified path (as long as it's valid).
    if args.output is not None:
        file_path = pathlib.Path(args.output)
        if not file_path.parent.exists() or not file_path.parent.is_dir():
            print("The specified output path does not exist!")
            return
        if file_path.suffix != ".wad":
            file_path = file_path.with_suffix(".wad")

    # Download the title from the NUS. This is done "manually" (as opposed to using download_title()) so that we can
    # provide verbose output if desired.
    title = libWiiPy.title.Title()

    # Announce the title being downloaded, and the version if applicable.
    if verbose:
        if title_version is not None:
            print("Downloading title " + tid + " v" + str(title_version) + ", please wait...")
        else:
            print("Downloading title " + tid + " vLatest, please wait...")

    # Download a specific TMD version if a version was specified, otherwise just download the latest TMD.
    if verbose:
        print(" - Downloading and parsing TMD...")
    if title_version is not None:
        title.load_tmd(libWiiPy.title.download_tmd(tid, title_version, wiiu_endpoint=use_wiiu_servers))
    else:
        title.load_tmd(libWiiPy.title.download_tmd(tid, wiiu_endpoint=use_wiiu_servers))

    # Download and parse the Ticket.
    if verbose:
        print(" - Downloading and parsing Ticket...")
    try:
        title.load_ticket(libWiiPy.title.download_ticket(tid, wiiu_endpoint=use_wiiu_servers))
    except ValueError:
        # If libWiiPy returns an error, then no ticket is available, so we can't continue.
        print("No Ticket is available for this title! Exiting...")
        return

    # Load the content records from the TMD, and begin iterating over the records.
    title.load_content_records()
    content_list = []
    for content in range(len(title.tmd.content_records)):
        if verbose:
            print(" - Downloading content " + str(content + 1) + " of " +
                  str(len(title.tmd.content_records)) + " (Content ID: " +
                  str(title.tmd.content_records[content].content_id) + ", Size: " +
                  str(title.tmd.content_records[content].content_size) + " bytes)...")
        content_list.append(libWiiPy.title.download_content(tid, title.tmd.content_records[content].content_id,
                                                            wiiu_endpoint=use_wiiu_servers))
        if verbose:
            print("   - Done!")
    title.content.content_list = content_list

    # Get the WAD certificate chain.
    if verbose:
        print(" - Building certificate...")
    title.wad.set_cert_data(libWiiPy.title.download_cert(wiiu_endpoint=use_wiiu_servers))

    # If we haven't gotten a name yet, make one from the TID and version.
    if file_path is None:
        file_path = pathlib.Path(args.tid + "-v" + str(title.tmd.title_version) + ".wad")

    wad_file = open(file_path, "wb")
    wad_file.write(title.dump_wad())
    wad_file.close()

    print("Downloaded title with Title ID \"" + args.tid + "\"!")
