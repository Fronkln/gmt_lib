from enum import IntFlag

class GMTVersion(IntFlag):
    KENZAN = 0x10001
    YAKUZA3 = 0x20000
    YAKUZA5 = 0x20001
    ISHIN = 0x20002

# Using IntFlag to support undocumented formats (patterns etc)
class GMTCurveType(IntFlag):
    ROTATION = 0
    LOCATION = 1
    PATTERN_HAND = 4
    PATTERN_FACE = 5


class GMTCurveChannel(IntFlag):
    ALL = LEFT_HAND = 0
    X = RIGHT_HAND = 1
    Y = 2
    Z = 3

    # Only used for position, instead of 3 for some reason
    Z_POS = 4


class GMTCurveFormat(IntFlag):
    ROT_QUAT_XYZ_FLOAT = 1

    # Half float before version 0x20000, scaled shorts everywhere else
    ROT_XYZW_SHORT = 2

    LOC_CHANNEL = 4
    LOC_XYZ = 6

    ROT_XW_FLOAT = 0x10
    ROT_YW_FLOAT = 0x11
    ROT_ZW_FLOAT = 0x12

    # Half float before version 0x20000, scaled shorts everywhere else
    ROT_XW_SHORT = 0x13
    ROT_YW_SHORT = 0x14
    ROT_ZW_SHORT = 0x15

    PATTERN_HAND = 0x1C
    PATTERN_UNK = 0x1D

    ROT_QUAT_XYZ_INT = 0x1E
