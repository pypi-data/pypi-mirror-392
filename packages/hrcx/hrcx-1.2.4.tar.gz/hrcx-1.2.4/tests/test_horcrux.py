"""
Tests for the horcrux file format module.

Tests header creation, file I/O, and file discovery functionality.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from hrcx.horcrux import (
    HORCRUX_EXTENSION,
    HorcruxHeader,
    create_horcrux_header,
    find_horcrux_files,
    generate_horcrux_filename,
    read_horcrux,
    write_horcrux,
)


class TestHorcruxHeader:
    """Tests for HorcruxHeader dataclass."""

    def test_to_dict(self):
        """Header should serialize to dict with base64-encoded bytes."""
        header = HorcruxHeader(
            original_filename="test.txt",
            timestamp=1234567890,
            index=1,
            total=5,
            threshold=3,
            key_fragment=b"\x01\x02\x03",
            nonce=b"\x04\x05\x06",
        )

        result = header.to_dict()

        assert result["originalFilename"] == "test.txt"
        assert result["timestamp"] == 1234567890
        assert result["index"] == 1
        assert result["total"] == 5
        assert result["threshold"] == 3
        # Base64 encoded values
        assert isinstance(result["keyFragment"], str)
        assert isinstance(result["nonce"], str)

    def test_from_dict(self):
        """Header should deserialize from dict."""
        import base64

        data = {
            "originalFilename": "test.txt",
            "timestamp": 1234567890,
            "index": 2,
            "total": 5,
            "threshold": 3,
            "keyFragment": base64.b64encode(b"\x01\x02\x03").decode("ascii"),
            "nonce": base64.b64encode(b"\x04\x05\x06").decode("ascii"),
        }

        header = HorcruxHeader.from_dict(data)

        assert header.original_filename == "test.txt"
        assert header.timestamp == 1234567890
        assert header.index == 2
        assert header.total == 5
        assert header.threshold == 3
        assert header.key_fragment == b"\x01\x02\x03"
        assert header.nonce == b"\x04\x05\x06"

    def test_roundtrip(self):
        """Header should roundtrip through dict conversion."""
        original = HorcruxHeader(
            original_filename="secret.pdf",
            timestamp=9876543210,
            index=3,
            total=7,
            threshold=4,
            key_fragment=b"test_key_fragment",
            nonce=b"test_nonce",
        )

        data = original.to_dict()
        restored = HorcruxHeader.from_dict(data)

        assert restored == original


class TestCreateHorcruxHeader:
    """Tests for create_horcrux_header function."""

    def test_creates_valid_header(self):
        """Should create header with all required sections."""
        header = create_horcrux_header(
            original_filename="test.txt",
            index=1,
            total=5,
            threshold=3,
            key_fragment=b"key123",
            nonce=b"nonce123",
            timestamp=1234567890,
        )

        assert "# THIS FILE IS A HORCRUX." in header
        assert "THIS IS HORCRUX NUMBER 1." in header
        assert "ONE OF 5 HORCRUXES" in header
        assert "-- HEADER --" in header
        assert "-- BODY --" in header
        assert "originalFilename" in header
        assert "test.txt" in header

    def test_contains_valid_json(self):
        """Header should contain valid JSON metadata."""
        header = create_horcrux_header(
            original_filename="test.txt",
            index=2,
            total=4,
            threshold=3,
            key_fragment=b"key",
            nonce=b"nonce",
            timestamp=1234567890,
        )

        # Extract JSON between markers
        start = header.index("-- HEADER --") + len("-- HEADER --\n")
        end = header.index("-- BODY --")
        json_str = header[start:end].strip()

        data = json.loads(json_str)
        assert data["originalFilename"] == "test.txt"
        assert data["index"] == 2
        assert data["total"] == 4
        assert data["threshold"] == 3

    def test_default_timestamp(self):
        """Should use current timestamp if not provided."""
        before = int(datetime.now().timestamp())

        header = create_horcrux_header(
            original_filename="test.txt",
            index=1,
            total=3,
            threshold=2,
            key_fragment=b"key",
            nonce=b"nonce",
        )

        after = int(datetime.now().timestamp())

        # Extract timestamp from JSON
        start = header.index("-- HEADER --") + len("-- HEADER --\n")
        end = header.index("-- BODY --")
        json_str = header[start:end].strip()
        data = json.loads(json_str)

        assert before <= data["timestamp"] <= after


class TestWriteAndReadHorcrux:
    """Tests for write_horcrux and read_horcrux functions."""

    def test_write_and_read_roundtrip(self):
        """Should write and read horcrux file correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_1_of_3.hrcx")
            key_fragment = b"test_key_fragment_data"
            nonce = b"test_nonce12"
            encrypted_content = b"encrypted data goes here"

            write_horcrux(
                output_path=output_path,
                original_filename="secret.txt",
                index=1,
                total=3,
                threshold=2,
                key_fragment=key_fragment,
                nonce=nonce,
                encrypted_content=encrypted_content,
                timestamp=1234567890,
            )

            # Read it back
            header, content = read_horcrux(output_path)

            assert header.original_filename == "secret.txt"
            assert header.index == 1
            assert header.total == 3
            assert header.threshold == 2
            assert header.timestamp == 1234567890
            assert header.key_fragment == key_fragment
            assert header.nonce == nonce
            assert content == encrypted_content

    def test_write_creates_directory(self):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_path = os.path.join(tmpdir, "nested", "dir", "test.hrcx")

            write_horcrux(
                output_path=nested_path,
                original_filename="test.txt",
                index=1,
                total=2,
                threshold=2,
                key_fragment=b"key",
                nonce=b"nonce",
                encrypted_content=b"data",
            )

            assert os.path.exists(nested_path)

    def test_read_nonexistent_file(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            read_horcrux("/nonexistent/file.hrcx")

    def test_read_invalid_format(self):
        """Should raise ValueError for invalid file format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".hrcx", delete=False) as f:
            f.write("This is not a valid horcrux file\n")
            f.write("No header markers here\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid horcrux file format"):
                read_horcrux(temp_path)
        finally:
            os.unlink(temp_path)

    def test_read_invalid_json(self):
        """Should raise ValueError for malformed JSON header."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".hrcx", delete=False) as f:
            f.write("-- HEADER --\n")
            f.write("{invalid json}\n")
            f.write("-- BODY --\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Failed to parse horcrux header"):
                read_horcrux(temp_path)
        finally:
            os.unlink(temp_path)

    def test_handles_binary_content(self):
        """Should correctly handle binary encrypted content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "binary_test.hrcx")
            # Binary content with all byte values
            encrypted_content = bytes(range(256))

            write_horcrux(
                output_path=output_path,
                original_filename="binary.dat",
                index=1,
                total=1,
                threshold=1,
                key_fragment=b"key",
                nonce=b"nonce",
                encrypted_content=encrypted_content,
            )

            header, content = read_horcrux(output_path)
            assert content == encrypted_content


class TestFindHorcruxFiles:
    """Tests for find_horcrux_files function."""

    def test_finds_horcrux_files(self):
        """Should find all .hrcx files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some horcrux files
            Path(tmpdir, "test_1_of_3.hrcx").touch()
            Path(tmpdir, "test_2_of_3.hrcx").touch()
            Path(tmpdir, "test_3_of_3.hrcx").touch()
            # Create non-horcrux files
            Path(tmpdir, "readme.txt").touch()
            Path(tmpdir, "data.bin").touch()

            files = find_horcrux_files(tmpdir)

            assert len(files) == 3
            assert all(f.endswith(HORCRUX_EXTENSION) for f in files)
            assert all(os.path.isabs(f) for f in files)

    def test_empty_directory(self):
        """Should return empty list for directory with no horcrux files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "other.txt").touch()

            files = find_horcrux_files(tmpdir)

            assert files == []

    def test_nonexistent_directory(self):
        """Should raise FileNotFoundError for missing directory."""
        with pytest.raises(FileNotFoundError):
            find_horcrux_files("/nonexistent/directory")

    def test_not_a_directory(self):
        """Should raise NotADirectoryError for file path."""
        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises(NotADirectoryError):
                find_horcrux_files(f.name)

    def test_sorted_output(self):
        """Should return files in sorted order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files in non-alphabetical order
            Path(tmpdir, "z_3_of_3.hrcx").touch()
            Path(tmpdir, "a_1_of_3.hrcx").touch()
            Path(tmpdir, "m_2_of_3.hrcx").touch()

            files = find_horcrux_files(tmpdir)

            basenames = [os.path.basename(f) for f in files]
            assert basenames == sorted(basenames)


class TestGenerateHorcruxFilename:
    """Tests for generate_horcrux_filename function."""

    def test_basic_filename(self):
        """Should generate correct filename format."""
        result = generate_horcrux_filename("test.txt", 1, 5)
        assert result == "test_1_of_5.hrcx"

    def test_strips_extension(self):
        """Should remove original file extension."""
        result = generate_horcrux_filename("document.pdf", 3, 7)
        assert result == "document_3_of_7.hrcx"

    def test_no_extension(self):
        """Should work with files without extension."""
        result = generate_horcrux_filename("README", 2, 4)
        assert result == "README_2_of_4.hrcx"

    def test_multiple_dots(self):
        """Should handle filenames with multiple dots."""
        result = generate_horcrux_filename("archive.tar.gz", 1, 3)
        assert result == "archive.tar_1_of_3.hrcx"

    def test_path_with_directories(self):
        """Should use only the basename."""
        result = generate_horcrux_filename("/path/to/file.txt", 4, 9)
        assert result == "file_4_of_9.hrcx"
