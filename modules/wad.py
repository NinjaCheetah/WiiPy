# "wad.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import os
import pathlib
import binascii
import libWiiPy


def handle_wad(args):
    input_path = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)

    # Code for if the --pack argument was passed.
    if args.pack:
        # Make sure input path both exists and is a directory. Separate checks because this provides more relevant
        # errors than just a NotADirectoryError if the actual issue is that there's nothing at all.
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        if not input_path.is_dir():
            raise NotADirectoryError(input_path)

        # Get a list of all files ending in .tmd, and then make sure that that list has *only* 1 entry. More than 1
        # means we can't pack a WAD because we couldn't really tell which TMD is intended for this WAD.
        tmd_list = list(input_path.glob('*.tmd'))
        if len(tmd_list) > 1:
            raise FileExistsError("More than one TMD file was found! Only one TMD can be packed into a WAD.")
        elif len(tmd_list) == 0:
            raise FileNotFoundError("No TMD file found! Cannot pack WAD.")
        else:
            tmd_file = tmd_list[0]

        # Repeat the same process as above for all .tik files.
        ticket_list = list(input_path.glob('*.tik'))
        if len(ticket_list) > 1:
            raise FileExistsError("More than one Ticket file was found! Only one Ticket can be packed into a WAD.")
        elif len(ticket_list) == 0:
            raise FileNotFoundError("No Ticket file found! Cannot pack WAD.")
        else:
            ticket_file = ticket_list[0]

        # And one more time for all .cert files.
        cert_list = list(input_path.glob('*.cert'))
        if len(cert_list) > 1:
            raise FileExistsError("More than one certificate file was found! Only one certificate can be packed into a "
                                  "WAD.")
        elif len(cert_list) == 0:
            raise FileNotFoundError("No certificate file found! Cannot pack WAD.")
        else:
            cert_file = cert_list[0]

        # Make sure that there's at least one content to pack.
        content_files = list(input_path.glob("*.app"))
        if not content_files:
            raise FileNotFoundError("No contents found! Cannot pack WAD.")

        # Open the output file, and load all the component files that we've now verified we have into a libWiiPy Title()
        # object.
        with open(output_path, "wb") as output_path:
            title = libWiiPy.title.Title()

            title.load_tmd(open(tmd_file, "rb").read())
            title.load_ticket(open(ticket_file, "rb").read())
            title.wad.set_cert_data(open(cert_file, "rb").read())
            # Footers are not super common and are not required, so we don't care about one existing until we get to
            # the step where we'd pack it.
            footer_file = list(input_path.glob("*.footer"))[0]
            if footer_file.exists():
                title.wad.set_meta_data(open(footer_file, "rb").read())
            # Method to ensure that the title's content records match between the TMD() and ContentRegion() objects.
            title.load_content_records()

            # Nullify TMD/Ticket signatures here if the argument was passed.
            if args.null_sigs:
                title.tmd.signature = b'\x00' * 256
                title.ticket.signature = b'\x00' * 256

            # Iterate over every file in the content_files list, and attempt to load it into the Title().
            for index in range(len(title.content.content_records)):
                for content in range(len(content_files)):
                    dec_content = open(content_files[content], "rb").read()
                    try:
                        # Attempt to load the content into the correct index.
                        title.load_content(dec_content, index)
                        break
                    except ValueError:
                        # Wasn't the right content, so try again.
                        pass

            output_path.write(title.dump_wad())

        print("WAD file packed!")

    # Code for if the --unpack argument was passed.
    elif args.unpack:
        if not input_path.exists():
            raise FileNotFoundError(input_path)
        # Check if the output path already exists, and if it does, ensure that it is both a directory and empty.
        if output_path.exists():
            if output_path.is_dir() and next(os.scandir(output_path), None):
                raise ValueError("Output folder is not empty!")
            elif output_path.is_file():
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

            for content_file in range(0, title.tmd.num_contents):
                content_file_name = "000000" + str(binascii.hexlify(content_file.to_bytes()).decode()) + ".app"
                content_out = open(output_path.joinpath(content_file_name), "wb")
                content_out.write(title.get_content_by_index(content_file))
                content_out.close()

        print("WAD file unpacked!")
