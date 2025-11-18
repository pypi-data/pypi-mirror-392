#!/usr/bin/env python3
from enum import Enum


class LibPdfToImage(Enum):
    """Enumerar as bibliotecas externas que convertem PDF em imagem"""
    PDF_TO_IMG_FITZ = 'fitz'
    NOT_IMPLEMENTED = 'null'


class LibImageToPdf(Enum):

    IMAGE_TO_PDF_FITZ = 'fitz'
    IMAGE_TO_PDF_CANVAS = 'canvas'
    IMAGE_TO_PDF_PIL = 'pil'
    NOT_IMPLEMENTED = 'null'


class LibPDF(Enum):

    PYPDF = 'pypdf'
    FITZ = 'fitz'
    NOT_IMPLEMENTED = 'null'


class LibImage(Enum):

    PIL = 'pil'
    OPENCV = 'opencv'
    NOT_IMPLEMENTED = 'null'


class RotationAngle(Enum):

    ROTATION_90 = 90
    ROTATION_180 = 180
    ROTATION_270 = 270
