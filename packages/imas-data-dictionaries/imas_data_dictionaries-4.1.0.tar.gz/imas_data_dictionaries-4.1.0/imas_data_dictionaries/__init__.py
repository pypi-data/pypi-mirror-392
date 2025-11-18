import difflib
import logging
import re
from contextlib import contextmanager, nullcontext
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterator, List, Tuple, Union
from zipfile import ZipFile

try:
    from importlib.resources import as_file, files

    try:
        from importlib.resources.abc import Traversable
    except ModuleNotFoundError:  # Python 3.9/3.10 support
        from importlib.abc import Traversable

except ImportError:  # Python 3.8 support
    from importlib_resources import as_file, files
    from importlib_resources.abc import Traversable

from packaging.version import InvalidVersion, Version

logger = logging.getLogger(__name__)
ZIPFILE_LOCATION = files("imas_data_dictionaries") / "imas_data_dictionaries.zip"


class UnknownDDVersion(ValueError):
    """Error raised when an unknown DD version is specified."""

    def __init__(self, version: str, available: List[str], note: str = "") -> None:
        close_matches = difflib.get_close_matches(version, available, n=1)
        if close_matches:
            suggestions = f"Did you mean {close_matches[0]!r}?"
        else:
            suggestions = f"Available versions are {', '.join(reversed(available))}"
        super().__init__(
            f"Data dictionary version {version!r} cannot be found. {suggestions}{note}"
        )


@contextmanager
def _open_zipfile(path: Union[Path, Traversable]) -> Iterator[ZipFile]:
    """Open a zipfile, given a Path or Traversable."""
    if isinstance(path, Path):
        ctx = nullcontext(path)
    else:
        ctx = as_file(path)
    with ctx as file:
        with ZipFile(file) as zipfile:
            yield zipfile


@lru_cache
def _read_dd_versions() -> Dict[str, Tuple[Union[Path, Traversable], str]]:
    """Traverse the DD zip file and return a map of known DD versions.

    Returns:
        version_map: version -> (zipfile path, filename)
    """
    versions = {}
    xml_re = re.compile(r"^data-dictionary/([0-9.]+)\.xml$")
    with _open_zipfile(ZIPFILE_LOCATION) as zipfile:
        for fname in zipfile.namelist():
            match = xml_re.match(fname)
            if match:
                version = match.group(1)
                if version not in versions:
                    versions[version] = (ZIPFILE_LOCATION, fname)
    if not versions:
        raise RuntimeError(
            "Could not find any data dictionary definitions. "
            f"Looked in: {ZIPFILE_LOCATION}."
        )
    return versions


@lru_cache
def _read_identifiers() -> Dict[str, Tuple[Union[Path, Traversable], str]]:
    """Traverse the DD zip file and return a map of known identifiers.

    Returns:
        identifier_map: identifier -> (zipfile path, filename)
    """
    identifiers = {}
    xml_re = re.compile(r"^identifiers/\w+/(\w+_identifier).xml$")
    with _open_zipfile(ZIPFILE_LOCATION) as zipfile:
        for fname in zipfile.namelist():
            match = xml_re.match(fname)
            if match:
                identifier_name = match.group(1)
                if identifier_name not in identifiers:
                    identifiers[identifier_name] = (ZIPFILE_LOCATION, fname)
    return identifiers


def parse_dd_version(version: str) -> Version:
    try:
        return Version(version)
    except InvalidVersion:
        # This is probably a dev build of the DD, of which the version is obtained with
        # `git describe` in the format X.Y.Z-<ncommits>-g<hash> with X.Y.Z the previous
        # released version: try again after converting the first dash to a + and treat
        # it like a `local` version specifier, which is recognized as newer.
        # https://packaging.python.org/en/latest/specifications/version-specifiers/
        return Version(version.replace("-", "+", 1))


@lru_cache
def dd_xml_versions() -> List[str]:
    """Parse zip file to find version numbers available"""

    def sort_key(version):
        try:
            return parse_dd_version(version)
        except InvalidVersion:
            # Don't fail when a malformatted version is present in the DD zip
            logger.error(
                f"Could not convert DD XML version {version} to a Version.", exc_info=1
            )
            return Version(0)

    return sorted(_read_dd_versions(), key=sort_key)


@lru_cache
def dd_identifiers() -> List[str]:
    """Parse zip file to find available identifiers"""

    return sorted(_read_identifiers())


def get_dd_xml(version):
    """Read XML file for the given data dictionary version."""
    dd_versions = dd_xml_versions()
    if version not in dd_versions:
        raise UnknownDDVersion(version, dd_versions)
    path, fname = _read_dd_versions()[version]
    with _open_zipfile(path) as zipfile:
        return zipfile.read(fname)


def get_dd_xml_crc(version):
    """Given a version string, return its CRC checksum"""
    dd_versions = dd_xml_versions()
    if version not in dd_versions:
        raise UnknownDDVersion(version, dd_versions)
    path, fname = _read_dd_versions()[version]
    with _open_zipfile(path) as zipfile:
        return zipfile.getinfo(fname).CRC


def get_identifier_xml(identifier_name):
    """Get identifier XML for the given identifier name"""
    path, fname = _read_identifiers()[identifier_name]
    with _open_zipfile(path) as zipfile:
        return zipfile.read(fname)
