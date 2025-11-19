from enum import IntEnum


class WaMessageTypeId(IntEnum):
    TEXT = 1
    INTERACTIVE = 2


class WaInteractiveTypeId(IntEnum):
    BUTTON_REPLY = 1
    LIST_REPLY = 2

