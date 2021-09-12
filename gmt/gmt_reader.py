from typing import Union

from .structure.br.br_gmt import *
from .structure.gmt import *
from .util import *


def read_gmt(file: Union[str, bytearray]) -> GMT:
    """Reads a GMT file and returns an GMT object.
    :param file: Path to file as a string, or bytes-like object containing the file
    :return: The GMT object
    """
    if isinstance(file, str):
        with open(file, 'rb') as f:
            file_bytes = f.read()
    else:
        file_bytes = file

    with BinaryReader(file_bytes, Endian.BIG) as br:
        br_gmt: BrGMT = br.read_struct(BrGMT)

    gmt = GMT(br_gmt.header.file_name.data, br_gmt.header.version)

    # Get bone names from groups
    bone_names: List[List[str]] = list(
        map(lambda x: br_gmt.strings[x.index: x.index + x.count], br_gmt.bone_groups))

    for br_anm in br_gmt.animations:
        br_anm: BrGMTAnimation

        anm = GMTAnimation(br_gmt.strings[br_anm.name_index].data, br_anm.framerate)
        anm_bone_names = bone_names[br_anm.bone_group_index]

        for i, br_group in enumerate(br_gmt.curve_groups[br_anm.curve_groups_index: br_anm.curve_groups_index + br_anm.curve_groups_count]):
            bone = GMTBone(anm_bone_names[i].data)
            curves = list()

            for br_curve in br_gmt.curves[br_group.index: br_group.index + br_group.count]:
                br_curve: BrGMTCurve
                curve = GMTCurve(br_curve.type, br_curve.channel)
                curve.keyframes = list(map(lambda k, v: GMTKeyframe(k, v), br_curve.graph.values, br_curve.values))

                curves.append(curve)

            bone.curves = curves
            anm.bones.append(bone)

        gmt.animation_list.append(anm)

    return gmt
