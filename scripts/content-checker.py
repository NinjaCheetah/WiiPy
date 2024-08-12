import pathlib
import sys

import libWiiPy

target_hash = sys.argv[1].lower().encode()
print(target_hash)

for content in range(3, 81):
    try:
        tmd = libWiiPy.title.download_tmd(f"00000007000000{content:02X}")
        open(f"00000007000000{content:02X}.tmd", "wb").write(tmd)
    except ValueError:
        pass

workdir = pathlib.Path(".")

tmd_files = list(workdir.glob("*.tmd"))

for tmd in tmd_files:
    new_tmd = libWiiPy.title.TMD()
    new_tmd.load(open(tmd, "rb").read())
    hash_list = []
    for content in new_tmd.content_records:
        hash_list.append(content.content_hash)
    if target_hash in hash_list:
        print(f"Found match in {tmd}\n")
