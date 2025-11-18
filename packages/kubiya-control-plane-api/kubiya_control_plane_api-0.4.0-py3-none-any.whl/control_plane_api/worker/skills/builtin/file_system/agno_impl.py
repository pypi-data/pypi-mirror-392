"""File System skill implementation for agno runtime."""
from pathlib import Path
from agno.tools.file import FileTools


class FileSystemTools(FileTools):
    """
    File system operations using agno FileTools.

    Wraps agno's FileTools to provide file system access.
    """

    def __init__(self, base_directory: str = "/workspace", **kwargs):
        """
        Initialize file system tools.

        Args:
            base_directory: Base directory for file operations
            **kwargs: Additional configuration (read_only, max_file_size, etc.)
        """
        super().__init__(base_dir=Path(base_directory))
        self.config = kwargs
