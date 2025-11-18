from importlib.metadata import metadata

_metadata = metadata("queens-solver")

__version__ = _metadata["Version"]
__pkg_name__ = _metadata["Name"]
__description__ = _metadata["Summary"]
__author__ = _metadata.get("Author")
__license__ = _metadata.get("License")