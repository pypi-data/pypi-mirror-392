from importlib import metadata

try:
    __version__ = metadata.version(__package__ or "iflow-mcp-mcpdoc-server")
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "0.0.4"
