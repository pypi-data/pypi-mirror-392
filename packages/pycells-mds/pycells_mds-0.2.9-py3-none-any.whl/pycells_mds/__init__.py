"""
PyCells is a mini spreadsheet engine with formulas, tables, sheets, and a cursor.
"""

from .session import init_db
from .core import PyCells

__all__ = ["init_db", "PyCells"]

__version__ = "0.2.9"
__author__ = "Zhandos Mambetali <zhandos.mambetali@gmail.com>"
