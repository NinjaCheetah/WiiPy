# "wad.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import binascii
import libWiiPy


def handle_wad(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    if args.pack:
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        if not input_path.is_dir():
            raise NotADirectoryError(input_path)

        tmd_file = list(input_path.glob("*.tmd"))[0]
        if not tmd_file.exists():
            raise FileNotFoundError("Cannot find a TMD! Exiting...")

        ticket_file = list(input_path.glob("*.tik"))[0]
        if not ticket_file.exists():
            raise FileNotFoundError("Cannot find a Ticket! Exiting...")

        cert_file = list(input_path.glob("*.cert"))[0]
        if not cert_file.exists():
            raise FileNotFoundError("Cannot find a cert! Exiting...")

        content_files = list(input_path.glob("*.app"))
        if not content_files:
            raise FileNotFoundError("Cannot find any contents! Exiting...")

        with open(output_path, "wb") as output_path:
            title = libWiiPy.title.Title()

            title.load_tmd(open(tmd_file, "rb").read())
            title.load_ticket(open(ticket_file, "rb").read())
            title.wad.set_cert_data(open(cert_file, "rb").read())
            footer_file = list(input_path.glob("*.footer"))[0]
            if footer_file.exists():
                title.wad.set_meta_data(open(footer_file, "rb").read())
            title.load_content_records()

            title_key = title.ticket.get_title_key()

            content_list = list(input_path.glob("*.app"))
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

            output_path.write(title.dump_wad())

        print("WAD file packed!")

    elif args.unpack:
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        if not output_path.is_dir():
            output_path.mkdir()

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

            for content_file in range(0, title.tmd.num_contents):
                content_file_name = "000000" + str(binascii.hexlify(content_file.to_bytes()).decode()) + ".app"
                content_out = open(output_path.joinpath(content_file_name), "wb")
                content_out.write(title.get_content_by_index(content_file))
                content_out.close()

        print("WAD file unpacked!")
