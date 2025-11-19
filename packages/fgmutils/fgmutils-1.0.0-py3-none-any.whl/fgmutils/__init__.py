"""FGMUtils Python port."""

from importlib import metadata as _metadata

try:  # pragma: no cover - metadata only available in installed dists
    __version__ = _metadata.version("fgmutils")
except _metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["__version__"]
