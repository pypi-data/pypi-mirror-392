"""Top-level package for jps-pre-commit-utils."""

from importlib.metadata import PackageNotFoundError, version

__all__ = [
    "__version__",
]

try:
    __version__ = version("jps-pre-commit-utils")
except PackageNotFoundError:  # pragma: no cover
    # Fallback when running from source without an installed dist
    __version__ = "0.0.0"
