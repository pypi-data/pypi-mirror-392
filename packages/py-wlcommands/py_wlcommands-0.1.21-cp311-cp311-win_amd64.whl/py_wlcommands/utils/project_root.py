"""Project root utilities for WL Commands."""

import os
from pathlib import Path

from .file_operations import get_file_operations

# Cache for project root paths to avoid repeated filesystem operations
_project_root_cache: dict[str, Path] = {}


def find_project_root(start_path: Path = None) -> Path:
    """
    Find the project root directory by looking for pyproject.toml file.

    Args:
        start_path: The path to start searching from. If None, uses current working directory.

    Returns:
        Path: The project root directory path

    Raises:
        FileNotFoundError: If project root with pyproject.toml cannot be found
        OSError: If there are filesystem access issues
    """
    if start_path is None:
        start_path = Path.cwd()

    current_path = start_path.resolve()
    path_str = str(current_path)

    # Check cache first
    if path_str in _project_root_cache:
        return _project_root_cache[path_str]

    file_ops = get_file_operations()

    try:
        while current_path.parent != current_path:
            marker_file = current_path / "pyproject.toml"
            try:
                if file_ops.exists(marker_file) and marker_file.is_file():
                    # Cache the result
                    _project_root_cache[path_str] = current_path
                    return current_path
            except OSError as e:
                # Handle permission errors or other filesystem issues
                raise OSError(f"无法访问目录 {current_path}: {e}")

            current_path = current_path.parent

        # If we get here, we've reached the filesystem root without finding pyproject.toml
        raise FileNotFoundError(f"无法在 {start_path} 或其父目录中找到 pyproject.toml")
    except OSError:
        # Re-raise OSError but handle other exceptions
        raise
    except Exception as e:
        # Handle any other unexpected exceptions
        raise RuntimeError(f"查找项目根目录时发生未知错误: {e}")


def clear_project_root_cache() -> None:
    """Clear the project root cache."""
    _project_root_cache.clear()
