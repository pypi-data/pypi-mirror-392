"""mask-env: Create safe example files from secret files in multiple formats."""

__version__ = "1.0.0"

from mask_env.core import create_safe_example
from mask_env.processor import process_file

__all__ = ["create_safe_example", "process_file", "__version__"]

