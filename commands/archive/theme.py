# "commands/archive/theme.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import configparser
import pathlib
import shutil
import tempfile
import zipfile
import libWiiPy
from modules.core import fatal_error


def handle_apply_mym(args):
    mym_path = pathlib.Path(args.mym)
    base_path = pathlib.Path(args.base)
    output_path = pathlib.Path(args.output)

    if not mym_path.exists():
        fatal_error(f"The specified MYM file \"{mym_path}\" does not exist!")
    if not base_path.exists():
        fatal_error(f"The specified base file \"{base_path}\" does not exist!")
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
            fatal_error("The provided MYM theme is not valid!")
        mym_tmp_path = pathlib.Path(tmp_path.joinpath("mym_out"))
        # Extract the asset archive into the temp directory.
        try:
            libWiiPy.archive.extract_u8(base_path.read_bytes(), str(tmp_path.joinpath("base_out")))
        except ValueError:
            fatal_error("The provided base assets are not valid!")
        base_temp_path = pathlib.Path(tmp_path.joinpath("base_out"))
        # Parse the mym.ini file in the root of the extracted MYM file.
        mym_ini = configparser.ConfigParser()
        if not mym_tmp_path.joinpath("mym.ini").exists():
            fatal_error("mym.ini could not be found in the theme! The provided theme is not valid.")
        mym_ini.read(mym_tmp_path.joinpath("mym.ini"))
        # Iterate over every key in the ini file and apply the theme based the source and target of each key.
        for section in mym_ini.sections():
            # Build the source path by adjusting the path in the ini file.
            source_file = mym_tmp_path
            for piece in mym_ini[section]["source"].replace("\\", "/").split("/"):
                source_file = source_file.joinpath(piece)
            # Check that this source file is actually valid, and error out if it isn't.
            if not source_file.exists():
                fatal_error(f"A source file specified in mym.ini, \"{mym_ini[section]['source']}\", does not exist! "
                            f"The provided theme is not valid.")
            # Build the target path the same way.
            target_file = base_temp_path
            for piece in mym_ini[section]["file"].replace("\\", "/").split("/"):
                target_file = target_file.joinpath(piece)
            # Move the source file into place over the target file.
            shutil.move(source_file, target_file)
        # Repack the now-themed asset archive and write it out.
        output_path.write_bytes(libWiiPy.archive.pack_u8(base_temp_path))

    print(f"Applied theme \"{mym_path.name}\" to \"{output_path.name}\"!")
