"""
JAX-XC: JAX implementations of exchange-correlation functionals.
This file should be copied to jxc/__init__.py during build.
"""

from . import functionals

# Import main functions from get_params if it exists
try:
    from .get_params import (
        XC_POLARIZED,
        XC_UNPOLARIZED,
        get_params,
        get_xc_functional,
        list_functionals,
    )

    __all__ = [
        "functionals",
        "get_params",
        "get_xc_functional",
        "list_functionals",
        "XC_UNPOLARIZED",
        "XC_POLARIZED",
    ]
except ImportError:
    # If get_params doesn't exist, just export functionals
    __all__ = ["functionals"]
