# WiiPy
WiiPy is a simple command line tool to use [libWiiPy](https://github.com/NinjaCheetah/libWiiPy)'s features to manage file formats used on the Wii. WiiPy also serves as a relatively simple reference implementation for libWiiPy's features, as it's designed to utilize all of them.

WiiPy is cross-platform, and supports macOS, Windows, and Linux, both because it's written in pure Python, and because it can be compiled for all three platforms via Nuitka.

To see what features are supported, I would recommend checking out the list of features that libWiiPy offers, which can be found [here]("https://github.com/NinjaCheetah/libWiiPy?tab=readme-ov-file#features").


## Requirements
libWiiPy has been tested on both Python 3.11 and 3.12, and works as expected in both places. WiiPy relies only on libWiiPy, so generally any version supported by libWiiPy should be supported by WiiPy.

To make sure you have libWiiPy and all of its dependencies, you can simply run:
```shell
pip install -r requirements.txt
```


## Usage
Basic usage for WiiPy is very simple.
```shell
python3 wiipy.py <command>
```
You can use `--help` to see a list of all commands, or use `<command> --help` to see usage instructions for that command. This also applies to subcommands, with the syntax `<command> <subcommand> --help`.

Available subcommands will expand as support for more features are added into libWiiPy. WiiPy is designed around libWiiPy's `main` branch, so any features that have been merged into main are likely to be supported here within a short period of time. This also means that any updates to the library will be addressed here quickly, so breaking changes in libWiiPy shouldn't cause issues.


## Compiling
If you'd like to compile WiiPy from Python into something a little more native, you can use one of the following commands. Make sure that you're in your venv, and that you've installed Nuitka first (it's included in `requirements.txt`).


### Linux and macOS
A Makefile is available to both build and install WiiPy on Linux and macOS. This will give you an executable named `wiipy` in the root of the project directory.
```shell
make all
```

Optionally, you can install WiiPy so that it's available system-wide. This will install it into `/usr/bin/`.
```shell
sudo make install
```


### Windows
On Windows, you can use the PowerShell script `Build.ps1` in place of the Makefile. This will give you an executable mamed `wiipy.exe` in the root of the project directory.
```shell
.\Build.ps1
```


### A Note About Scripts
WiiPy's source includes a directory named `scripts`, which is currently where miscellaneous libWiiPy-based scripts live. Note that they are not part of WiiPy releases, and are not tested the same way the WiiPy is. They are simply here for those who may find them useful.
