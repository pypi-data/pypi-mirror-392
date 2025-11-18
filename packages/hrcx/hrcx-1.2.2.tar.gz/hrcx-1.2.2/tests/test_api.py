"""Tests for the public API."""

import os
import tempfile
from pathlib import Path

import pytest

from hrcx.api import bind, split
from hrcx.horcrux import find_horcrux_files


class TestSplit:
    """Tests for split() function."""

    def test_split_basic(self):
        """Should split file into horcruxes successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.txt")
            test_content = b"This is a secret message!"
            with open(test_file, "wb") as f:
                f.write(test_content)

            # Split it
            output_dir = os.path.join(tmpdir, "horcruxes")
            split(test_file, total=5, threshold=3, output_dir=output_dir)

            # Verify horcrux files were created
            horcrux_files = find_horcrux_files(output_dir)
            assert len(horcrux_files) == 5
            
            # Verify all files exist and have content
            for horcrux_file in horcrux_files:
                assert os.path.exists(horcrux_file)
                assert os.path.getsize(horcrux_file) > 0

    def test_split_default_output_dir(self):
        """Should use same directory as input file by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"test content")

            split(test_file, total=3, threshold=2)

            # Should create horcruxes in same directory
            horcrux_files = find_horcrux_files(tmpdir)
            assert len(horcrux_files) == 3

    def test_split_nonexistent_file(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            split("/nonexistent/file.txt", total=3, threshold=2)

    def test_split_not_a_file(self):
        """Should raise ValueError for directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Not a file"):
                split(tmpdir, total=3, threshold=2)

    def test_split_invalid_threshold_too_low(self):
        """Should reject threshold < 2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"test")

            with pytest.raises(ValueError, match="Threshold must be at least 2"):
                split(test_file, total=3, threshold=1)

    def test_split_invalid_total_less_than_threshold(self):
        """Should reject total < threshold."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"test")

            with pytest.raises(ValueError, match="Total .* must be >= threshold"):
                split(test_file, total=2, threshold=5)

    def test_split_invalid_total_too_high(self):
        """Should reject total > 255."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"test")

            with pytest.raises(ValueError, match="Total cannot exceed 255"):
                split(test_file, total=256, threshold=128)

    def test_split_empty_file(self):
        """Should handle empty files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "empty.txt")
            Path(test_file).touch()

            split(test_file, total=3, threshold=2)

            horcrux_files = find_horcrux_files(tmpdir)
            assert len(horcrux_files) == 3

    def test_split_binary_file(self):
        """Should handle binary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "binary.dat")
            test_content = bytes(range(256)) * 10
            with open(test_file, "wb") as f:
                f.write(test_content)

            split(test_file, total=4, threshold=3)

            horcrux_files = find_horcrux_files(tmpdir)
            assert len(horcrux_files) == 4


