from pathlib import Path
import logging

# Basic logger config
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

def validate_file(path: Path):
    """
    Validate that a file exists and is a file.
    """
    if not isinstance(path, Path):
        raise TypeError("path must be a pathlib.Path object")

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")


def safe_filename(base: str) -> str:
    """
    Create a safe file name (remove unsafe characters).
    """
    for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        base = base.replace(c, "_")
    return base
