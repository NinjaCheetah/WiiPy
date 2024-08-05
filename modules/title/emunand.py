# "modules/title/emunand.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import os
import pathlib
import shutil
import libWiiPy


class _EmuNANDStructure:
    def __init__(self, emunand_root):
        self.emunand_root: pathlib.Path = emunand_root

        self.import_dir = self.emunand_root.joinpath("import")
        self.meta_dir = self.emunand_root.joinpath("meta")
        self.shared1_dir = self.emunand_root.joinpath("shared1")
        self.shared2_dir = self.emunand_root.joinpath("shared2")
        self.sys_dir = self.emunand_root.joinpath("sys")
        self.ticket_dir = self.emunand_root.joinpath("ticket")
        self.title_dir = self.emunand_root.joinpath("title")
        self.tmp_dir = self.emunand_root.joinpath("tmp")
        self.wfs_dir = self.emunand_root.joinpath("wfs")

        self.import_dir.mkdir(exist_ok=True)
        self.meta_dir.mkdir(exist_ok=True)
        self.shared1_dir.mkdir(exist_ok=True)
        self.shared2_dir.mkdir(exist_ok=True)
        self.sys_dir.mkdir(exist_ok=True)
        self.ticket_dir.mkdir(exist_ok=True)
        self.title_dir.mkdir(exist_ok=True)
        self.tmp_dir.mkdir(exist_ok=True)
        self.wfs_dir.mkdir(exist_ok=True)


def _do_wad_install(emunand_struct: _EmuNANDStructure, title: libWiiPy.title.Title, skip_hash=False):
    # Save the upper and lower portions of the Title ID, because these are used as target install directories.
    tid_upper = title.tmd.title_id[:8]
    tid_lower = title.tmd.title_id[8:]

    # Tickets are installed as <tid_lower>.tik in /ticket/<tid_upper>/
    ticket_dir = emunand_struct.ticket_dir.joinpath(tid_upper)
    ticket_dir.mkdir(exist_ok=True)
    open(ticket_dir.joinpath(tid_lower + ".tik"), "wb").write(title.wad.get_ticket_data())

    # The TMD and normal contents are installed to /title/<tid_upper>/<tid_lower>/content/, with the tmd being named
    # title.tmd and the contents being named <cid>.app.
    title_dir = emunand_struct.title_dir.joinpath(tid_upper)
    title_dir.mkdir(exist_ok=True)
    title_dir = title_dir.joinpath(tid_lower)
    title_dir.mkdir(exist_ok=True)
    content_dir = title_dir.joinpath("content")
    if content_dir.exists():
        shutil.rmtree(content_dir)  # Clear the content directory so old contents aren't left behind.
    content_dir.mkdir(exist_ok=True)
    open(content_dir.joinpath("title.tmd"), "wb").write(title.wad.get_tmd_data())
    for content_file in range(0, title.tmd.num_contents):
        if title.tmd.content_records[content_file].content_type == 1:
            content_file_name = f"{title.tmd.content_records[content_file].content_id:08X}".lower()
            open(content_dir.joinpath(content_file_name + ".app"), "wb").write(
                title.get_content_by_index(content_file, skip_hash=skip_hash))
    title_dir.joinpath("data").mkdir(exist_ok=True)  # Empty directory used for save data for the title.

    # Shared contents need to be installed to /shared1/, with incremental names determined by /shared1/content.map.
    content_map_path = emunand_struct.shared1_dir.joinpath("content.map")
    content_map = libWiiPy.title.SharedContentMap()
    existing_hashes = []
    if content_map_path.exists():
        content_map.load(open(content_map_path, "rb").read())
        for record in content_map.shared_records:
            existing_hashes.append(record.content_hash)
    for content_file in range(0, title.tmd.num_contents):
        if title.tmd.content_records[content_file].content_type == 32769:
            if title.tmd.content_records[content_file].content_hash not in existing_hashes:
                content_file_name = content_map.add_content(title.tmd.content_records[content_file].content_hash)
                open(emunand_struct.shared1_dir.joinpath(content_file_name + ".app"), "wb").write(
                    title.get_content_by_index(content_file, skip_hash=skip_hash))
    open(emunand_struct.shared1_dir.joinpath("content.map"), "wb").write(content_map.dump())

    # The "footer" or meta file is installed as title.met in /meta/<tid_upper>/<tid_lower>/. Only write this if meta
    # is not nothing.
    meta_data = title.wad.get_meta_data()
    if meta_data != b'':
        meta_dir = emunand_struct.meta_dir.joinpath(tid_upper)
        meta_dir.mkdir(exist_ok=True)
        meta_dir = meta_dir.joinpath(tid_lower)
        meta_dir.mkdir(exist_ok=True)
        open(meta_dir.joinpath("title.met"), "wb").write(title.wad.get_meta_data())

    # The Title ID needs to be added to uid.sys, which is essentially a log of all titles that are installed or have
    # ever been installed.
    uid_sys_path = emunand_struct.sys_dir.joinpath("uid.sys")
    uid_sys = libWiiPy.title.UidSys()
    existing_tids = []
    if uid_sys_path.exists():
        uid_sys.load(open(uid_sys_path, "rb").read())
        for entry in uid_sys.uid_entries:
            existing_tids.append(entry.title_id)
    else:
        uid_sys.create()
        existing_tids.append(uid_sys.uid_entries[0].title_id)
    if title.tmd.title_id not in existing_tids:
        uid_sys.add(title.tmd.title_id)
    open(uid_sys_path, "wb").write(uid_sys.dump())


