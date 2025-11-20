"""
OCR Layout Formatter - Convert OCR JSON to spatial text.

This library converts OCR data to formatted text that preserves
document layout using spatial positioning.

Example:
    >>> from ocr_layout import Formatter
    >>> formatter = Formatter()
    >>> result = formatter.format(ocr_data)

To enable logging:
    >>> import logging
    >>> logging.basicConfig(level=logging.DEBUG)
"""

from .formatter import Formatter

__version__ = "0.1.1"
__all__ = ["Formatter"]
