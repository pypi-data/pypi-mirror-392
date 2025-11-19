from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Point2D(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class BoundingBox(_message.Message):
    __slots__ = ("x", "y", "width", "height", "angle", "full_orientation")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ANGLE_FIELD_NUMBER: _ClassVar[int]
    FULL_ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    width: int
    height: int
    angle: float
    full_orientation: bool
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., angle: _Optional[float] = ..., full_orientation: bool = ...) -> None: ...

class PolygonRing(_message.Message):
    __slots__ = ("hierarchy", "points")
    HIERARCHY_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    hierarchy: int
    points: _containers.RepeatedCompositeFieldContainer[Point2D]
    def __init__(self, hierarchy: _Optional[int] = ..., points: _Optional[_Iterable[_Union[Point2D, _Mapping]]] = ...) -> None: ...

class Polygon(_message.Message):
    __slots__ = ("rings",)
    RINGS_FIELD_NUMBER: _ClassVar[int]
    rings: _containers.RepeatedCompositeFieldContainer[PolygonRing]
    def __init__(self, rings: _Optional[_Iterable[_Union[PolygonRing, _Mapping]]] = ...) -> None: ...

class BinaryMaskData(_message.Message):
    __slots__ = ("delta_values", "mask_width", "mask_height")
    DELTA_VALUES_FIELD_NUMBER: _ClassVar[int]
    MASK_WIDTH_FIELD_NUMBER: _ClassVar[int]
    MASK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    delta_values: _containers.RepeatedScalarFieldContainer[int]
    mask_width: int
    mask_height: int
    def __init__(self, delta_values: _Optional[_Iterable[int]] = ..., mask_width: _Optional[int] = ..., mask_height: _Optional[int] = ...) -> None: ...
