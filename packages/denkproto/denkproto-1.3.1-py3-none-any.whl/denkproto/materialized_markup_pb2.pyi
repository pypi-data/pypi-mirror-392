import geometry_pb2 as _geometry_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClassificationAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "value")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    value: float
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class SegmentationAnnotation(_message.Message):
    __slots__ = ("annotation_id", "label_id", "x", "y", "data")
    ANNOTATION_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    annotation_id: str
    label_id: str
    x: int
    y: int
    data: _geometry_pb2.BinaryMaskData
    def __init__(self, annotation_id: _Optional[str] = ..., label_id: _Optional[str] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., data: _Optional[_Union[_geometry_pb2.BinaryMaskData, _Mapping]] = ...) -> None: ...

class ObjectDetectionAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "bounding_box")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    bounding_box: _geometry_pb2.BoundingBox
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ...) -> None: ...

class OcrAnnotation(_message.Message):
    __slots__ = ("id", "label_id", "text", "bounding_box", "polygon")
    ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    BOUNDING_BOX_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    id: str
    label_id: str
    text: str
    bounding_box: _geometry_pb2.BoundingBox
    polygon: _geometry_pb2.Polygon
    def __init__(self, id: _Optional[str] = ..., label_id: _Optional[str] = ..., text: _Optional[str] = ..., bounding_box: _Optional[_Union[_geometry_pb2.BoundingBox, _Mapping]] = ..., polygon: _Optional[_Union[_geometry_pb2.Polygon, _Mapping]] = ...) -> None: ...

class MaterializedMarkup(_message.Message):
    __slots__ = ("height", "width", "classification_annotations", "segmentation_annotations", "object_detection_annotations", "ocr_annotations")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    SEGMENTATION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_DETECTION_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    OCR_ANNOTATIONS_FIELD_NUMBER: _ClassVar[int]
    height: int
    width: int
    classification_annotations: _containers.RepeatedCompositeFieldContainer[ClassificationAnnotation]
    segmentation_annotations: _containers.RepeatedCompositeFieldContainer[SegmentationAnnotation]
    object_detection_annotations: _containers.RepeatedCompositeFieldContainer[ObjectDetectionAnnotation]
    ocr_annotations: _containers.RepeatedCompositeFieldContainer[OcrAnnotation]
    def __init__(self, height: _Optional[int] = ..., width: _Optional[int] = ..., classification_annotations: _Optional[_Iterable[_Union[ClassificationAnnotation, _Mapping]]] = ..., segmentation_annotations: _Optional[_Iterable[_Union[SegmentationAnnotation, _Mapping]]] = ..., object_detection_annotations: _Optional[_Iterable[_Union[ObjectDetectionAnnotation, _Mapping]]] = ..., ocr_annotations: _Optional[_Iterable[_Union[OcrAnnotation, _Mapping]]] = ...) -> None: ...
