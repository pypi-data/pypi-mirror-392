from ._version import __version__
from .lfn2pfn import lfn2pfn
from .scope import scope

__all__ = [
    "__version__",
    "SUPPORTED_VERSION",
    "get_algorithms",
]

#: RUCIO versions supported by this package
SUPPORTED_VERSION = "~=38.0"


def get_algorithms():
    return {
        "lfn2pfn": {
            "ctao_bdms": lfn2pfn,
        },
        "scope": {
            "ctao_bdms": scope,
        },
    }
