import struct
from contextlib import AsyncExitStack
from math import sqrt

from ...util import *
from ..enums.gmt_enum import *
from .br_rgg import BrRGGString


class BrGMT(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.header = br.read_struct(BrGMTHeader)
        header: BrGMTHeader = self.header

        br.seek(header.animations_offset)
        self.animations = br.read_struct(BrGMTAnimation, header.animations_count)

        self.graphs = [None] * header.graphs_count
        br.seek(header.graphs_offset)
        for i, offset in enumerate(br.read_uint32(header.graphs_count)):
            br.seek(offset)
            self.graphs[i] = br.read_struct(BrGMTGraph)

        br.seek(header.strings_offset)
        self.strings = br.read_struct(BrRGGString, header.strings_count)

        br.seek(header.bone_groups_offset)
        self.bone_groups = br.read_struct(BrGMTGroup, header.bone_groups_count)

        br.seek(header.curve_groups_offset)
        self.curve_groups = br.read_struct(BrGMTGroup, header.curve_groups_count)

        br.seek(header.curves_offset)
        self.curves = br.read_struct(BrGMTCurve, header.curves_count, self.graphs, header.version)

        # This will be done in the reader file
        # br.seek(header.animation_data_offset)
        # self.animation_data = br.buffer()[br.pos(): br.pos() + header.animation_data_size]


class BrGMTHeader(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.magic = br.read_str(4)

        if self.magic != 'GSGT':
            raise Exception(f'Invalid magic: Expected GSGT, got {self.magic}')

        br.read_uint8()  # 0x02 for little, 0x21 for big endian
        self.endianness = br.read_uint8() == 1

        br.set_endian(self.endianness)

        # Padding
        br.read_uint16()

        self.version = GMTVersion(br.read_uint32())

        # File size without padding
        self.data_size = br.read_uint32()

        self.file_name = br.read_struct(BrRGGString)

        self.animations_count = br.read_uint32()
        self.animations_offset = br.read_uint32()
        self.graphs_count = br.read_uint32()
        self.graphs_offset = br.read_uint32()
        self.graph_data_size = br.read_uint32()
        self.graph_data_offset = br.read_uint32()
        self.strings_count = br.read_uint32()
        self.strings_offset = br.read_uint32()
        self.bone_groups_count = br.read_uint32()
        self.bone_groups_offset = br.read_uint32()
        self.curve_groups_count = br.read_uint32()
        self.curve_groups_offset = br.read_uint32()
        self.curves_count = br.read_uint32()
        self.curves_offset = br.read_uint32()
        self.animation_data_size = br.read_uint32()
        self.animation_data_offset = br.read_uint32()

        # Padding
        br.read_uint32(3)

        # Unknown functionality
        self.flags = br.read_uint8(4)


class BrGMTAnimation(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.start_frame = br.read_uint32()
        self.end_frame = br.read_uint32()
        self.index = br.read_uint32()
        self.framerate = br.read_float()
        self.name_index = br.read_uint32()
        self.bone_group_index = br.read_uint32()
        self.curve_groups_index = br.read_uint32()
        self.curve_groups_count = br.read_uint32()
        self.curves_count = br.read_uint32()
        self.graphs_index = br.read_uint32()
        self.graphs_count = br.read_uint32()
        self.animation_data_size = br.read_uint32()
        self.animation_data_offset = br.read_uint32()
        self.graph_data_size = br.read_uint32()
        self.graph_data_offset = br.read_uint32()
        br.read_uint32()


class BrGMTGraph(BrStruct):
    def __br_read__(self, br: BinaryReader):
        self.count = br.read_uint16()
        self.values = br.read_uint16(self.count)
        br.read_int16()  # Delimiter (0xFFFF)


class BrGMTGroup(BrStruct):
    index: int
    count: int

    def __init__(self, index=0, count=0):
        self.index = index
        self.count = count

    def __br_read__(self, br: BinaryReader):
        self.index = br.read_uint16()
        self.count = br.read_uint16()

    def __br_write__(self, br: BinaryReader):
        br.write_uint16(self.index)
        br.write_uint16(self.count)


# LOC_XYZ
def _read_loc_all(br: BinaryReader, count):
    return list(map(lambda _: br.read_float(3), range(count)))


# LOC_CHANNEL
def _read_loc_channel(br: BinaryReader, count):
    return list(map(lambda _: br.read_float(1), range(count)))


# ROT_QUAT_XYZ_FLOAT
def _read_quat_xyz_float(br: BinaryReader, count):
    values = [None] * count

    for i in range(count):
        xyz = br.read_float(3)
        w = 1.0 - sum(map(lambda a: a ** 2, xyz))
        values[i] = (*xyz, (sqrt(w) if w > 0 else 0))

    return values


# ROT_XYZW_SHORT (KENZAN)
def _read_quat_half_float(br: BinaryReader, count):
    return list(map(lambda _: br.read_half_float(4), range(count)))


# ROT_XYZW_SHORT
def _read_quat_scaled(br: BinaryReader, count):
    return list(map(lambda _: tuple([(x / 16_384) for x in br.read_int16(4)]), range(count)))


# ROT_XW_FLOAT
def _read_quat_channel_float(br: BinaryReader, count):
    return list(map(lambda _: br.read_float(2), range(count)))


# ROT_XW_SHORT (KENZAN)
def _read_quat_channel_half_float(br: BinaryReader, count):
    return list(map(lambda _: br.read_half_float(2), range(count)))


# ROT_XW_SHORT
def _read_quat_channel_scaled(br: BinaryReader, count):
    return list(map(lambda _: tuple([(x / 16_384) for x in br.read_int16(2)]), range(count)))


# ROT_QUAT_XYZ_INT
def _read_quat_xyz_int(br: BinaryReader, count):
    base_quaternion = [(x / 32_768) for x in br.read_int16(4)]
    scale_quaternion = [(x / 32_768) for x in br.read_uint16(4)]

    values = [None] * count

    for i in range(count):
        f = br.read_uint32()
        axis_index = f & 3
        f = f >> 2

        indices = [0, 1, 2, 3]
        indices.pop(axis_index)

        v123 = (0x3FF00000, 0x000FFC00, 0x000003FF)
        m123 = struct.unpack(">fff", b'\x30\x80\x00\x00\x35\x80\x00\x00\x3A\x80\x00\x00')

        # A lengthy calculation taken straight out of decompiled code
        a123 = list(map(lambda v, m, l: (float(f & v) * m *
                                         scale_quaternion[l]) + base_quaternion[l], v123, m123, indices))
        a4 = 1.0 - sum(map(lambda a: a ** 2, a123))

        a123.insert(axis_index, sqrt(a4) if a4 > 0 else 0)
        values[i] = tuple(a123)

    return values


# PATTERN_HAND
def _read_pattern_short(br: BinaryReader, count):
    return list(map(lambda _: br.read_int16(2), range(count)))


# PATTERN_UNK
def _read_bytes(br: BinaryReader, count):
    return list(map(lambda _: br.read_uint8(1), range(count)))


class BrGMTCurve(BrStruct):
    def __br_read__(self, br: BinaryReader, graphs, version):
        self.graph_index = br.read_uint32()
        self.animation_data_offset = br.read_uint32()
        self.format = GMTCurveFormat(br.read_uint32())
        self.channel = GMTCurveChannel(br.read_uint16())
        self.type = GMTCurveType(br.read_uint16())

        self.graph = graphs[self.graph_index]
        count = self.graph.count
        with br.seek_to(self.animation_data_offset):
            if self.format == GMTCurveFormat.ROT_QUAT_XYZ_FLOAT:
                self.values = _read_quat_xyz_float(br, count)
            elif self.format == GMTCurveFormat.ROT_XYZW_SHORT:
                if version > GMTVersion.KENZAN:
                    self.values = _read_quat_scaled(br, count)
                else:
                    self.values = _read_quat_half_float(br, count)
            elif self.format == GMTCurveFormat.LOC_CHANNEL:
                self.values = _read_loc_channel(br, count)
            elif self.format == GMTCurveFormat.LOC_XYZ:
                self.values = _read_loc_all(br, count)
            elif self.format in [GMTCurveFormat.ROT_XW_FLOAT, GMTCurveFormat.ROT_YW_FLOAT, GMTCurveFormat.ROT_ZW_FLOAT]:
                self.values = _read_quat_channel_float(br, count)
            elif self.format in [GMTCurveFormat.ROT_XW_SHORT, GMTCurveFormat.ROT_YW_SHORT, GMTCurveFormat.ROT_ZW_SHORT]:
                if version > GMTVersion.KENZAN:
                    self.values = _read_quat_channel_scaled(br, count)
                else:
                    self.values = _read_quat_channel_half_float(br, count)
            elif self.format == GMTCurveFormat.PATTERN_HAND:
                self.values = _read_pattern_short(br, count)
            elif self.format == GMTCurveFormat.PATTERN_UNK:
                self.values = _read_bytes(br, count)
            elif self.format == GMTCurveFormat.ROT_QUAT_XYZ_INT:
                self.values = _read_quat_xyz_int(br, count)
            else:
                self.values = _read_bytes(br, count)
