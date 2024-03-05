# "main.py" from libWiiPy-cli by NinjaCheetah
# https://github.com/NinjaCheetah/libWiiPy-cli

import sys
from modules.wad import *

opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

if __name__ == "__main__":
    if "WAD" in args:
        if "-u" in opts:
            if len(args) == 3:
                extract_wad_to_folder(args[1], args[2])
                exit(0)
        raise SystemExit(f"Usage: {sys.argv[0]} WAD (-u | -p) <input> <output>")
    else:
        raise SystemExit(f"Usage: {sys.argv[0]} WAD (-u | -p) <input> <output>")
