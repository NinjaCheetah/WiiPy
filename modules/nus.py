# "nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import libWiiPy


def handle_nus(args):
    title_version = None
    if args.version is not None:
        try:
            title_version = int(args.version)
        except ValueError:
            print("Enter a valid integer for the Title Version.")
            return

    title = libWiiPy.title.download_title(args.tid, title_version)

    file_name = args.tid + "-v" + str(title.tmd.title_version) + ".wad"

    wad_file = open(file_name, "wb")
    wad_file.write(title.dump_wad())
    wad_file.close()

    print("Downloaded title with Title ID \"" + args.tid + "\"!")
