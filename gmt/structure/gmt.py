from itertools import chain
from typing import Dict, List, Optional, Tuple, Union

from .enums.gmt_enum import *


class GMT:
    name: str
    version: GMTVersion
    animation_list: List['GMTAnimation']

    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.animation_list = list()

    @property
    def animation(self) -> Optional['GMTAnimation']:
        return self.animation_list[0] if len(self.animation_list) == 1 else None

    @animation.setter
    def animation(self, val):
        self.animation_list[0] = val

    @property
    def vector_version(self) -> GMTVectorVersion:
        vector_version = GMTVectorVersion.from_GMTVersion(self.version)

        # Detect old version by the scale bone
        if vector_version != GMTVectorVersion.NO_VECTOR and len(self.animation_list) != 0:
            vector_version = GMTVectorVersion.OLD_VECTOR if self.animation_list[0].bones.get('scale') else GMTVectorVersion.DRAGON_VECTOR

        return vector_version

    def __str__(self) -> str:
        return f'name: "{self.name}", version: {GMTVersion(self.version).name}, animation: {{{self.animation}}}'

    def __repr__(self) -> str:
        return str(self)


class GMTAnimation:
    name: str
    frame_rate: float
    end_frame: int
    bones: Dict[str, 'GMTBone']

    def __init__(self, name, frame_rate, end_frame):
        self.name = name
        self.frame_rate = frame_rate
        self.end_frame = end_frame
        self.bones = dict()

    def get_end_frame(self):
        return max(0, *map(lambda c: c.get_end_frame(), chain(*map(lambda x: x.curves, self.bones.values()))))

    def __str__(self) -> str:
        return f'name: {self.name}, len(bones): {len(self.bones)}'

    def __repr__(self) -> str:
        return str(self)


class GMTBone:
    name: str

    __curve_dict: Dict[GMTCurveType, 'GMTCurve']

    def __init__(self, name):
        self.name = name

    # Curves
    @property
    def curves(self) -> List['GMTCurve']:
        """Returns a copied list containing the curves for this bone. Modifying this does not modify the internal curves dict."""
        return list(self.__curve_dict.values())

    @curves.setter
    def curves(self, val: List['GMTCurve']):
        """Creates the curves dict from a list. The list is not preserved/used after this."""
        self.__curve_dict = dict(map(lambda x: (x.type, x), val))

    # Location curve
    @property
    def location(self) -> 'GMTCurve':
        return self.__curve_dict.get(GMTCurveType.LOCATION)

    @location.setter
    def location(self, val: 'GMTCurve'):
        self.__curve_dict[GMTCurveType.LOCATION] = val

    # Rotation curve
    @property
    def rotation(self) -> 'GMTCurve':
        return self.__curve_dict.get(GMTCurveType.ROTATION)

    @rotation.setter
    def rotation(self, val: 'GMTCurve'):
        self.__curve_dict[GMTCurveType.ROTATION] = val

    # Hand patterns
    @property
    def patterns_hand(self) -> List['GMTCurve']:
        return self.__curve_dict.get(GMTCurveType.PATTERN_HAND)

    @patterns_hand.setter
    def patterns_hand(self, val: List['GMTCurve']):
        self.__curve_dict[GMTCurveType.PATTERN_HAND] = val

    # Face patterns
    @property
    def patterns_face(self) -> List['GMTCurve']:
        return self.__curve_dict.get(GMTCurveType.PATTERN_FACE)

    @patterns_face.setter
    def patterns_face(self, val: List['GMTCurve']):
        self.__curve_dict[GMTCurveType.PATTERN_FACE] = val

    # @property
    # def other_curves(self) -> List['GMTCurve']:
    #     return [self.__curve_dict[c] for c in self.__curve_dict if c not in list(GMTCurveType)]


class GMTCurve:
    type: GMTCurveType
    channel: GMTCurveChannel
    keyframes: List['GMTKeyframe']

    def __init__(self, type, channel):
        self.type = type
        self.channel = channel


    def get_end_frame(self):
        return self.keyframes[-1].frame if len(self.keyframes) else 0


    def fill_channels(self):
        if self.channel != GMTCurveChannel.ALL:
            if self.type == GMTCurveType.LOCATION:
                if self.channel == GMTCurveChannel.X:
                    for kf in self.keyframes:
                        kf.value = (kf.value[0], 0.0, 0.0)
                elif self.channel == GMTCurveChannel.Y:
                    for kf in self.keyframes:
                        kf.value = (0.0, kf.value[0], 0.0)
                elif self.channel == GMTCurveChannel.Z:
                    for kf in self.keyframes:
                        kf.value = (0.0, 0.0, kf.value[0])

                self.channel = GMTCurveChannel.ALL
            elif self.type == GMTCurveType.ROTATION:
                if self.channel == GMTCurveChannel.XW:
                    for kf in self.keyframes:
                        kf.value = (kf.value[0], 0.0, 0.0, kf.value[1])
                elif self.channel == GMTCurveChannel.YW:
                    for kf in self.keyframes:
                        kf.value = (0.0, kf.value[0], 0.0, kf.value[1])
                elif self.channel == GMTCurveChannel.ZW:
                    for kf in self.keyframes:
                        kf.value = (0.0, 0.0, kf.value[0], kf.value[1])

                self.channel = GMTCurveChannel.ALL


class GMTKeyframe:
    frame: int
    value: Tuple[Union[int, float]]

    def __init__(self, frame, value):
        self.frame = frame
        self.value = value
