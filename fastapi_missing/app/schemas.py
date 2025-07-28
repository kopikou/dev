from enum import Enum
from pydantic import BaseModel, Field
from typing import *

import base64
from io import BytesIO

class ImputationMethod(str, Enum):
    MEAN = "mean"
    KNN = "knn"
    MICE = "mice"
    RANDOM_FOREST = "random_forest"
    FREQUENT = "frequent"

class VisualizationFormat(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    SVG = "svg"

class ImageFormat(Enum):
    PNG = "png"
    JPEG = "jpeg"
    TIFF = "tiff"

class FileFormat(Enum):
    CSV = "csv"
    EXCEL = "xlsx"

class ImageMediaType(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"

class ImputationResponse(BaseModel):
    mechanisms: Dict[str, str]
    applied_methods: Dict[str, str]
    method_used: str
    stats_before: Dict[str, Any]
    stats_after: Dict[str, Any]
    warnings: List[str] = Field(default_factory=list) 


class AnalysisStats(BaseModel):
    missing: int
    missing_percent: float
    dtype: str
    mechanism: str
    recommended_method: str

class AnalysisResponse(BaseModel):
    stats: Dict[str, AnalysisStats]