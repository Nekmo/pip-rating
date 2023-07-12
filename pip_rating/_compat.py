import warnings

from pkg_resources import parse_version

# Force patch of distutils, which is vendored into setuptools
import setuptools  # noqa:F401

# Ignore warnings of distutils being present after setuptools
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import pip

PIP_VERSION = list(parse_version(pip.__version__)._version.release)


if PIP_VERSION < [10]:
    from pip.locations import USER_CACHE_DIR
else:
    from pip._internal.locations import USER_CACHE_DIR  # noqa:F401


try:
    import tomllib
except ImportError:
    import tomlkit as tomllib


try:
    from functools import cache
except ImportError:
    from functools import lru_cache as cache
