"""
Horcrux file format handling.

This module defines the .hrcx file format and provides functions for reading
and writing horcrux files. Each horcrux contains:
- A human-readable header with metadata (JSON)
- Encrypted file content
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Horcrux file extension
HORCRUX_EXTENSION = ".hrcx"


@dataclass
class HorcruxHeader:
    """
    Metadata header for a horcrux file.
    
    Attributes:
        original_filename: Name of the original file that was split
        timestamp: Unix timestamp when the file was split
        index: This horcrux's index (1-based)
        total: Total number of horcruxes created
        threshold: Minimum number of horcruxes needed to reconstruct
        key_fragment: This horcrux's share of the encryption key
        nonce: Nonce used for AES-GCM encryption (same for all horcruxes)
    """

    original_filename: str
    timestamp: int
    index: int
    total: int
    threshold: int
    key_fragment: bytes
    nonce: bytes

    def to_dict(self) -> dict:
        """
        Convert header to dictionary for JSON serialization.
        
        Returns:
            Dictionary with base64-encoded binary fields
        """
        import base64

        return {
            "originalFilename": self.original_filename,
            "timestamp": self.timestamp,
            "index": self.index,
            "total": self.total,
            "threshold": self.threshold,
            "keyFragment": base64.b64encode(self.key_fragment).decode("ascii"),
            "nonce": base64.b64encode(self.nonce).decode("ascii"),
        }

    @staticmethod
    def from_dict(data: dict) -> "HorcruxHeader":
        """
        Create header from dictionary (JSON deserialization).
        
        Args:
            data: Dictionary with header fields
        
        Returns:
            HorcruxHeader instance
        
        Raises:
            KeyError: If required fields are missing
            ValueError: If base64 decoding fails
        """
        import base64

        return HorcruxHeader(
            original_filename=data["originalFilename"],
            timestamp=data["timestamp"],
            index=data["index"],
            total=data["total"],
            threshold=data["threshold"],
            key_fragment=base64.b64decode(data["keyFragment"]),
            nonce=base64.b64decode(data["nonce"]),
        )


def create_horcrux_header(
    original_filename: str,
    index: int,
    total: int,
    threshold: int,
    key_fragment: bytes,
    nonce: bytes,
    timestamp: Optional[int] = None,
) -> str:
    """
    Create the header section of a horcrux file.
    
    Args:
        original_filename: Name of the original file
        index: This horcrux's index (1-based)
        total: Total number of horcruxes
        threshold: Minimum horcruxes needed to reconstruct
        key_fragment: This horcrux's key share
        nonce: Encryption nonce
        timestamp: Optional Unix timestamp (defaults to current time)
    
    Returns:
        Complete header string including banner and JSON metadata
    """
    if timestamp is None:
        timestamp = int(datetime.now().timestamp())

    header = HorcruxHeader(
        original_filename=original_filename,
        timestamp=timestamp,
        index=index,
        total=total,
        threshold=threshold,
        key_fragment=key_fragment,
        nonce=nonce,
    )

    header_json = json.dumps(header.to_dict(), indent=2)

    # Calculate how many more horcruxes are needed (threshold - 1 since we have this one)
    others_needed = threshold - 1
    
    banner = f"""# THIS FILE IS A HORCRUX.
# IT IS ONE OF {total} HORCRUXES THAT EACH CONTAIN PART OF AN ORIGINAL FILE.
# THIS IS HORCRUX NUMBER {index}.
# IN ORDER TO RESURRECT THIS ORIGINAL FILE YOU MUST FIND AT LEAST {others_needed} OTHER HORCRUX(ES) AND THEN BIND THEM USING THE HRCX PROGRAM
# https://pypi.org/project/hrcx/
# https://github.com/juliuspleunes4/horcrux

-- HEADER --
{header_json}
-- BODY --
"""
    return banner


def write_horcrux(
    output_path: str,
    original_filename: str,
    index: int,
    total: int,
    threshold: int,
    key_fragment: bytes,
    nonce: bytes,
    encrypted_content: bytes,
    timestamp: Optional[int] = None,
) -> None:
    """
    Write a complete horcrux file to disk.
    
    Args:
        output_path: Path where the horcrux file will be written
        original_filename: Name of the original file
        index: This horcrux's index (1-based)
        total: Total number of horcruxes
        threshold: Minimum horcruxes needed to reconstruct
        key_fragment: This horcrux's key share
        nonce: Encryption nonce
        encrypted_content: Encrypted file content
        timestamp: Optional Unix timestamp (defaults to current time)
    
    Raises:
        OSError: If unable to write file
        PermissionError: If lacking write permissions
    """
    # Ensure parent directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    header = create_horcrux_header(
        original_filename, index, total, threshold, key_fragment, nonce, timestamp
    )

    with open(output_path, "wb") as f:
        # Write header as UTF-8 text
        f.write(header.encode("utf-8"))
        # Write encrypted content as binary
        f.write(encrypted_content)


def read_horcrux(file_path: str) -> tuple[HorcruxHeader, bytes]:
    """
    Read and parse a horcrux file.
    
    Reads the header metadata and encrypted content from a horcrux file.
    
    Args:
        file_path: Path to the horcrux file
    
    Returns:
        Tuple of (header, encrypted_content)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid or header can't be parsed
        OSError: If unable to read file
    """
    with open(file_path, "rb") as f:
        content = f.read()

    # Find the header section
    try:
        header_start = content.index(b"-- HEADER --")
        body_start = content.index(b"-- BODY --")
    except ValueError:
        raise ValueError(f"Invalid horcrux file format: {file_path}")

    # Extract JSON header (between -- HEADER -- and -- BODY --)
    header_json_start = header_start + len(b"-- HEADER --\n")
    header_json_bytes = content[header_json_start:body_start].strip()

    try:
        header_dict = json.loads(header_json_bytes.decode("utf-8"))
        header = HorcruxHeader.from_dict(header_dict)
    except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to parse horcrux header: {e}")

    # Extract encrypted content (after -- BODY --)
    encrypted_start = body_start + len(b"-- BODY --\n")
    encrypted_content = content[encrypted_start:]

    return header, encrypted_content


def find_horcrux_files(directory: str) -> List[str]:
    """
    Find all horcrux files in a directory.
    
    Args:
        directory: Path to directory to search
    
    Returns:
        List of absolute paths to .hrcx files
    
    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    horcrux_files = sorted(dir_path.glob(f"*{HORCRUX_EXTENSION}"))
    return [str(f.absolute()) for f in horcrux_files]


def generate_horcrux_filename(original_filename: str, index: int, total: int) -> str:
    """
    Generate a horcrux filename following the naming convention.
    
    Format: {basename}_{index}_of_{total}.hrcx
    
    Args:
        original_filename: Name of original file
        index: Horcrux index (1-based)
        total: Total number of horcruxes
    
    Returns:
        Horcrux filename
    
    Example:
        >>> generate_horcrux_filename("secret.txt", 1, 5)
        'secret_1_of_5.hrcx'
        >>> generate_horcrux_filename("photo.jpg", 3, 7)
        'photo_3_of_7.hrcx'
    """
    # Remove extension from original filename
    basename = Path(original_filename).stem
    return f"{basename}_{index}_of_{total}{HORCRUX_EXTENSION}"
