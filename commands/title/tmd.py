# "commands/title/tmd.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy
from modules.core import fatal_error
from modules.title import tmd_edit_ios, tmd_edit_tid, tmd_edit_type


def handle_tmd_edit(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    tmd = libWiiPy.title.TMD()
    tmd.load(input_path.read_bytes())

    # State variable to make sure that changes are made.
    edits_made = False
    # Go over every possible change, and apply them if they were specified.
    if args.tid is not None:
        tmd = tmd_edit_tid(tmd, args.tid)
        edits_made = True
    if args.ios is not None:
        tmd = tmd_edit_ios(tmd, args.ios)
        edits_made = True
    if args.type is not None:
        tmd = tmd_edit_type(tmd, args.type)
        edits_made = True

    if not edits_made:
        fatal_error("You must specify at least one change to make!")

    # Fakesign the title since any changes have already invalidated the signature.
    tmd.fakesign()
    output_path.write_bytes(tmd.dump())

    print("Successfully edited TMD file!")


def handle_tmd_remove(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        fatal_error("The specified TMD files does not exist!")

    tmd = libWiiPy.title.TMD()
    tmd.load(input_path.read_bytes())

    if args.index is not None:
        # Make sure the target index exists, then remove it from the TMD.
        if args.index >= len(tmd.content_records):
            fatal_error("The specified index could not be found in the provided TMD!")
        tmd.content_records.pop(args.index)
        tmd.num_contents -= 1
        # Auto fakesign because we've edited the TMD.
        tmd.fakesign()
        output_path.write_bytes(tmd.dump())
        print(f"Removed content record at index {args.index}!")

    elif args.cid is not None:
        if len(args.cid) != 8:
            fatal_error("The specified Content ID is invalid!")
        target_cid = int(args.cid, 16)
        # List Contents IDs in the title, and ensure that the target Content ID exists.
        valid_ids = []
        for record in tmd.content_records:
            valid_ids.append(record.content_id)
        if target_cid not in valid_ids:
            fatal_error("The specified Content ID could not be found in the provided TMD!")
        tmd.content_records.pop(valid_ids.index(target_cid))
        tmd.num_contents -= 1
        # Auto fakesign because we've edited the TMD.
        tmd.fakesign()
        output_path.write_bytes(tmd.dump())
        print(f"Removed content record with Content ID \"{target_cid:08X}\"!")
