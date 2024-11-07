# "commands/title/tmd.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import pathlib
import libWiiPy


def handle_tmd_remove(args):
    input_path = pathlib.Path(args.input)
    if args.output is not None:
        output_path = pathlib.Path(args.output)
    else:
        output_path = pathlib.Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    tmd = libWiiPy.title.TMD()
    tmd.load(input_path.read_bytes())

    if args.index is not None:
        # Make sure the target index exists, then remove it from the TMD.
        if args.index >= len(tmd.content_records):
            raise ValueError("The provided index could not be found in this TMD!")
        tmd.content_records.pop(args.index)
        tmd.num_contents -= 1
        # Auto fakesign because we've edited the TMD.
        tmd.fakesign()
        output_path.write_bytes(tmd.dump())
        print(f"Removed content record at index {args.index}!")

    elif args.cid is not None:
        if len(args.cid) != 8:
            raise ValueError("The provided Content ID is invalid!")
        target_cid = int(args.cid, 16)
        # List Contents IDs in the title, and ensure that the target Content ID exists.
        valid_ids = []
        for record in tmd.content_records:
            valid_ids.append(record.content_id)
        if target_cid not in valid_ids:
            raise ValueError("The provided Content ID could not be found in this TMD!")
        tmd.content_records.pop(valid_ids.index(target_cid))
        tmd.num_contents -= 1
        # Auto fakesign because we've edited the TMD.
        tmd.fakesign()
        output_path.write_bytes(tmd.dump())
        print(f"Removed content record with Content ID \"{target_cid:08X}\"!")
