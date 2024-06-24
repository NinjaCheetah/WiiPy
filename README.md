# WiiPy
WiiPy is a simple command line tool to use [libWiiPy](https://github.com/NinjaCheetah/libWiiPy)'s features to manage file formats used on the Wii. WiiPy also serves as a relatively simple reference implementation for libWiiPy's features, as it's designed to utilize all of them.

WiiPy is cross-platform, and supports macOS, Windows, and Linux, both because it's written in pure Python, and because it can be compiled for all three platforms via Nuitka.

To see what features are supported, I would recommend checking out the list of features that libWiiPy offers, which can be found [here]("https://github.com/NinjaCheetah/libWiiPy?tab=readme-ov-file#features").

## Requirements
libWiiPy has been tested on both Python 3.11 and 3.12, and works as expected in both places. libWiiPy *should* support Python 3.10, however this is not verified. WiiPy only relies on libWiiPy, so it supports the same Python versions.

To make sure you have libWiiPy and all of its dependencies, you can simply run:
```shell
pip install -r requirements.txt
```

## Usage
Basic usage for WiiPy is very simple.
```shell
python3 wiipy.py <subcommand>
```
You can use `--help` to see a list of all subcommands, or use `<subcommand> --help` to see usage instructions for that subcommand.

Available subcommands will expand as support for more features are added into libWiiPy. WiiPy is designed around libWiiPy's `main` branch, so any features that have been merged into main are likely to be supported here within a short period of time. This also means that any breaking changes to the library will be handled here quickly, so incompatibilities shouldn't happen.

## Compiling
If you'd like to compile WiiPy from Python into something a little more native, you can use one of the following commands. Make sure you've installed Nuitka first (it's included in `requirements.txt`).
```shell
python -m nuitka --show-progress --assume-yes-for-downloads --onefile wiipy.py
```
On macOS and Linux, this will give you a binary named `wiipy.bin` in the same directory as the Python file. On Windows, you'll get a binary named `wiipy.exe` instead.