class TestBind:
    """Tests for bind() function."""

    def test_bind_basic(self):
        """Should reconstruct file from horcruxes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and split test file
            test_file = os.path.join(tmpdir, "original.txt")
            test_content = b"This is the original content!"
            with open(test_file, "wb") as f:
                f.write(test_content)

            split(test_file, total=5, threshold=3)

            # Remove original
            os.remove(test_file)

            # Get horcrux files and use only 3 (threshold)
            horcrux_files = find_horcrux_files(tmpdir)
            selected_horcruxes = horcrux_files[:3]

            # Reconstruct
            bind(selected_horcruxes)

            # Verify reconstructed file
            assert os.path.exists(test_file)
            with open(test_file, "rb") as f:
                reconstructed = f.read()
            assert reconstructed == test_content

    def test_bind_with_all_horcruxes(self):
        """Should work when using all horcruxes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            test_content = b"Secret data"
            with open(test_file, "wb") as f:
                f.write(test_content)

            split(test_file, total=3, threshold=2)
            os.remove(test_file)

            horcrux_files = find_horcrux_files(tmpdir)
            bind(horcrux_files)

            with open(test_file, "rb") as f:
                reconstructed = f.read()
            assert reconstructed == test_content

    def test_bind_custom_output_path(self):
        """Should write to custom output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "original.txt")
            test_content = b"Original content"
            with open(test_file, "wb") as f:
                f.write(test_content)

            split(test_file, total=3, threshold=2)

            horcrux_files = find_horcrux_files(tmpdir)
            output_path = os.path.join(tmpdir, "restored.txt")
            bind(horcrux_files, output_path=output_path)

            assert os.path.exists(output_path)
            with open(output_path, "rb") as f:
                reconstructed = f.read()
            assert reconstructed == test_content

    def test_bind_overwrite_protection(self):
        """Should refuse to overwrite existing file without flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"original")

            split(test_file, total=3, threshold=2)

            horcrux_files = find_horcrux_files(tmpdir)

            # Original file still exists, should fail
            with pytest.raises(FileExistsError, match="already exists"):
                bind(horcrux_files)

    def test_bind_overwrite_allowed(self):
        """Should overwrite when overwrite=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            original_content = b"original"
            with open(test_file, "wb") as f:
                f.write(original_content)

            split(test_file, total=3, threshold=2)

            # Modify the file
            with open(test_file, "wb") as f:
                f.write(b"modified")

            horcrux_files = find_horcrux_files(tmpdir)
            bind(horcrux_files, overwrite=True)

            # Should have original content back
            with open(test_file, "rb") as f:
                reconstructed = f.read()
            assert reconstructed == original_content

    def test_bind_no_horcruxes(self):
        """Should raise ValueError for empty horcrux list."""
        with pytest.raises(ValueError, match="No horcrux files provided"):
            bind([])

    def test_bind_insufficient_horcruxes(self):
        """Should raise ValueError when not enough horcruxes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"test content")

            split(test_file, total=5, threshold=3)

            horcrux_files = find_horcrux_files(tmpdir)
            # Only use 2 horcruxes (need 3)
            with pytest.raises(ValueError, match="Insufficient horcruxes"):
                bind(horcrux_files[:2])

    def test_bind_mismatched_original_filename(self):
        """Should reject horcruxes from different files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two different files and split them
            file1 = os.path.join(tmpdir, "dir1", "file1.txt")
            file2 = os.path.join(tmpdir, "dir2", "file2.txt")
            os.makedirs(os.path.dirname(file1))
            os.makedirs(os.path.dirname(file2))
            
            with open(file1, "wb") as f:
                f.write(b"content1")
            with open(file2, "wb") as f:
                f.write(b"content2")

            split(file1, total=3, threshold=2)
            split(file2, total=3, threshold=2)

            horcruxes1 = find_horcrux_files(os.path.dirname(file1))
            horcruxes2 = find_horcrux_files(os.path.dirname(file2))

            # Try to mix horcruxes from different files
            with pytest.raises(ValueError, match="different original files"):
                bind([horcruxes1[0], horcruxes2[0]])

    def test_bind_duplicate_indices(self):
        """Should reject duplicate horcrux indices."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "wb") as f:
                f.write(b"test")

            split(test_file, total=3, threshold=2)

            horcrux_files = find_horcrux_files(tmpdir)
            # Use same horcrux twice
            with pytest.raises(ValueError, match="Duplicate horcrux indices"):
                bind([horcrux_files[0], horcrux_files[0]])

    def test_bind_binary_file(self):
        """Should handle binary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "binary.dat")
            test_content = bytes(range(256)) * 10
            with open(test_file, "wb") as f:
                f.write(test_content)

            split(test_file, total=4, threshold=3)
            os.remove(test_file)

            horcrux_files = find_horcrux_files(tmpdir)
            bind(horcrux_files[:3])  # Use exactly threshold

            with open(test_file, "rb") as f:
                reconstructed = f.read()
            assert reconstructed == test_content


class TestIntegration:
    """End-to-end integration tests."""

    def test_split_bind_roundtrip(self):
        """Complete roundtrip: split and bind should restore original file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_file = os.path.join(tmpdir, "document.pdf")
            original_content = b"PDF" + bytes(range(256)) * 100
            with open(original_file, "wb") as f:
                f.write(original_content)

            # Split
            split(original_file, total=7, threshold=4)

            # Remove original
            os.remove(original_file)

            # Bind with subset of horcruxes
            horcrux_files = find_horcrux_files(tmpdir)
            bind(horcrux_files[1:5])  # Use 4 horcruxes (exactly threshold)

            # Verify
            with open(original_file, "rb") as f:
                restored = f.read()
            assert restored == original_content

    def test_multiple_files_same_directory(self):
        """Should handle multiple files in same directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = os.path.join(tmpdir, "file1.txt")
            file2 = os.path.join(tmpdir, "file2.txt")
            
            with open(file1, "wb") as f:
                f.write(b"content of file 1")
            with open(file2, "wb") as f:
                f.write(b"content of file 2")

            # Split both
            output1 = os.path.join(tmpdir, "vault1")
            output2 = os.path.join(tmpdir, "vault2")
            split(file1, total=3, threshold=2, output_dir=output1)
            split(file2, total=3, threshold=2, output_dir=output2)

            # Should have separate horcrux sets
            horcruxes1 = find_horcrux_files(output1)
            horcruxes2 = find_horcrux_files(output2)
            assert len(horcruxes1) == 3
            assert len(horcruxes2) == 3

            # Remove originals
            os.remove(file1)
            os.remove(file2)

            # Reconstruct both
            bind(horcruxes1, output_path=file1)
            bind(horcruxes2, output_path=file2)

            with open(file1, "rb") as f:
                assert f.read() == b"content of file 1"
            with open(file2, "rb") as f:
                assert f.read() == b"content of file 2"
