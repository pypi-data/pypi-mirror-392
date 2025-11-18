"""
bbox - A Python library for manipulating bounding boxes in various coordinate formats.

This library provides the `Bbox` class and utility functions for manipulating bounding boxes
in various coordinate formats (Pascal VOC, COCO, YOLO, etc.). Supports transformations,
geometric operations, and conversions.

Classes:
    Bbox: A class to represent a bounding box.

Functions:
    nms: Perform Non-Maximum Suppression on a list of bounding boxes.
"""

from importlib.metadata import version as _version

from .bbox import Bbox
from .utils import nms

__version__ = _version("easy-bbox")
__all__ = ["Bbox", "nms"]
