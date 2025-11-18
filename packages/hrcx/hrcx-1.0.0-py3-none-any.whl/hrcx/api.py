"""
Public API for Horcrux file operations.

This module provides the main split() and bind() functions for the library interface.
"""

import os
from pathlib import Path
from typing import List, Optional

from .crypto import encrypt, generate_key
from .horcrux import generate_horcrux_filename, write_horcrux
from .shamir import split as shamir_split


def split(
    file_path: str,
    total: int,
    threshold: int,
    output_dir: Optional[str] = None
) -> None:
    """
    Split a file into encrypted horcruxes using Shamir's Secret Sharing.
    
    This function encrypts the input file with AES-256-GCM and splits the encryption
    key into N fragments using Shamir's Secret Sharing, where any K fragments can
    reconstruct the original key and decrypt the file.
    
    Args:
        file_path: Path to the file to split
        total: Total number of horcruxes to create (must be >= threshold)
        threshold: Minimum number of horcruxes needed to reconstruct (must be >= 2)
        output_dir: Optional output directory for horcruxes (default: same as input file)
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If total < threshold or threshold < 2
        PermissionError: If unable to write to output directory
        
    Example:
        >>> split("secret.txt", total=5, threshold=3, output_dir="./vault")
        # Creates: secret_1_of_5.hrcx, secret_2_of_5.hrcx, ...
    """
    # Validate input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not os.path.isfile(file_path):
        raise ValueError(f"Not a file: {file_path}")
    
    # Validate parameters
    if threshold < 2:
        raise ValueError(f"Threshold must be at least 2, got {threshold}")
    
    if total < threshold:
        raise ValueError(f"Total ({total}) must be >= threshold ({threshold})")
    
    if total > 255:
        raise ValueError(f"Total cannot exceed 255, got {total}")
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(file_path))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the input file
    with open(file_path, "rb") as f:
        plaintext = f.read()
    
    # Generate encryption key and encrypt the file
    key = generate_key()
    nonce, ciphertext = encrypt(plaintext, key)
    
    # Split the key into shares using Shamir's Secret Sharing
    key_shares = shamir_split(key, total, threshold)
    
    # Get original filename (without path)
    original_filename = os.path.basename(file_path)
    
    # Create horcrux files
    for index in range(1, total + 1):
        horcrux_filename = generate_horcrux_filename(original_filename, index, total)
        horcrux_path = os.path.join(output_dir, horcrux_filename)
        
        # Each horcrux gets the same encrypted content and nonce, but a different key share
        write_horcrux(
            output_path=horcrux_path,
            original_filename=original_filename,
            index=index,
            total=total,
            threshold=threshold,
            key_fragment=key_shares[index - 1],  # Convert 1-based to 0-based index
            nonce=nonce,
            encrypted_content=ciphertext,
        )
        
        print(f"Created: {horcrux_path}")


def bind(
    horcrux_paths: List[str],
    output_path: Optional[str] = None,
    overwrite: bool = False
) -> None:
    """
    Reconstruct the original file from horcruxes.
    
    This function takes K or more horcrux files, reconstructs the encryption key
    using Shamir's Secret Sharing, and decrypts the original file using AES-256-GCM.
    
    Args:
        horcrux_paths: List of paths to horcrux files (must have >= threshold files)
        output_path: Optional output file path (default: original filename from horcrux metadata)
        overwrite: If True, overwrite existing file without prompting
    
    Raises:
        FileNotFoundError: If any horcrux file doesn't exist
        ValueError: If insufficient horcruxes provided or files are incompatible
        FileExistsError: If output file exists and overwrite=False
        
    Example:
        >>> bind(["secret_1_of_5.hrcx", "secret_3_of_5.hrcx", "secret_5_of_5.hrcx"])
        # Reconstructs: secret.txt
    """
    from .crypto import decrypt
    from .horcrux import read_horcrux
    from .shamir import combine as shamir_combine
    
    # Validate we have at least one horcrux
    if not horcrux_paths:
        raise ValueError("No horcrux files provided")
    
    # Read all horcrux files
    headers = []
    encrypted_contents = []
    key_fragments = []
    
    for horcrux_path in horcrux_paths:
        if not os.path.exists(horcrux_path):
            raise FileNotFoundError(f"Horcrux file not found: {horcrux_path}")
        
        header, encrypted_content = read_horcrux(horcrux_path)
        headers.append(header)
        encrypted_contents.append(encrypted_content)
        key_fragments.append(header.key_fragment)
    
    # Validate all horcruxes are from the same set
    first_header = headers[0]
    for i, header in enumerate(headers[1:], start=1):
        if header.original_filename != first_header.original_filename:
            raise ValueError(
                f"Horcrux files are from different original files: "
                f"{first_header.original_filename} vs {header.original_filename}"
            )
        if header.timestamp != first_header.timestamp:
            raise ValueError(
                f"Horcrux files have different timestamps (from different split operations)"
            )
        if header.total != first_header.total:
            raise ValueError(
                f"Horcrux files have different total counts: "
                f"{first_header.total} vs {header.total}"
            )
        if header.threshold != first_header.threshold:
            raise ValueError(
                f"Horcrux files have different thresholds: "
                f"{first_header.threshold} vs {header.threshold}"
            )
        if header.nonce != first_header.nonce:
            raise ValueError("Horcrux files have different nonces (corrupted)")
    
    # Check for duplicate indices
    indices = [h.index for h in headers]
    if len(indices) != len(set(indices)):
        raise ValueError("Duplicate horcrux indices found")
    
    # Validate we have enough horcruxes
    if len(horcrux_paths) < first_header.threshold:
        raise ValueError(
            f"Insufficient horcruxes: need at least {first_header.threshold}, "
            f"but only have {len(horcrux_paths)}"
        )
    
    # Validate all encrypted contents are identical
    # (All horcruxes contain the same encrypted file)
    for i, content in enumerate(encrypted_contents[1:], start=1):
        if content != encrypted_contents[0]:
            raise ValueError(
                f"Horcrux {i+1} has different encrypted content (corrupted)"
            )
    
    # Reconstruct the encryption key from key fragments
    key = shamir_combine(key_fragments)
    
    # Decrypt the file
    nonce = first_header.nonce
    ciphertext = encrypted_contents[0]
    plaintext = decrypt(ciphertext, key, nonce)
    
    # Determine output path
    if output_path is None:
        # Default to same directory as first horcrux file
        horcrux_dir = os.path.dirname(os.path.abspath(horcrux_paths[0]))
        output_path = os.path.join(horcrux_dir, first_header.original_filename)
    
    # Check if output file already exists
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {output_path}. "
            f"Use overwrite=True to replace it."
        )
    
    # Write the reconstructed file
    with open(output_path, "wb") as f:
        f.write(plaintext)
    
    print(f"Reconstructed: {output_path}")
