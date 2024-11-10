# "commands/archive/theme.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import configparser
import pathlib
import shutil
import tempfile
import zipfile
import libWiiPy
import time


def handle_apply_mym(args):
    mym_path = pathlib.Path(args.mym)
    base_path = pathlib.Path(args.base)
    output_path = pathlib.Path(args.output)

    if not mym_path.exists():
        raise FileNotFoundError(mym_path)
    if not base_path.exists():
        raise FileNotFoundError(base_path)
    if output_path.suffix != ".csm":
        output_path = output_path.with_suffix(".csm")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        # Extract the MYM file into the temp directory.
        # MYM files are just ZIP files, so if zipfile doesn't accept it then it can't be valid.
        try:
            with zipfile.ZipFile(mym_path) as mym:
                mym.extractall(tmp_path.joinpath("mym_out"))
        except zipfile.BadZipfile:
            print("Error: The provided MYM theme is not valid!")
            exit(1)
        mym_tmp_path = pathlib.Path(tmp_path.joinpath("mym_out"))
        # Extract the asset archive into the temp directory.
        try:
            libWiiPy.archive.extract_u8(base_path.read_bytes(), str(tmp_path.joinpath("base_out")))
        except ValueError:
            print("Error: The provided base assets are not valid!")
            exit(1)
        base_temp_path = pathlib.Path(tmp_path.joinpath("base_out"))
        # Parse the mym.ini file in the root of the extracted MYM file.
        mym_ini = configparser.ConfigParser()
        mym_ini.read(mym_tmp_path.joinpath("mym.ini"))
        # Iterate over every key in the ini file and apply the theme based the source and target of each key.
        for section in mym_ini.sections():
            source_file = mym_tmp_path
            for piece in mym_ini[section]["source"].replace("\\", "/").split("/"):
                source_file = source_file.joinpath(piece)
            target_file = base_temp_path
            for piece in mym_ini[section]["file"].replace("\\", "/").split("/"):
                target_file = target_file.joinpath(piece)
            shutil.move(source_file, target_file)
        # Repack the now-themed asset archive and write it out.
        output_path.write_bytes(libWiiPy.archive.pack_u8(base_temp_path))

    print(f"Applied theme \"{mym_path.name}\" to \"{output_path.name}\"!")
