import geometry_pb2 as _geometry_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClassificationPrediction(_message.Message):
    __slots__ = ("label_id", "probability", "interpretation_map")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    INTERPRETATION_MAP_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    probability: float
    interpretation_map: bytes
    def __init__(self, label_id: _Optional[str] = ..., probability: _Optional[float] = ..., interpretation_map: _Optional[bytes] = ...) -> None: ...

class ObjectDetectionPrediction(_message.Message):
    __slots__ = ("label_id", "top_leftx", "top_left_y", "width", "height", "probability", "angle", "full_orientation")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFTX_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    ANGLE_FIELD_NUMBER: _ClassVar[int]
    FULL_ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    top_leftx: int
    top_left_y: int
    width: int
    height: int
    probability: float
    angle: float
    full_orientation: bool
    def __init__(self, label_id: _Optional[str] = ..., top_leftx: _Optional[int] = ..., top_left_y: _Optional[int] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., probability: _Optional[float] = ..., angle: _Optional[float] = ..., full_orientation: bool = ...) -> None: ...

class InstanceSegmentationPrediction(_message.Message):
    __slots__ = ("label_id", "top_left_x", "top_left_y", "mask", "probability")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_X_FIELD_NUMBER: _ClassVar[int]
    TOP_LEFT_Y_FIELD_NUMBER: _ClassVar[int]
    MASK_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    top_left_x: int
    top_left_y: int
    mask: bytes
    probability: float
    def __init__(self, label_id: _Optional[str] = ..., top_left_x: _Optional[int] = ..., top_left_y: _Optional[int] = ..., mask: _Optional[bytes] = ..., probability: _Optional[float] = ...) -> None: ...

class CharacterPrediction(_message.Message):
    __slots__ = ("character", "probability")
    CHARACTER_FIELD_NUMBER: _ClassVar[int]
    PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    character: str
    probability: float
    def __init__(self, character: _Optional[str] = ..., probability: _Optional[float] = ...) -> None: ...

class OcrPrediction(_message.Message):
    __slots__ = ("label_id", "text", "character_predictions", "bounding_box", "polygon")
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    label_id: str
    text: str
    character_predictions: _containers.RepeatedCompositeFieldContainer[CharacterPrediction]
    bounding_box: _geometry_pb2.BoundingBox
    polygon: _geometry_pb2.Polygon
    def __init__(self, label_id: _Optional[str] = ..., text: _Optional[str] = ..., character_predictions: _Optional[_Iterable[_Union[CharacterPrediction, _Mapping]]] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., polygon: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ...) -> None: ...

class Prediction(_message.Message):
    __slots__ = ("height", "width", "classification_predictions", "object_detection_predictions", "instance_segmentation_predictions", "ocr_predictions")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_SEGMENTATION_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    OCR_PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    classification_predictions: _containers.RepeatedCompositeFieldContainer[ClassificationPrediction]
    object_detection_predictions: _containers.RepeatedCompositeFieldContainer[ObjectDetectionPrediction]
    instance_segmentation_predictions: _containers.RepeatedCompositeFieldContainer[InstanceSegmentationPrediction]
    ocr_predictions: _containers.RepeatedCompositeFieldContainer[OcrPrediction]
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., classification_predictions: _Optional[_Iterable[_Union[ClassificationPrediction, _Mapping]]] = ..., object_detection_predictions: _Optional[_Iterable[_Union[ObjectDetectionPrediction, _Mapping]]] = ..., instance_segmentation_predictions: _Optional[_Iterable[_Union[InstanceSegmentationPrediction, _Mapping]]] = ..., ocr_predictions: _Optional[_Iterable[_Union[OcrPrediction, _Mapping]]] = ...) -> None: ...
