# "main.py" from libWiiPy-cli by NinjaCheetah
# https://github.com/NinjaCheetah/libWiiPy-cli

import sys
from modules.wad import *
from modules.nus import *
from modules.u8 import *

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

if __name__ == "__main__":
    if "WAD" in args:
        if "-u" in opts:
            if len(args) == 3:
                extract_wad_to_folder(args[1], args[2])
                exit(0)
        if "-p" in opts:
            if len(args) == 3:
                pack_wad_from_folder(args[1], args[2])
                exit(0)
        raise SystemExit(f"Usage: {sys.argv[0]} WAD (-u | -p) <input> <output>")
    elif "NUS" in args:
        if "-d" in opts:
            if len(args) == 2:
                download_title(args[1])
                exit(0)
            elif len(args) == 3:
                download_title(args[1], args[2])
                exit(0)
        raise SystemExit(f"Usage: {sys.argv[0]} NUS -d <Title ID> <Title Version (Optional)>")
    elif "U8" in args:
        if "-u" in opts:
            if len(args) == 3:
                extract_u8_to_folder(args[1], args[2])
                exit(0)
        elif "-p" in opts:
            if len(args) == 3:
                pack_u8_from_folder(args[1], args[2])
                exit(0)
        raise SystemExit(f"Usage: {sys.argv[0]} U8 (-u | -p) <input> <output>")
    else:
        raise SystemExit(f"Usage: {sys.argv[0]} WAD (-u | -p) <input> <output>")
