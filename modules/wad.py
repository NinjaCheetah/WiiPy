# "wad.py" from libWiiPy-cli by NinjaCheetah
# https://github.com/NinjaCheetah/libWiiPy-cli

import os
import pathlib
import binascii
import libWiiPy


def extract_wad_to_folder(in_file: str, out_folder: str):
    if not os.path.isfile(in_file):
        raise FileNotFoundError(in_file)
    out_folder = pathlib.Path(out_folder)
    if not out_folder.is_dir():
        out_folder.mkdir()

    with open(in_file, "rb") as wad_file:
        wad = libWiiPy.title.WAD()
        wad.load(wad_file.read())

        tmd = libWiiPy.title.TMD()
        tmd.load(wad.get_tmd_data())
        ticket = libWiiPy.title.Ticket()
        ticket.load(wad.get_ticket_data())
        content_region = libWiiPy.title.ContentRegion()
        content_region.load(wad.get_content_data(), tmd.content_records)

        title_key = ticket.get_title_key()

        cert_name = tmd.title_id + ".cert"
        cert_out = open(os.path.join(out_folder, cert_name), "wb")
        cert_out.write(wad.get_cert_data())
        cert_out.close()

        tmd_name = tmd.title_id + ".tmd"
        tmd_out = open(os.path.join(out_folder, tmd_name), "wb")
        tmd_out.write(wad.get_tmd_data())
        tmd_out.close()

        ticket_name = tmd.title_id + ".tik"
        ticket_out = open(os.path.join(out_folder, ticket_name), "wb")
        ticket_out.write(wad.get_ticket_data())
        ticket_out.close()

        meta_name = tmd.title_id + ".footer"
        meta_out = open(os.path.join(out_folder, meta_name), "wb")
        meta_out.write(wad.get_meta_data())
        meta_out.close()

        for content_file in range(0, tmd.num_contents):
            content_file_name = "000000"
            content_file_name += str(binascii.hexlify(content_file.to_bytes()).decode()) + ".app"
            content_out = open(os.path.join(out_folder, content_file_name), "wb")
            content_out.write(content_region.get_content_by_index(content_file, title_key))
            content_out.close()


def pack_wad_from_folder(in_folder, out_file):
    if not os.path.exists(in_folder):
        raise FileNotFoundError(in_folder)
    if not os.path.isdir(in_folder):
        raise NotADirectoryError(in_folder)

    out_file = pathlib.Path(out_file)
    in_folder = pathlib.Path(in_folder)

    tmd_file = list(in_folder.glob("*.tmd"))[0]
    if not os.path.exists(tmd_file):
        raise FileNotFoundError("Cannot find a TMD! Exiting...")

    ticket_file = list(in_folder.glob("*.tik"))[0]
    if not os.path.exists(ticket_file):
        raise FileNotFoundError("Cannot find a Ticket! Exiting...")

    cert_file = list(in_folder.glob("*.cert"))[0]
    if not os.path.exists(cert_file):
        raise FileNotFoundError("Cannot find a cert! Exiting...")

    content_files = list(in_folder.glob("*.app"))
    if not content_files:
        raise FileNotFoundError("Cannot find any contents! Exiting...")

    with open(out_file, "wb") as out_file:
        title = libWiiPy.title.Title()

        title.load_tmd(open(tmd_file, "rb").read())
        title.load_ticket(open(ticket_file, "rb").read())
        title.wad.set_cert_data(open(cert_file, "rb").read())
        footer_file = list(in_folder.glob("*.footer"))[0]
        if os.path.exists(footer_file):
            title.wad.set_meta_data(open(footer_file, "rb").read())
        title.load_content_records()

        title_key = title.ticket.get_title_key()

        content_list = list(in_folder.glob("*.app"))
        for index in range(len(title.content.content_records)):
            for content in range(len(content_list)):
                dec_content = open(content_list[content], "rb").read()
                try:
                    # Attempt to load the content into the correct index.
                    title.content.load_content(dec_content, index, title_key)
                    break
                except ValueError:
                    # Wasn't the right content, so try again.
                    pass

        out_file.write(title.dump_wad())
