from math import atan
from typing import List, Optional, Tuple

from mathutils import Euler, Quaternion, Vector

from .enums.cmt_enum import *


class CMT:
    version: CMTVersion
    animation_list: List['CMTAnimation']

    def __init__(self, version=CMTVersion.YAKUZA5):
        self.version = version
        self.animation_list = list()

    @property
    def animation(self) -> Optional['CMTAnimation']:
        return self.animation_list[0] if len(self.animation_list) == 1 else None

    @animation.setter
    def animation(self, val):
        if len(self.animation_list):
            self.animation_list[0] = val
        else:
            self.animation_list.append(val)


class CMTAnimation:
    frame_rate: float
    frames: List['CMTFrame']

    def __init__(self, frame_rate=30.0):
        self.frame_rate = frame_rate
        self.frames = list()

    def has_clip_range(self):
        return any([True for x in self.frames if x.clip_range])


class CMTFrame:
    location: Vector
    fov: float

    focus_point: Vector
    roll: float

    clip_range: Optional[Tuple[float, float]]

    def __init__(self, location, fov):
        self.location = location
        self.fov = fov
        self.clip_range = None

    def from_dist_rotation(self, distance: float, rotation: Quaternion):
        forward: Vector = rotation @ Vector((0.0, 1.0, 0.0))
        forward.length = distance

        self.focus_point = self.location + forward
        self.roll = 2 * atan(rotation.y / rotation.w)

    def to_dist_rotation(self) -> Tuple[float, Quaternion]:
        forward: Vector = self.focus_point - self.location
        dist = forward.length

        forward.normalize()
        rotation = forward.to_track_quat('-Z', 'Y')
        rotation = rotation @ Euler((0, 0, self.roll)).to_quaternion()

        return (dist, rotation)
