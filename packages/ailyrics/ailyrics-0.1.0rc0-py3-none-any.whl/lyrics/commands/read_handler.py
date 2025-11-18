"""
Read Handler - Handles 'read' commands for reading files.
"""

import logging
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)


class ReadHandler:
    """
    Handles reading files from skills or workspace directories.

    This handler provides functionality equivalent to the bash 'read' command
    but specifically tailored for Agent Skills usage patterns.
    """

    def __init__(self):
        # Maximum file size to read (10MB)
        self.max_file_size = 10 * 1024 * 1024

        # Supported text file types
        self.text_extensions = {
            ".txt",
            ".md",
            ".py",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".csv",
            ".tsv",
            ".log",
            ".cfg",
            ".conf",
            ".ini",
            ".properties",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".csh",
            ".ksh",
            ".html",
            ".htm",
            ".css",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".pl",
            ".lua",
            ".r",
            ".m",
            ".swift",
            ".kt",
            ".scala",
            ".clj",
            ".erl",
            ".ex",
            ".exs",
            ".dockerfile",
            ".gitignore",
            ".env",
            ".example",
        }

        # Binary file types that should not be read as text
        self.binary_extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".xz",
            ".7z",
            ".rar",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".ico",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".app",
            ".deb",
            ".rpm",
        }

    def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read a file and return its contents.

        Args:
            file_path: Path to the file to read
            encoding: Text encoding to use (default: utf-8)

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file cannot be read
            ValueError: If the file is too large or unsupported
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if it's a file (not a directory)
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(
                f"File too large: {file_size} bytes (max: {self.max_file_size})"
            )

        # Determine file type
        file_extension = path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(path))

        # Check if it's a binary file
        if self._is_binary_file(path, file_extension, mime_type):
            raise ValueError(f"Cannot read binary file: {file_path}")

        # Read the file
        try:
            logger.debug(f"Reading file: {file_path} (size: {file_size} bytes)")

            with open(path, encoding=encoding, errors="replace") as f:
                content = f.read()

            logger.debug(
                f"Successfully read {len(content)} characters from {file_path}"
            )
            return content

        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error reading {file_path}: {e}")
            raise ValueError(f"Cannot decode file {file_path} as text: {e}")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise OSError(f"Error reading file {file_path}: {e}")

    def _is_binary_file(
        self, path: Path, file_extension: str, mime_type: str | None
    ) -> bool:
        """
        Determine if a file should be treated as binary.

        Args:
            path: Path to the file
            file_extension: File extension (with dot)
            mime_type: MIME type of the file

        Returns:
            True if the file should be treated as binary
        """
        # Check by extension first
        if file_extension in self.binary_extensions:
            return True

        if file_extension in self.text_extensions:
            return False

        # Check by MIME type
        if mime_type:
            if mime_type.startswith("text/"):
                return False
            if mime_type.startswith("application/") and "text" in mime_type:
                return False
            if "binary" in mime_type:
                return True

        # Try to detect by reading a small portion of the file
        try:
            with open(path, "rb") as f:
                sample = f.read(8192)  # Read first 8KB

            # Check for null bytes (common in binary files)
            if b"\x00" in sample:
                return True

            # Check the ratio of non-printable characters
            non_printable = sum(
                1 for byte in sample if byte < 0x20 and byte not in (b"\t\n\r")
            )
            if len(sample) > 0 and (non_printable / len(sample)) > 0.3:
                return True

            # Check for common binary file signatures
            binary_signatures = [
                b"\x89PNG",  # PNG
                b"\xff\xd8",  # JPEG
                b"PK\x03\x04",  # ZIP
                b"Rar!",  # RAR
                b"%PDF",  # PDF
                b"\xca\xfe\xba\xbe",  # Mach-O
                b"\x7fELF",  # ELF
            ]

            for signature in binary_signatures:
                if sample.startswith(signature):
                    return True

        except Exception as e:
            logger.warning(f"Error detecting file type for {path}: {e}")
            # If we can't determine, assume it's binary to be safe
            return True

        # Default to text if we can't determine
        return False

    def get_file_info(self, file_path: str) -> dict:
        """
        Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = path.stat()
        file_extension = path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(path))

        try:
            is_binary = self._is_binary_file(path, file_extension, mime_type)
        except Exception:
            is_binary = True

        return {
            "path": str(path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": file_extension,
            "mime_type": mime_type,
            "is_binary": is_binary,
            "is_readable": not is_binary and stat.st_size <= self.max_file_size,
        }

    def can_read_file(self, file_path: str) -> bool:
        """
        Check if a file can be read by this handler.

        Args:
            file_path: Path to the file

        Returns:
            True if the file can be read
        """
        try:
            info = self.get_file_info(file_path)
            return info["is_readable"]
        except Exception:
            return False

    def get_supported_extensions(self) -> set:
        """Get the set of supported text file extensions."""
        return self.text_extensions.copy()

    def get_binary_extensions(self) -> set:
        """Get the set of known binary file extensions."""
        return self.binary_extensions.copy()

    def set_max_file_size(self, max_size: int):
        """
        Set the maximum file size for reading.

        Args:
            max_size: Maximum file size in bytes
        """
        self.max_file_size = max_size

    def read_file_safe(self, file_path: str, encoding: str = "utf-8") -> str | None:
        """
        Safely read a file, returning None on error.

        Args:
            file_path: Path to the file to read
            encoding: Text encoding to use

        Returns:
            File contents or None if error occurred
        """
        try:
            return self.read_file(file_path, encoding)
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {e}")
            return None
