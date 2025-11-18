"""
Ziyo - O'zbekcha dasturlash tili
Ziyo kodini Python kodiga aylantiruvchi va bajaruvchi kutubxona.
"""

__version__ = "1.0.0"
__author__ = "Yoqubov Javohir"
__email__ = "RaKUZEN@gmail.com"
__description__ = "Ziyo - O'zbekcha dasturlash tili transpiler va interpreter"

from .compiler import ZiyoTranspiler, transpile, run, validate_code

__all__ = [
    "ZiyoTranspiler",
    "transpile", 
    "run",
    "validate_code"
]

__title__ = "ziyo-lang"
__license__ = "MIT"

VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "release": "stable"
}

def get_version():
    return __version__

def get_info():
    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__
    }