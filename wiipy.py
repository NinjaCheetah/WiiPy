# "wiipy.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import argparse
from importlib.metadata import version

from commands.archive.ash import *
from commands.archive.theme import *
from commands.archive.u8 import *
from commands.nand.emunand import *
from commands.nand.setting import *
from commands.title.ciosbuild import *
from commands.title.fakesign import *
from commands.title.info import *
from commands.title.iospatcher import *
from commands.title.nus import *
from commands.title.tmd import *
from commands.title.wad import *

wiipy_ver = "1.5.0"

if __name__ == "__main__":
    # Main argument parser.
    parser = argparse.ArgumentParser(
        description="A simple command line tool to manage file formats used by the Wii.")
    parser.add_argument("--version", action="version",
                        version=f"WiiPy v{wiipy_ver}, based on libWiiPy v{version('libWiiPy')} (from branch \'main\')")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", required=True)

    # Argument parser for the ASH subcommand.
    ash_parser = subparsers.add_parser("ash", help="compress/decompress an ASH file",
                                       description="compress/decompress an ASH file")
    ash_subparsers = ash_parser.add_subparsers(title="emunand", dest="emunand", required=True)
    # ASH compress parser.
    ash_compress_parser = ash_subparsers.add_parser("compress", help="compress a file into an ASH file",
                                                    description="compress a file into an ASH file; by default, this "
                                                                "will output to <input file>.ash")
    ash_compress_parser.set_defaults(func=handle_ash_compress)
    ash_compress_parser.add_argument("input", metavar="IN", type=str, help="file to compress")
    ash_compress_parser.add_argument("--sym-bits", metavar="SYM_BITS", type=int,
                            help="number of bits in each symbol tree leaf (default: 9)", default=9)
    ash_compress_parser.add_argument("--dist-bits", metavar="DIST_BITS", type=int,
                            help="number of bits in each distance tree leaf (default: 11)", default=11)
    ash_compress_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                     help="file to output the ASH file to (optional)")
    # ASH decompress parser.
    ash_decompress_parser = ash_subparsers.add_parser("decompress", help="decompress an ASH file",
                                                      description="decompress an ASH file; by default, this will "
                                                                  "output to <input file>.arc")
    ash_decompress_parser.set_defaults(func=handle_ash_decompress)
    ash_decompress_parser.add_argument("input", metavar="IN", type=str, help="ASH file to decompress")
    ash_decompress_parser.add_argument("--sym-bits", metavar="SYM_BITS", type=int,
                            help="number of bits in each symbol tree leaf (default: 9)", default=9)
    ash_decompress_parser.add_argument("--dist-bits", metavar="DIST_BITS", type=int,
                            help="number of bits in each distance tree leaf (default: 11)", default=11)
    ash_decompress_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                     help="file to output the ASH file to (optional)")

    # Argument parser for the cIOS command
    cios_parser = subparsers.add_parser("cios", help="build a cIOS from a base IOS and provided map",
                                        description="build a cIOS from a base IOS and provided map")
    cios_parser.set_defaults(func=build_cios)
    cios_parser.add_argument("base", metavar="BASE", type=str, help="base IOS WAD")
    cios_parser.add_argument("map", metavar="MAP", type=str, help="cIOS map file")
    cios_parser.add_argument("output", metavar="OUT", type=str, help="file to output the cIOS to")
    cios_parser.add_argument("-c", "--cios-ver", metavar="CIOS", type=str,
                             help="cIOS version from the map to build", required=True)
    cios_parser.add_argument("-m", "--modules", metavar="MODULES", type=str,
                             help="directory to look for cIOS commands in (optional, defaults to current directory)")
    cios_parser.add_argument("-s", "--slot", metavar="SLOT", type=int,
                             help="slot that this cIOS will install to (optional, defaults to 249)", default=249)
    cios_parser.add_argument("-v", "--version", metavar="VERSION", type=int,
                             help="version that this cIOS will be (optional, defaults to 65535)", default=65535)

    # Argument parser for the EmuNAND subcommand.
    emunand_parser = subparsers.add_parser("emunand", help="manage Wii EmuNAND directories",
                                           description="manage Wii EmuNAND directories")
    emunand_subparsers = emunand_parser.add_subparsers(title="emunand", dest="emunand", required=True)
    # Title EmuNAND subcommand.
    emunand_title_parser = emunand_subparsers.add_parser("title", help="manage titles on an EmuNAND",
                                                         description="manage titles on an EmuNAND")
    emunand_title_parser.set_defaults(func=handle_emunand_title)
    emunand_title_parser.add_argument("emunand", metavar="EMUNAND", type=str,
                                      help="path to the target EmuNAND directory")
    emunand_title_install_group = emunand_title_parser.add_mutually_exclusive_group(required=True)
    emunand_title_install_group.add_argument("--install", metavar="WAD", type=str,
                                             help="install the target WAD(s) to an EmuNAND (can be a single file or a "
                                                  "folder of WADs)")
    emunand_title_install_group.add_argument("--uninstall", metavar="TID", type=str,
                                             help="uninstall a title with the provided Title ID from an EmuNAND (also"
                                                  "accepts a WAD file to read the TID from)")
    emunand_title_parser.add_argument("-s", "--skip-hash", help="skips validating the hashes of decrypted "
                                      "content (install only)", action="store_true")

    # Argument parser for the fakesign subcommand.
    fakesign_parser = subparsers.add_parser("fakesign", help="fakesign a TMD, Ticket, or WAD (trucha bug)",
                                            description="fakesign a TMD, Ticket, or WAD (trucha bug); by default, this "
                                                        "will overwrite the input file if no output file is specified")
    fakesign_parser.set_defaults(func=handle_fakesign)
    fakesign_parser.add_argument("input", metavar="IN", type=str, help="input file")
    fakesign_parser.add_argument("-o", "--output", metavar="OUT", type=str, help="output file (optional)")

    # Argument parser for the info command.
    info_parser = subparsers.add_parser("info", help="get information about a TMD, Ticket, or WAD",
                                        description="get information about a TMD, Ticket, or WAD")
    info_parser.set_defaults(func=handle_info)
    info_parser.add_argument("input", metavar="IN", type=str, help="input file")

    # Argument parser for the iospatch command.
    iospatch_parser = subparsers.add_parser("iospatch", help="patch IOS WADs to re-enable exploits",
                                            description="patch IOS WADs to re-enable exploits; by default, this will "
                                                        "overwrite the input file in place unless you use -o/--output")
    iospatch_parser.set_defaults(func=handle_iospatch)
    iospatch_parser.add_argument("input", metavar="IN", type=str, help="input file")
    iospatch_parser.add_argument("-o", "--output", metavar="OUT", type=str, help="output file (optional)")
    iospatch_parser.add_argument("-fs", "--fakesigning", action="store_true", help="patch in fakesigning support")
    iospatch_parser.add_argument("-ei", "--es-identify", action="store_true", help="patch in ES_Identify access")
    iospatch_parser.add_argument("-na", "--nand-access", action="store_true", help="patch in /dev/flash access")
    iospatch_parser.add_argument("-vd", "--version-downgrading", action="store_true",
                                 help="patch in version downgrading support")
    iospatch_parser.add_argument("-di", "--drive-inquiry", action="store_true",
                                 help="patches out the drive inquiry (EXPERIMENTAL)")
    iospatch_parser.add_argument("-v", "--version", metavar="VERSION", type=int, help="set the IOS version")
    iospatch_parser.add_argument("-s", "--slot", metavar="SLOT", type=int,
                                 help="set the slot that this IOS will install to")
    iospatch_parser.add_argument("-a", "--all", action="store_true", help="apply all patches (overrides other options)")
    iospatch_parser.add_argument("-ns", "--no-shared", action="store_true",
                                 help="set all patched content to be non-shared")

    # Argument parser for the NUS subcommand.
    nus_parser = subparsers.add_parser("nus", help="download data from the NUS",
                                       description="download from the NUS")
    nus_subparsers = nus_parser.add_subparsers(dest="subcommand", required=True)
    # Title NUS subcommand.
    nus_title_parser = nus_subparsers.add_parser("title", help="download a title from the NUS",
                                                 description="download a title from the NUS")
    nus_title_parser.set_defaults(func=handle_nus_title)
    nus_title_parser.add_argument("tid", metavar="TID", type=str, help="Title ID to download")
    nus_title_parser.add_argument("-v", "--version", metavar="VERSION", type=int,
                                  help="version to download (optional)")
    nus_title_out_group_label = nus_title_parser.add_argument_group(title="output types (required)")
    nus_title_out_group = nus_title_out_group_label.add_mutually_exclusive_group(required=True)
    nus_title_out_group.add_argument("-o", "--output", metavar="OUT", type=str,
                                     help="download the title to a folder")
    nus_title_out_group.add_argument("-w", "--wad", metavar="WAD", type=str,
                                     help="pack a wad with the provided name")
    nus_title_parser.add_argument("--wii", help="use original Wii NUS instead of the Wii U servers",
                                  action="store_true")
    # Content NUS subcommand.
    nus_content_parser = nus_subparsers.add_parser("content", help="download a specific content from the NUS",
                                                   description="download a specific content from the NUS")
    nus_content_parser.set_defaults(func=handle_nus_content)
    nus_content_parser.add_argument("tid", metavar="TID", type=str, help="Title ID the content belongs to")
    nus_content_parser.add_argument("cid", metavar="CID", type=str,
                                    help="Content ID to download (in \"000000xx\" format)")
    nus_content_parser.add_argument("-v", "--version", metavar="VERSION", type=int,
                                    help="version this content belongs to (required for decryption)")
    nus_content_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                    help="path to download the content to (optional)")
    nus_content_parser.add_argument("-d", "--decrypt", action="store_true", help="decrypt this content")
    # TMD NUS subcommand.
    nus_tmd_parser = nus_subparsers.add_parser("tmd", help="download a tmd from the NUS",
                                               description="download a tmd from the NUS")
    nus_tmd_parser.set_defaults(func=handle_nus_tmd)
    nus_tmd_parser.add_argument("tid", metavar="TID", type=str, help="Title ID the TMD is for")
    nus_tmd_parser.add_argument("-v", "--version", metavar="VERSION", type=int, help="version of the TMD to download")
    nus_tmd_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                help="path to download the TMD to (optional)")

    # Argument parser for the setting subcommand.
    setting_parser = subparsers.add_parser("setting", help="manage setting.txt",
                                           description="manage setting.txt")
    setting_subparsers = setting_parser.add_subparsers(dest="subcommand", required=True)
    # Decrypt setting.txt subcommand.
    setting_dec_parser = setting_subparsers.add_parser("decrypt", help="decrypt setting.txt",
                                                       description="decrypt setting.txt; by default, this will output "
                                                                   "to setting_dec.txt")
    setting_dec_parser.set_defaults(func=handle_setting_decrypt)
    setting_dec_parser.add_argument("input", metavar="IN", type=str, help="encrypted setting.txt file to decrypt")
    setting_dec_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                    help="path to output the decrypted file to (optional)")
    # Encrypt setting.txt subcommand.
    setting_enc_parser = setting_subparsers.add_parser("encrypt", help="encrypt setting.txt",
                                                       description="encrypt setting.txt; by default, this will output "
                                                                   "to setting.txt")
    setting_enc_parser.set_defaults(func=handle_setting_encrypt)
    setting_enc_parser.add_argument("input", metavar="IN", type=str, help="decrypted setting.txt file to encrypt")
    setting_enc_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                    help="path to output the encrypted file to (optional)")
    # Generate setting.txt subcommand.
    setting_gen_parser = setting_subparsers.add_parser("gen",
                                                       help="generate a new setting.txt based on the provided values",
                                                       description="generate a new setting.txt based on the provided values")
    setting_gen_parser.set_defaults(func=handle_setting_gen)
    setting_gen_parser.add_argument("serno", metavar="SERNO", type=str,
                                           help="serial number of the console these settings are for")
    setting_gen_parser.add_argument("region", metavar="REGION", type=str,
                                           help="region of the console these settings are for (USA, EUR, JPN, or KOR)")

    # Argument parser for the theme subcommand.
    theme_parser = subparsers.add_parser("theme", help="apply custom themes to the Wii Menu",
                                         description="apply custom themes to the Wii Menu")
    theme_subparsers = theme_parser.add_subparsers(dest="subcommand", required=True)
    # MYM theme subcommand.
    theme_mym_parser = theme_subparsers.add_parser("mym", help="apply an MYM theme to the Wii Menu",
                                                   description="apply an MYM theme to the Wii Menu")
    theme_mym_parser.set_defaults(func=handle_apply_mym)
    theme_mym_parser.add_argument("mym", metavar="MYM", type=str, help="MYM theme to apply")
    theme_mym_parser.add_argument("base", metavar="BASE", type=str,
                                  help="base Wii Menu assets to apply the theme to (000000xx.app)")
    theme_mym_parser.add_argument("output", metavar="OUT", type=str,
                                  help="path to output the finished theme to (<filename>.csm)")

    # Argument parser for the TMD subcommand.
    tmd_parser = subparsers.add_parser("tmd", help="edit a TMD file",
                                       description="edit a TMD file")
    tmd_subparsers = tmd_parser.add_subparsers(dest="subcommand", required=True)
    # Edit TMD subcommand.
    tmd_edit_parser = tmd_subparsers.add_parser("edit", help="edit the properties of a TMD file",
                                                description="edit the properties of a TMD file; by default, this will "
                                                            "overwrite the input file unless an output is specified")
    tmd_edit_parser.set_defaults(func=handle_tmd_edit)
    tmd_edit_parser.add_argument("input", metavar="IN", type=str, help="TMD file to edit")
    tmd_edit_parser.add_argument("--tid", metavar="TID", type=str,
                                 help="a new Title ID for this title (formatted as 4 ASCII characters)")
    tmd_edit_parser.add_argument("--ios", metavar="IOS", type=str,
                                 help="a new IOS version for this title (formatted as the decimal IOS version, eg. 58)")
    tmd_edit_parser.add_argument("--type", metavar="TYPE", type=str,
                                 help="a new type for this title (valid options: System, Channel, SystemChannel, "
                                      "GameChannel, DLC, HiddenChannel)")
    tmd_edit_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                 help="file to output the updated TMD to (optional)")
    # Remove TMD subcommand.
    tmd_remove_parser = tmd_subparsers.add_parser("remove", help="remove a content record from a TMD file",
                                                  description="remove a content record from a TMD file, either by its "
                                                              "CID or by its index; by default, this will overwrite "
                                                              "the input file unless an output is specified")
    tmd_remove_parser.set_defaults(func=handle_tmd_remove)
    tmd_remove_parser.add_argument("input", metavar="IN", type=str, help="TMD file to remove a content record from")
    tmd_remove_targets = tmd_remove_parser.add_mutually_exclusive_group(required=True)
    tmd_remove_targets.add_argument("-i", "--index", metavar="INDEX", type=int,
                                    help="index of the content record to remove")
    tmd_remove_targets.add_argument("-c", "--cid", metavar="CID", type=str,
                                    help="Content ID of the content record to remove")
    tmd_remove_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                   help="file to output the updated TMD to (optional)")

    # Argument parser for the U8 subcommand.
    u8_parser = subparsers.add_parser("u8", help="pack/unpack a U8 archive",
                                      description="pack/unpack a U8 archive")
    u8_subparsers = u8_parser.add_subparsers(dest="subcommand", required=True)
    # Pack U8 subcommand.
    u8_pack_parser = u8_subparsers.add_parser("pack", help="pack a folder into U8 archive",
                                              description="pack a folder into U8 archive")
    u8_pack_parser.set_defaults(func=handle_u8_pack)
    u8_pack_parser.add_argument("input", metavar="IN", type=str, help="folder to pack")
    u8_pack_parser.add_argument("output", metavar="OUT", type=str, help="output U8 archive")
    # Unpack U8 subcommand.
    u8_unpack_parser = u8_subparsers.add_parser("unpack", help="unpack a U8 archive into a folder",
                                                description="unpack a U8 archive into a folder")
    u8_unpack_parser.set_defaults(func=handle_u8_unpack)
    u8_unpack_parser.add_argument("input", metavar="IN", type=str, help="U8 archive to unpack")
    u8_unpack_parser.add_argument("output", metavar="OUT", type=str, help="folder to output to")

    # Argument parser for the WAD subcommand.
    wad_parser = subparsers.add_parser("wad", help="pack/unpack/edit a WAD file",
                                       description="pack/unpack/edit a WAD file")
    wad_subparsers = wad_parser.add_subparsers(dest="subcommand", required=True)
    # Add WAD subcommand.
    wad_add_parser = wad_subparsers.add_parser("add", help="add decrypted content to a WAD file",
                                               description="add decrypted content to a WAD file; by default, this "
                                                        "will overwrite the input file unless an output is specified")
    wad_add_parser.set_defaults(func=handle_wad_add)
    wad_add_parser.add_argument("input", metavar="IN", type=str, help="WAD file to add to")
    wad_add_parser.add_argument("content", metavar="CONTENT", type=str, help="decrypted content to add")
    wad_add_parser.add_argument("-c", "--cid", metavar="CID", type=str,
                                help="Content ID to assign the new content (optional, will be randomly assigned if "
                                     "not specified)")
    wad_add_parser.add_argument("-t", "--type", metavar="TYPE", type=str,
                                help="the type of the new content, can be \"Normal\", \"Shared\", or \"DLC\" "
                                     "(optional, will default to \"Normal\" if not specified)")
    wad_add_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                help="file to output the updated WAD to (optional)")
    # Convert WAD subcommand.
    wad_convert_parser = wad_subparsers.add_parser("convert", help="re-encrypt a WAD file with a different key",
                                                   description="re-encrypt a WAD file with a different key, making it "
                                                               "possible to use the WAD in a different environment; "
                                                               "this fakesigns the WAD by default")
    wad_convert_parser.set_defaults(func=handle_wad_convert)
    wad_convert_parser.add_argument("input", metavar="IN", type=str, help="WAD file to re-encrypt")
    wad_convert_targets_lbl = wad_convert_parser.add_argument_group(title="target keys")
    wad_convert_targets = wad_convert_targets_lbl.add_mutually_exclusive_group(required=True)
    wad_convert_targets.add_argument("-d", "--dev", action="store_true",
                                     help="re-encrypt the WAD with the development common key, allowing it to be "
                                          "installed on development consoles")
    wad_convert_targets.add_argument("-r", "--retail", action="store_true",
                                     help="re-encrypt the WAD with the retail common key, allowing it to be installed "
                                          "on retail consoles or inside of Dolphin")
    wad_convert_targets.add_argument("-v", "--vwii", action="store_true",
                                     help="re-encrypt the WAD with the vWii key, allowing it to theoretically be "
                                          "installed from Wii U mode if a Wii U mode WAD installer is created")
    wad_convert_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                    help="file to output the new WAD to (optional, defaults to '<old_name>_<key>.wad')")
    # Edit WAD subcommand.
    wad_edit_parser = wad_subparsers.add_parser("edit", help="edit the properties of a WAD file",
                                                description="edit the properties of a WAD file; by default, this will "
                                                            "overwrite the input file unless an output is specified")
    wad_edit_parser.set_defaults(func=handle_wad_edit)
    wad_edit_parser.add_argument("input", metavar="IN", type=str, help="WAD file to edit")
    wad_edit_parser.add_argument("--tid", metavar="TID", type=str,
                                 help="a new Title ID for this WAD (formatted as 4 ASCII characters)")
    wad_edit_parser.add_argument("--ios", metavar="IOS", type=str,
                                 help="a new IOS version for this WAD (formatted as the decimal IOS version, eg. 58)")
    wad_edit_parser.add_argument("--type", metavar="TYPE", type=str,
                                 help="a new title type for this WAD (valid options: System, Channel, SystemChannel, "
                                      "GameChannel, DLC, HiddenChannel)")
    wad_edit_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                 help="file to output the updated WAD to (optional)")
    # Pack WAD subcommand.
    wad_pack_parser = wad_subparsers.add_parser("pack", help="pack a directory to a WAD file",
                                                 description="pack a directory to a WAD file")
    wad_pack_parser.set_defaults(func=handle_wad_pack)
    wad_pack_parser.add_argument("input", metavar="IN", type=str, help="input directory")
    wad_pack_parser.add_argument("output", metavar="OUT", type=str, help="WAD file to pack")
    wad_pack_parser.add_argument("-f", "--fakesign", help="fakesign the TMD and Ticket (trucha bug)",
                                 action="store_true")
    # Remove WAD subcommand.
    wad_remove_parser = wad_subparsers.add_parser("remove", help="remove content from a WAD file",
                                                  description="remove content from a WAD file, either by its CID or"
                                                              "by its index; by default, this will overwrite the input "
                                                              "file unless an output is specified")
    wad_remove_parser.set_defaults(func=handle_wad_remove)
    wad_remove_parser.add_argument("input", metavar="IN", type=str, help="WAD file to remove content from")
    wad_remove_targets = wad_remove_parser.add_mutually_exclusive_group(required=True)
    wad_remove_targets.add_argument("-i", "--index", metavar="INDEX", type=int,
                                    help="index of the content to remove")
    wad_remove_targets.add_argument("-c", "--cid", metavar="CID", type=str,
                                    help="Content ID of the content to remove")
    wad_remove_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                   help="file to output the updated WAD to (optional)")
    # Set WAD subcommand.
    wad_set_parser = wad_subparsers.add_parser("set", help="set content in a WAD file",
                                               description="replace existing content in a WAD file with new decrypted "
                                                           "data; by default, this will overwrite the input file "
                                                           "unless an output is specified")
    wad_set_parser.set_defaults(func=handle_wad_set)
    wad_set_parser.add_argument("input", metavar="IN", type=str, help="WAD file to replace content in")
    wad_set_parser.add_argument("content", metavar="CONTENT", type=str, help="new decrypted content")
    wad_set_targets = wad_set_parser.add_mutually_exclusive_group(required=True)
    wad_set_targets.add_argument("-i", "--index", metavar="INDEX", type=int,
                                 help="index of the content to replace")
    wad_set_targets.add_argument("-c", "--cid", metavar="CID", type=str,
                                 help="Content ID of the content to replace")
    wad_set_parser.add_argument("-o", "--output", metavar="OUT", type=str,
                                help="file to output the updated WAD to (optional)")
    wad_set_parser.add_argument("-t", "--type", metavar="TYPE", type=str,
                                help="specifies a new type for the content, can be \"Normal\", \"Shared\", or \"DLC\" "
                                     "(optional)")
    # Unpack WAD subcommand.
    wad_unpack_parser = wad_subparsers.add_parser("unpack", help="unpack a WAD file to a directory",
                                                  description="unpack a WAD file to a directory")
    wad_unpack_parser.set_defaults(func=handle_wad_unpack)
    wad_unpack_parser.add_argument("input", metavar="IN", type=str, help="WAD file to unpack")
    wad_unpack_parser.add_argument("output", metavar="OUT", type=str, help="output directory")
    wad_unpack_parser.add_argument("-s", "--skip-hash", help="skips validating the hashes of decrypted "
                                   "content", action="store_true")


    # Parse all the args, and call the appropriate function with all of those args if a valid subcommand was passed.
    args = parser.parse_args()
    args.func(args)
