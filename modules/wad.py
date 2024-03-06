# "wad.py" from libWiiPy-cli by NinjaCheetah
# https://github.com/NinjaCheetah/libWiiPy-cli

import os
import pathlib
import binascii
from libWiiPy import wad, tmd, ticket, content


def extract_wad_to_folder(in_file_input: str, out_folder_input: str):
    if not os.path.isfile(in_file_input):
        raise FileNotFoundError(in_file_input)
    out_folder = pathlib.Path(out_folder_input)
    if not out_folder.is_dir():
        out_folder.mkdir()

    with open(in_file_input, "rb") as wad_file:
        wad_data = wad.WAD(wad_file.read())

        tmd_data = tmd.TMD(wad_data.get_tmd_data())
        ticket_data = ticket.Ticket(wad_data.get_ticket_data())
        content_data = content.ContentRegion(wad_data.get_content_data(), tmd_data.content_records)

        title_key = ticket_data.get_title_key()

        cert_name = tmd_data.title_id + ".cert"
        cert_out = open(os.path.join(out_folder, cert_name), "wb")
        cert_out.write(wad_data.get_cert_data())
        cert_out.close()

        tmd_name = tmd_data.title_id + ".tmd"
        tmd_out = open(os.path.join(out_folder, tmd_name), "wb")
        tmd_out.write(wad_data.get_tmd_data())
        tmd_out.close()

        ticket_name = tmd_data.title_id + ".tik"
        ticket_out = open(os.path.join(out_folder, ticket_name), "wb")
        ticket_out.write(wad_data.get_ticket_data())
        ticket_out.close()

        meta_name = tmd_data.title_id + ".footer"
        meta_out = open(os.path.join(out_folder, meta_name), "wb")
        meta_out.write(wad_data.get_meta_data())
        meta_out.close()

        for content_file in range(0, tmd_data.num_contents):
            content_file_name = "000000"
            content_file_name += str(binascii.hexlify(content_file.to_bytes()).decode()) + ".app"
            content_out = open(os.path.join(out_folder, content_file_name), "wb")
            content_out.write(content_data.get_content(content_file, title_key))
            content_out.close()
