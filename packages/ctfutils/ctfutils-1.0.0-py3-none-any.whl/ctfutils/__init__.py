"""
CTFUtils - A comprehensive toolkit for CTF competitions and cybersecurity challenges.

Version 1.0.0 - Functional Programming Architecture
87 pure functions across 4 modules (crypto, stego, misc, forensics)
"""

__version__ = "1.0.0"
__author__ = "Oxidizerhack"
__email__ = "jhonnyantoquispe@gmail.com"

# Importar módulos principales
from . import crypto
from . import stego
from . import forensics
from . import misc
from .exceptions import *

__all__ = ['crypto', 'stego', 'forensics', 'misc']