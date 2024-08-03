# "modules/title/emunand.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import os
import pathlib
import shutil
import libWiiPy


def handle_emunand_title(args):
    emunand_path = pathlib.Path(args.emunand)

    # Code for if the --install argument was passed.
    if args.install:
        wad_path = pathlib.Path(args.install)

        if not wad_path.exists():
            raise FileNotFoundError(wad_path)
        # Check if the EmuNAND path already exists, and ensure that it is a directory if it does.
        if emunand_path.exists():
            if emunand_path.is_file():
                raise ValueError("A file already exists with the provided directory name!")
        else:
            emunand_path.mkdir()

        # Check for required EmuNAND directories, and create them if they don't exist.
        ticket_dir = emunand_path.joinpath("ticket")
        title_dir = emunand_path.joinpath("title")
        shared_dir = emunand_path.joinpath("shared1")
        meta_dir = emunand_path.joinpath("meta")

        if not ticket_dir.exists():
            ticket_dir.mkdir()
        if not title_dir.exists():
            title_dir.mkdir()
        if not shared_dir.exists():
            shared_dir.mkdir()
        if not meta_dir.exists():
            meta_dir.mkdir()

        wad_file = open(wad_path, "rb").read()
        title = libWiiPy.title.Title()
        title.load_wad(wad_file)

        # Save the upper and lower portions of the Title ID, because these are used as target install directories.
        tid_upper = title.tmd.title_id[:8]
        tid_lower = title.tmd.title_id[8:]

        # Tickets are installed as <tid_lower>.tik in /ticket/<tid_upper>/
        ticket_dir = ticket_dir.joinpath(tid_upper)
        if not ticket_dir.exists():
            ticket_dir.mkdir()
        ticket_out = open(ticket_dir.joinpath(tid_lower + ".tik"), "wb")
        ticket_out.write(title.wad.get_ticket_data())
        ticket_out.close()

        # The TMD and normal contents are installed to /title/<tid_upper>/<tid_lower>/content/, with the tmd being named
        # title.tmd and the contents being named <cid>.app.
        title_dir = title_dir.joinpath(tid_upper)
        if not title_dir.exists():
            title_dir.mkdir()
        title_dir = title_dir.joinpath(tid_lower)
        if not title_dir.exists():
            title_dir.mkdir()
        content_dir = title_dir.joinpath("content")
        if not content_dir.exists():
            content_dir.mkdir()
        tmd_out = open(content_dir.joinpath("title.tmd"), "wb")
        tmd_out.write(title.wad.get_tmd_data())
        tmd_out.close()
        for content_file in range(0, title.tmd.num_contents):
            if title.tmd.content_records[content_file].content_type == 1:
                content_file_name = f"{title.tmd.content_records[content_file].content_id:08X}".lower()
                content_out = open(content_dir.joinpath(content_file_name + ".app"), "wb")
                content_out.write(title.get_content_by_index(content_file))
                content_out.close()
        if not title_dir.joinpath("data").exists():
            title_dir.joinpath("data").mkdir()  # Empty directory used for save data for the title.

        # Shared contents need to be installed to /shared1/, with incremental names determined by /shared1/content.map.
        content_map_path = shared_dir.joinpath("content.map")
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
                    content_out = open(shared_dir.joinpath(content_file_name + ".app"), "wb")
                    content_out.write(title.get_content_by_index(content_file))
                    content_out.close()
        content_map_out = open(shared_dir.joinpath("content.map"), "wb")
        content_map_out.write(content_map.dump())
        content_map_out.close()

        # The "footer" or meta file is installed as title.met in /meta/<tid_upper>/<tid_lower>/. Only write this if meta
        # is not nothing.
        meta_data = title.wad.get_meta_data()
        if meta_data != b'':
            meta_dir = meta_dir.joinpath(tid_upper)
            if not meta_dir.exists():
                meta_dir.mkdir()
            meta_dir = meta_dir.joinpath(tid_lower)
            if not meta_dir.exists():
                meta_dir.mkdir()
            meta_out = open(meta_dir.joinpath("title.met"), "wb")
            meta_out.write(title.wad.get_meta_data())
            meta_out.close()

        print("Title successfully installed to EmuNAND!")

    # Code for if the --uninstall argument was passed.
    elif args.uninstall:
        target_tid = args.uninstall
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
