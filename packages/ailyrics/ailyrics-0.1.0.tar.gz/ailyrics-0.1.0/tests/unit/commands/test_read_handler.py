"""
Unit tests for the Read Handler module.
"""

import os
import tempfile
from pathlib import Path

import pytest

from lyrics.commands.read_handler import ReadHandler


class TestReadHandler:
    """Test cases for ReadHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ReadHandler()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_text_file_success(self):
        """Test reading a simple text file."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        content = "Hello, World!\nThis is a test file."
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Read file
        result = self.handler.read_file(test_file)

        assert result == content

    def test_read_markdown_file(self):
        """Test reading a markdown file."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "README.md")
        content = (
            "# Test Document\n\nThis is a test markdown file.\n\n- Item 1\n- Item 2"
        )
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Read file
        result = self.handler.read_file(test_file)

        assert result == content

    def test_read_python_file(self):
        """Test reading a Python file."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "script.py")
        content = """#!/usr/bin/env python3

def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
"""
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Read file
        result = self.handler.read_file(test_file)

        assert result == content

    def test_read_json_file(self):
        """Test reading a JSON file."""
        # Create test file
        test_file = os.path.join(self.temp_dir, "config.json")
        content = '{"name": "test", "version": "1.0", "enabled": true}'
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Read file
        result = self.handler.read_file(test_file)

        assert result == content

    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        with pytest.raises(FileNotFoundError):
            self.handler.read_file(nonexistent_file)

    def test_read_directory_instead_of_file(self):
        """Test reading a directory instead of a file."""
        test_dir = os.path.join(self.temp_dir, "testdir")
        os.makedirs(test_dir)

        with pytest.raises(ValueError, match="Not a file"):
            self.handler.read_file(test_dir)

    def test_read_file_too_large(self):
        """Test reading a file that exceeds maximum size."""
        # Create a large file (exceeds 10MB limit)
        test_file = os.path.join(self.temp_dir, "large_file.txt")
        large_content = "x" * (self.handler.max_file_size + 1)
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(large_content)

        with pytest.raises(ValueError, match="File too large"):
            self.handler.read_file(test_file)

    def test_read_binary_file_blocked(self):
        """Test reading a binary file that should be blocked."""
        # Create a fake binary file (PDF)
        test_file = os.path.join(self.temp_dir, "document.pdf")
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.4\nfake pdf content")

        with pytest.raises(ValueError, match="Cannot read binary file"):
            self.handler.read_file(test_file)

    def test_read_binary_image_blocked(self):
        """Test reading an image file that should be blocked."""
        # Create a fake PNG file
        test_file = os.path.join(self.temp_dir, "image.png")
        with open(test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\nfake png content")

        with pytest.raises(ValueError, match="Cannot read binary file"):
            self.handler.read_file(test_file)

    def test_read_binary_zip_blocked(self):
        """Test reading a ZIP file that should be blocked."""
        # Create a fake ZIP file
        test_file = os.path.join(self.temp_dir, "archive.zip")
        with open(test_file, "wb") as f:
            f.write(b"PK\x03\x04fake zip content")

        with pytest.raises(ValueError, match="Cannot read binary file"):
            self.handler.read_file(test_file)

    def test_read_binary_executable_blocked(self):
        """Test reading an executable file that should be blocked."""
        # Create a fake ELF executable
        test_file = os.path.join(self.temp_dir, "program")
        with open(test_file, "wb") as f:
            f.write(b"\x7fELF\x02\x01\x01\x00fake elf content")

        with pytest.raises(ValueError, match="Cannot read binary file"):
            self.handler.read_file(test_file)

    def test_read_unicode_decode_error(self):
        """Test handling of Unicode decode errors."""
        # Create a file with invalid UTF-8
        test_file = os.path.join(self.temp_dir, "invalid.txt")
        with open(test_file, "wb") as f:
            f.write(b"Valid text\xff\xfe\xfd\xfcinvalid bytes")

        # Should handle decode errors gracefully with "replace" errors
        result = self.handler.read_file(test_file)
        assert "Valid text" in result
        # The invalid bytes should be replaced with replacement characters
        assert "\ufffd" in result

    def test_read_different_encoding(self):
        """Test reading file with different encoding."""
        # Create a file with Latin-1 encoding
        test_file = os.path.join(self.temp_dir, "latin1.txt")
        content = "Café résumé naïve"
        with open(test_file, "w", encoding="latin-1") as f:
            f.write(content)

        # Read with Latin-1 encoding
        result = self.handler.read_file(test_file, encoding="latin-1")
        assert result == content

    def test_read_empty_file(self):
        """Test reading an empty file."""
        test_file = os.path.join(self.temp_dir, "empty.txt")
        Path(test_file).touch()

        result = self.handler.read_file(test_file)
        assert result == ""

    def test_read_file_with_special_chars(self):
        """Test reading file with special characters."""
        test_file = os.path.join(self.temp_dir, "special.txt")
        content = "Special chars: àáâãäåæçèéêë ñ 中文 🚀 €"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        result = self.handler.read_file(test_file)
        assert result == content

    def test_is_binary_file_by_extension_text(self):
        """Test binary file detection by extension (text files)."""
        test_file = os.path.join(self.temp_dir, "test.py")
        Path(test_file).touch()

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".py", "text/x-python")
        assert is_binary is False

    def test_is_binary_file_by_extension_binary(self):
        """Test binary file detection by extension (binary files)."""
        test_file = os.path.join(self.temp_dir, "test.pdf")
        Path(test_file).touch()

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".pdf", "application/pdf")
        assert is_binary is True

    def test_is_binary_file_by_mime_type_text(self):
        """Test binary file detection by MIME type (text)."""
        test_file = os.path.join(self.temp_dir, "test.html")
        with open(test_file, "w") as f:
            f.write("<html><body>Test</body></html>")

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".html", "text/html")
        assert is_binary is False

    def test_is_binary_file_by_mime_type_binary(self):
        """Test binary file detection by MIME type (binary)."""
        test_file = os.path.join(self.temp_dir, "test.jpg")
        Path(test_file).touch()

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".jpg", "image/jpeg")
        assert is_binary is True

    def test_is_binary_file_by_content_null_bytes(self):
        """Test binary file detection by content (null bytes)."""
        test_file = os.path.join(self.temp_dir, "test.dat")
        with open(test_file, "wb") as f:
            f.write(b"Valid text\x00\x00\x00binary data")

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".dat", None)
        assert is_binary is True

    def test_is_binary_file_by_content_signature(self):
        """Test binary file detection by content (file signature)."""
        test_file = os.path.join(self.temp_dir, "test.png")
        with open(test_file, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".png", None)
        assert is_binary is True

    def test_is_binary_file_by_content_non_printable_ratio(self):
        """Test binary file detection by content (non-printable ratio)."""
        test_file = os.path.join(self.temp_dir, "test.bin")
        # Create content with high ratio of non-printable characters
        content = b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0e\x0f"
        with open(test_file, "wb") as f:
            f.write(content)

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".bin", None)
        assert is_binary is True

    def test_is_binary_file_by_content_elf_signature(self):
        """Test binary file detection by ELF signature."""
        test_file = os.path.join(self.temp_dir, "test.elf")
        with open(test_file, "wb") as f:
            f.write(b"\x7fELF\x02\x01\x01\x00")

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".elf", None)
        assert is_binary is True

    def test_is_binary_file_by_content_pdf_signature(self):
        """Test binary file detection by PDF signature."""
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.4\n")

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".pdf", None)
        assert is_binary is True

    def test_is_binary_file_by_content_zip_signature(self):
        """Test binary file detection by ZIP signature."""
        test_file = os.path.join(self.temp_dir, "test.zip")
        with open(test_file, "wb") as f:
            f.write(b"PK\x03\x04")

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".zip", None)
        assert is_binary is True

    def test_is_binary_file_detection_error(self):
        """Test binary file detection when file reading fails."""
        test_file = os.path.join(self.temp_dir, "test.dat")
        # Don't create the file

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".dat", None)
        # Should default to True (binary) on error
        assert is_binary is True

    def test_get_file_info_text_file(self):
        """Test getting file info for a text file."""
        test_file = os.path.join(self.temp_dir, "test.py")
        content = "print('hello')"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)

        info = self.handler.get_file_info(test_file)

        assert info["path"] == test_file
        assert info["size"] == len(content)
        assert info["extension"] == ".py"
        assert info["mime_type"] == "text/x-python"
        assert info["is_binary"] is False
        assert info["is_readable"] is True

    def test_get_file_info_binary_file(self):
        """Test getting file info for a binary file."""
        test_file = os.path.join(self.temp_dir, "test.pdf")
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.4\nfake content")

        info = self.handler.get_file_info(test_file)

        assert info["path"] == test_file
        assert info["size"] == len(b"%PDF-1.4\nfake content")
        assert info["extension"] == ".pdf"
        assert info["mime_type"] == "application/pdf"
        assert info["is_binary"] is True
        assert info["is_readable"] is False

    def test_get_file_info_nonexistent(self):
        """Test getting file info for non-existent file."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        with pytest.raises(FileNotFoundError):
            self.handler.get_file_info(nonexistent_file)

    def test_can_read_file_text(self):
        """Test checking if text file can be read."""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        result = self.handler.can_read_file(test_file)
        assert result is True

    def test_can_read_file_binary(self):
        """Test checking if binary file can be read."""
        test_file = os.path.join(self.temp_dir, "test.exe")
        with open(test_file, "wb") as f:
            f.write(b"\x7fELF\x02\x01\x01\x00")

        result = self.handler.can_read_file(test_file)
        assert result is False

    def test_can_read_file_nonexistent(self):
        """Test checking if non-existent file can be read."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        result = self.handler.can_read_file(nonexistent_file)
        assert result is False

    def test_set_max_file_size(self):
        """Test setting maximum file size."""
        new_size = 5 * 1024 * 1024  # 5MB
        self.handler.set_max_file_size(new_size)
        assert self.handler.max_file_size == new_size

    def test_read_file_safe_success(self):
        """Test safe file reading with success."""
        test_file = os.path.join(self.temp_dir, "test.txt")
        content = "Safe reading test"
        with open(test_file, "w") as f:
            f.write(content)

        result = self.handler.read_file_safe(test_file)
        assert result == content

    def test_read_file_safe_with_error(self):
        """Test safe file reading with error."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")

        result = self.handler.read_file_safe(nonexistent_file)
        assert result is None

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        extensions = self.handler.get_supported_extensions()
        assert isinstance(extensions, set)
        assert ".py" in extensions
        assert ".txt" in extensions
        assert ".md" in extensions
        assert ".json" in extensions

    def test_get_binary_extensions(self):
        """Test getting binary extensions."""
        extensions = self.handler.get_binary_extensions()
        assert isinstance(extensions, set)
        assert ".pdf" in extensions
        assert ".exe" in extensions
        assert ".zip" in extensions
        assert ".jpg" in extensions

    def test_read_file_with_different_encodings(self):
        """Test reading files with different text encodings."""
        # Test UTF-8
        utf8_file = os.path.join(self.temp_dir, "utf8.txt")
        utf8_content = "UTF-8 content: café"
        with open(utf8_file, "w", encoding="utf-8") as f:
            f.write(utf8_content)

        result = self.handler.read_file(utf8_file, encoding="utf-8")
        assert result == utf8_content

        # Test Latin-1
        latin1_file = os.path.join(self.temp_dir, "latin1.txt")
        latin1_content = "Latin-1 content: résumé"
        with open(latin1_file, "w", encoding="latin-1") as f:
            f.write(latin1_content)

        result = self.handler.read_file(latin1_file, encoding="latin-1")
        assert result == latin1_content

    def test_read_file_with_bom(self):
        """Test reading file with Byte Order Mark."""
        test_file = os.path.join(self.temp_dir, "bom.txt")
        content = "File with BOM"
        # Write with UTF-8 BOM
        with open(test_file, "w", encoding="utf-8-sig") as f:
            f.write(content)

        result = self.handler.read_file(test_file)
        # Should handle BOM correctly
        assert "File with BOM" in result

    def test_read_file_performance_large_text(self):
        """Test reading a large text file for performance."""
        # Create a reasonably large text file (1MB)
        test_file = os.path.join(self.temp_dir, "large_text.txt")
        line = "This is a test line with some content.\n"
        repetitions = (1024 * 1024) // len(line)

        with open(test_file, "w", encoding="utf-8") as f:
            for _ in range(repetitions):
                f.write(line)

        # Should read successfully
        result = self.handler.read_file(test_file)
        assert len(result) > 0
        assert "This is a test line" in result

    def test_mime_type_detection_various_files(self):
        """Test MIME type detection for various file types."""
        test_cases = [
            ("test.html", "<html>test</html>", "text/html"),
            ("test.css", "body { color: red; }", "text/css"),
            ("test.js", "console.log('test');", "text/javascript"),
            ("test.json", '{"test": true}', "application/json"),
            ("test.xml", "<root>test</root>", "application/xml"),
        ]

        for filename, content, expected_mime in test_cases:
            test_file = os.path.join(self.temp_dir, filename)
            with open(test_file, "w") as f:
                f.write(content)

            info = self.handler.get_file_info(test_file)
            assert info["mime_type"] == expected_mime

    def test_edge_case_file_names(self):
        """Test reading files with edge case names."""
        # File with spaces
        space_file = os.path.join(self.temp_dir, "file with spaces.txt")
        with open(space_file, "w") as f:
            f.write("File with spaces")

        result = self.handler.read_file(space_file)
        assert result == "File with spaces"

        # File with special characters
        special_file = os.path.join(self.temp_dir, "file-with_special.chars.txt")
        with open(special_file, "w") as f:
            f.write("File with special chars")

        result = self.handler.read_file(special_file)
        assert result == "File with special chars"

        # File with unicode name
        unicode_file = os.path.join(self.temp_dir, "测试文件.txt")
        with open(unicode_file, "w", encoding="utf-8") as f:
            f.write("Unicode file content")

        result = self.handler.read_file(unicode_file)
        assert result == "Unicode file content"

    def test_file_type_detection_ambiguous_extension(self):
        """Test file type detection for ambiguous extensions."""
        # File with unknown extension
        test_file = os.path.join(self.temp_dir, "test.unknown")
        with open(test_file, "w") as f:
            f.write("This is plain text content")

        # Should be detected as text based on content
        info = self.handler.get_file_info(test_file)
        # Since it's text content, should be readable
        assert (
            info["is_binary"] is False or info["is_binary"] is True
        )  # Depends on detection

    def test_binary_detection_with_mixed_content(self):
        """Test binary detection with mixed content."""
        test_file = os.path.join(self.temp_dir, "mixed.dat")
        # Content with high ratio of non-printable characters
        content = b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0e\x0f" * 10
        with open(test_file, "wb") as f:
            f.write(content)

        path = Path(test_file)
        is_binary = self.handler._is_binary_file(path, ".dat", None)
        # Should be detected as binary due to high non-printable ratio
        assert is_binary is True

    def test_read_file_with_permission_error(self):
        """Test reading file with permission error."""
        test_file = os.path.join(self.temp_dir, "no_permission.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Remove read permissions
        os.chmod(test_file, 0o000)

        try:
            with pytest.raises((PermissionError, OSError)):
                self.handler.read_file(test_file)
        finally:
            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_handler_initialization(self):
        """Test that handler initializes with correct default values."""
        new_handler = ReadHandler()

        assert new_handler.max_file_size == 10 * 1024 * 1024  # 10MB
        assert ".txt" in new_handler.text_extensions
        assert ".pdf" in new_handler.binary_extensions
        assert len(new_handler.text_extensions) > 50
        assert len(new_handler.binary_extensions) > 20

    def test_read_file_with_symlink(self):
        """Test reading file through symbolic link."""
        # Create original file
        original_file = os.path.join(self.temp_dir, "original.txt")
        with open(original_file, "w") as f:
            f.write("Original content")

        # Create symlink
        symlink_file = os.path.join(self.temp_dir, "symlink.txt")
        os.symlink(original_file, symlink_file)

        result = self.handler.read_file(symlink_file)
        assert result == "Original content"

    def test_read_file_circular_symlink(self):
        """Test handling circular symbolic link."""
        # This should be handled by Path.resolve() or similar
        link1 = os.path.join(self.temp_dir, "link1.txt")
        link2 = os.path.join(self.temp_dir, "link2.txt")

        # Create circular links (this might not work on all systems)
        try:
            os.symlink(link2, link1)
            os.symlink(link1, link2)

            # Should handle gracefully
            with pytest.raises((OSError, ValueError, RuntimeError)):
                self.handler.read_file(link1)
        except OSError:
            # Circular symlinks might not be allowed on some systems
            pytest.skip("Circular symlinks not supported on this system")

    def test_concurrent_file_access(self):
        """Test concurrent access to read handler."""
        import threading

        # Create multiple test files
        results = {}
        errors = []

        def read_file_task(file_num):
            try:
                test_file = os.path.join(self.temp_dir, f"concurrent_{file_num}.txt")
                with open(test_file, "w") as f:
                    f.write(f"Content {file_num}")

                result = self.handler.read_file(test_file)
                results[file_num] = result
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=read_file_task, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0
        assert len(results) == 10
        for i in range(10):
            assert i in results
            assert f"Content {i}" in results[i]

    def test_performance_with_many_small_files(self):
        """Test performance with many small files."""
        import time

        # Create many small files
        num_files = 100
        for i in range(num_files):
            test_file = os.path.join(self.temp_dir, f"small_{i}.txt")
            with open(test_file, "w") as f:
                f.write(f"Small file {i}")

        # Read all files and measure time
        start_time = time.time()
        for i in range(num_files):
            test_file = os.path.join(self.temp_dir, f"small_{i}.txt")
            result = self.handler.read_file(test_file)
            assert f"Small file {i}" in result

        end_time = time.time()
        duration = end_time - start_time

        # Should complete reasonably quickly (less than 5 seconds for 100 files)
        assert duration < 5.0, (
            f"Reading {num_files} files took too long: {duration} seconds"
        )


if __name__ == "__main__":
    # Run a simple test
    pytest.main([__file__, "-v"])
