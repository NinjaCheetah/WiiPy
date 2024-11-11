# "modules/core.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import sys


def fatal_error(msg: str) -> None:
    print(f"\033[31mError:\033[0m {msg}")
    sys.exit(-1)
