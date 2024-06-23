# "nus.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import libWiiPy


def download_title(title_id: str, title_version_input: str = None):
    title_version = None
    if title_version_input is not None:
        try:
            title_version = int(title_version_input)
        except ValueError:
            print("Enter a valid integer for the Title Version.")
            return

    title = libWiiPy.title.download_title(title_id, title_version)

    file_name = title_id + "-v" + str(title.tmd.title_version) + ".wad"

    wad_file = open(file_name, "wb")
    wad_file.write(title.dump_wad())
    wad_file.close()
