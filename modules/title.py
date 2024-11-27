# "modules/title.py" from WiiPy by NinjaCheetah
# https://github.com/NinjaCheetah/WiiPy

import binascii
from modules.core import fatal_error


def title_edit_ios(new_ios: str) -> str:
    # Setting a new required IOS.
    try:
        new_ios = int(new_ios)
    except ValueError:
        fatal_error("The specified IOS is not valid! The new IOS should be a valid integer.")
    if new_ios < 3 or new_ios > 255:
        fatal_error("The specified IOS is not valid! The new IOS version should be between 3 and 255.")
    new_ios_tid = f"00000001{new_ios:08X}"
    return new_ios_tid


def title_edit_tid(tid: str, new_tid: str) -> str:
    # Setting a new TID, only changing TID low since this expects a 4 character ASCII input.
    if len(new_tid) != 4:
        fatal_error(f"The specified Title ID is not valid! The new Title ID should be 4 characters long.")
    if not new_tid.isalnum():
        fatal_error(f"The specified Title ID is not valid! The new Title ID should be alphanumeric.")
    # Get the current TID high, because we want to preserve the title type while only changing the TID low.
    tid_high = tid[:8]
    new_tid = f"{tid_high}{str(binascii.hexlify(new_tid.encode()), 'ascii')}"
    return new_tid


def title_edit_type(tid: str, new_type: str) -> str:
    # Setting a new title type.
    new_tid_high = None
    match new_type:
        case "System":
            new_tid_high = "00000001"
        case "Channel":
            new_tid_high = "00010001"
        case "SystemChannel":
            new_tid_high = "00010002"
        case "GameChannel":
            new_tid_high = "00010004"
        case "DLC":
            new_tid_high = "00010005"
        case "HiddenChannel":
            new_tid_high = "00010008"
        case _:
            fatal_error("The specified type is not valid! The new type must be one of: System, Channel, "
                        "SystemChannel, GameChannel, DLC, HiddenChannel.")
    tid_low = tid[8:]
    new_tid = f"{new_tid_high}{tid_low}"
    return new_tid