def handle_emunand_title(args):
    emunand_path = pathlib.Path(args.emunand)
    if args.skip_hash:
        skip_hash = True
    else:
        skip_hash = False

    # Code for if the --install argument was passed.
    if args.install:
        input_path = pathlib.Path(args.install)

        if not input_path.exists():
            raise FileNotFoundError(input_path)
        # Check if the EmuNAND path already exists, and ensure that it is a directory if it does.
        if emunand_path.exists():
            if emunand_path.is_file():
                raise ValueError("A file already exists with the provided directory name!")
        else:
            emunand_path.mkdir()

        emunand_struct = _EmuNANDStructure(emunand_path)

        if input_path.is_dir():
            wad_files = list(input_path.glob("*.[wW][aA][dD]"))
            if not wad_files:
                raise FileNotFoundError("No WAD files were found in the provided input directory!")
            wad_count = 0
            for wad in wad_files:
                title = libWiiPy.title.Title()
                title.load_wad(open(wad, "rb").read())
                try:
                    _do_wad_install(emunand_struct, title, skip_hash)
                    wad_count += 1
                except ValueError:
                    print(f"WAD {wad} could not be installed!")
            print(f"Successfully installed {wad_count} WAD(s) to EmuNAND!")
        else:
            title = libWiiPy.title.Title()
            title.load_wad(open(input_path, "rb").read())
            _do_wad_install(emunand_struct, title, skip_hash)
            print("Successfully installed WAD to EmuNAND!")

    # Code for if the --uninstall argument was passed.
    elif args.uninstall:
        input_str = args.uninstall
        if pathlib.Path(input_str).exists():
            title = libWiiPy.title.Title()
            title.load_wad(open(pathlib.Path(input_str), "rb").read())
            target_tid = title.tmd.title_id
        else:
            target_tid = args.install

        if len(target_tid) != 16:
            raise ValueError("Invalid Title ID! Title IDs must be 16 characters long.")

        # Setup required EmuNAND directories.
        ticket_dir = emunand_path.joinpath("ticket")
        title_dir = emunand_path.joinpath("title")
        meta_dir = emunand_path.joinpath("meta")

        # Save the upper and lower portions of the Title ID, because these are used as target install directories.
        tid_upper = target_tid[:8]
        tid_lower = target_tid[8:]

        if not title_dir.joinpath(tid_upper).joinpath(tid_lower).exists():
            print(f"Title with Title ID {target_tid} does not appear to be installed!")

        # Begin by removing the Ticket, which is installed to /ticket/<tid_upper>/<tid_lower>.tik
        if ticket_dir.joinpath(tid_upper).joinpath(tid_lower + ".tik").exists():
            os.remove(ticket_dir.joinpath(tid_upper).joinpath(tid_lower + ".tik"))

        # The TMD and contents are stored in /title/<tid_upper>/<tid_lower>/. Remove the TMD and all contents, but don't
        # delete the entire directory if anything exists in data.
        title_dir = title_dir.joinpath(tid_upper).joinpath(tid_lower)
        if not title_dir.joinpath("data").exists():
            shutil.rmtree(title_dir)
        elif title_dir.joinpath("data").exists() and not os.listdir(title_dir.joinpath("data")):
            shutil.rmtree(title_dir)
        else:
            # There are files in data, so we only want to delete the content directory.
            shutil.rmtree(title_dir.joinpath("content"))

        # On the off chance this title has a meta entry, delete that too.
        if meta_dir.joinpath(tid_upper).joinpath(tid_lower).joinpath("title.met").exists():
            shutil.rmtree(meta_dir.joinpath(tid_upper).joinpath(tid_lower))

        print("Title uninstalled from EmuNAND!")
