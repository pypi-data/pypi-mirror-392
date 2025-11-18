"""
Interactive CLI for Horcrux - User-friendly interface for non-technical users.

This module provides a beautiful, color-coded interactive interface for splitting
and binding files using the Horcrux encryption system.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

import click
from colorama import Fore, Style, init

from hrcx import split, bind
from hrcx.horcrux.format import find_horcrux_files

# Initialize colorama for Windows support
init(autoreset=True)

# Version info
VERSION = "1.2.4"
PYPI_URL = "https://pypi.org/project/hrcx/"
GITHUB_URL = "https://github.com/juliuspleunes4/Horcrux"


def print_header() -> None:
    """
    Print the beautiful HORCRUX ASCII art header with version info.
    
    Displays a blue ASCII art logo with grey metadata including version,
    PyPI package link, and GitHub repository link.
    """
    # Clear screen for clean presentation
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # ASCII art in ocean blue (bigger version)
    ascii_art = f"""{Fore.BLUE}{Style.BRIGHT}
    ██╗  ██╗ ██████╗ ██████╗  ██████╗██████╗ ██╗   ██╗██╗  ██╗
    ██║  ██║██╔═══██╗██╔══██╗██╔════╝██╔══██╗██║   ██║╚██╗██╔╝
    ███████║██║   ██║██████╔╝██║     ██████╔╝██║   ██║ ╚███╔╝ 
    ██╔══██║██║   ██║██╔══██╗██║     ██╔══██╗██║   ██║ ██╔██╗ 
    ██║  ██║╚██████╔╝██║  ██║╚██████╗██║  ██║╚██████╔╝██╔╝ ██╗
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
    {Style.RESET_ALL}"""
    
    print(ascii_art)
    print(f"{Fore.LIGHTBLACK_EX}------------------------------------------------------------")
    print(f"{Fore.LIGHTBLACK_EX}  Split your files into encrypted fragments.")
    print(f"{Fore.LIGHTBLACK_EX}  Version:  {VERSION}")
    print(f"{Fore.LIGHTBLACK_EX}  PyPI:     {PYPI_URL}")
    print(f"{Fore.LIGHTBLACK_EX}  GitHub:   {GITHUB_URL}")
    print(f"{Fore.LIGHTBLACK_EX}------------------------------------------------------------")
    print(f"{Style.RESET_ALL}")


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str) -> None:
    """Print an info message in cyan."""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_prompt(message: str) -> None:
    """Print a prompt message in white/bright."""
    print(f"{Fore.WHITE}{Style.BRIGHT}{message}{Style.RESET_ALL}", end="")


def get_choice(prompt: str, options: List[str]) -> str:
    """
    Get a validated choice from the user.
    
    Args:
        prompt: The prompt message to display
        options: List of valid options (case-insensitive)
    
    Returns:
        The validated user choice (lowercase)
    """
    while True:
        try:
            print_prompt(f"{prompt} ")
            choice = input().strip().lower()
            
            if choice in [opt.lower() for opt in options]:
                return choice
            
            print_error(f"Invalid choice. Please choose from: {', '.join(options)}")
            print()
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:
            print_error(f"Input error: {str(e)}")
            print()


def get_file_path(prompt: str, must_exist: bool = True) -> str:
    """
    Get a validated file path from the user.
    
    Args:
        prompt: The prompt message to display
        must_exist: Whether the file must already exist
    
    Returns:
        The validated absolute file path
    """
    while True:
        try:
            print_prompt(f"{prompt} ")
            path = input().strip().strip('"').strip("'")
            
            if not path:
                print_error("Path cannot be empty.")
                print()
                continue
            
            # Handle common folder shortcuts (case-insensitive)
            path_lower = path.lower().rstrip('/\\')  # Remove trailing slashes
            common_folders = {
                'desktop': os.path.join(os.path.expanduser('~'), 'Desktop'),
                'downloads': os.path.join(os.path.expanduser('~'), 'Downloads'),
                'documents': os.path.join(os.path.expanduser('~'), 'Documents'),
                'pictures': os.path.join(os.path.expanduser('~'), 'Pictures'),
                'videos': os.path.join(os.path.expanduser('~'), 'Videos'),
                'music': os.path.join(os.path.expanduser('~'), 'Music'),
            }
            
            # Check if path is exactly a common folder name (after stripping slashes)
            if path_lower in common_folders:
                path = common_folders[path_lower]
            # Check if path starts with a common folder name
            else:
                original_path_lower = path.lower()
                for folder_name, folder_path in common_folders.items():
                    if original_path_lower.startswith(folder_name + '\\') or original_path_lower.startswith(folder_name + '/'):
                        # Replace the folder name with the actual path
                        remaining_path = path[len(folder_name)+1:]
                        path = os.path.join(folder_path, remaining_path)
                        break
            
            # Expand user home directory (~)
            path = os.path.expanduser(path)
            
            # Expand environment variables
            path = os.path.expandvars(path)
            
            # Convert to absolute path
            abs_path = os.path.abspath(path)
            
            if must_exist and not os.path.exists(abs_path):
                print_error(f"File or directory does not exist: {abs_path}")
                print_info(f"Tip: Try 'Desktop\\file.txt', '~\\Desktop\\file.txt', or full path")
                print()
                continue
            
            if must_exist and not os.path.isfile(abs_path):
                print_error(f"Path is not a file: {abs_path}")
                print()
                continue
            
            return abs_path
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:
            print_error(f"Input error: {str(e)}")
            print()


def get_directory_path(prompt: str, must_exist: bool = False) -> str:
    """
    Get a validated directory path from the user.
    
    Args:
        prompt: The prompt message to display
        must_exist: Whether the directory must already exist
    
    Returns:
        The validated absolute directory path
    """
    while True:
        try:
            print_prompt(f"{prompt} ")
            path = input().strip().strip('"').strip("'")
            
            if not path:
                print_error("Path cannot be empty.")
                print()
                continue
            
            # Handle common folder shortcuts (case-insensitive)
            path_lower = path.lower().rstrip('/\\')  # Remove trailing slashes
            common_folders = {
                'desktop': os.path.join(os.path.expanduser('~'), 'Desktop'),
                'downloads': os.path.join(os.path.expanduser('~'), 'Downloads'),
                'documents': os.path.join(os.path.expanduser('~'), 'Documents'),
                'pictures': os.path.join(os.path.expanduser('~'), 'Pictures'),
                'videos': os.path.join(os.path.expanduser('~'), 'Videos'),
                'music': os.path.join(os.path.expanduser('~'), 'Music'),
            }
            
            # Check if path is exactly a common folder name (after stripping slashes)
            if path_lower in common_folders:
                path = common_folders[path_lower]
            # Check if path starts with a common folder name
            else:
                original_path_lower = path.lower()
                for folder_name, folder_path in common_folders.items():
                    if original_path_lower.startswith(folder_name + '\\') or original_path_lower.startswith(folder_name + '/'):
                        # Replace the folder name with the actual path
                        remaining_path = path[len(folder_name)+1:]
                        path = os.path.join(folder_path, remaining_path)
                        break
            
            # Expand user home directory (~)
            path = os.path.expanduser(path)
            
            # Expand environment variables
            path = os.path.expandvars(path)
            
            # Convert to absolute path
            abs_path = os.path.abspath(path)
            
            if must_exist and not os.path.exists(abs_path):
                print_error(f"Directory does not exist: {abs_path}")
                print_info(f"Tip: Try 'Desktop', 'Downloads', or '~\\Desktop'")
                print()
                continue
            
            if must_exist and not os.path.isdir(abs_path):
                print_error(f"Path is not a directory: {abs_path}")
                print()
                continue
            
            return abs_path
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:
            print_error(f"Input error: {str(e)}")
            print()


def get_number(prompt: str, min_val: int, max_val: int) -> int:
    """
    Get a validated number from the user.
    
    Args:
        prompt: The prompt message to display
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        The validated number
    """
    while True:
        try:
            print_prompt(f"{prompt} ({min_val}-{max_val}): ")
            value = input().strip()
            
            if not value:
                print_error("Please enter a number.")
                print()
                continue
            
            num = int(value)
            if min_val <= num <= max_val:
                return num
            else:
                print_error(f"Number must be between {min_val} and {max_val}.")
                print()
        except ValueError:
            print_error("Please enter a valid number.")
            print()
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:
            print_error(f"Input error: {str(e)}")
            print()


def interactive_split() -> None:
    """
    Interactive workflow for splitting a file into horcruxes.
    
    Guides the user through:
    1. Selecting the file to split
    2. Choosing total number of horcruxes
    3. Setting the threshold
    4. Specifying output directory
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ SPLIT FILE ═══{Style.RESET_ALL}\n")
    
    # Get file to split
    print_info("Select the file you want to split into horcruxes.")
    file_path = get_file_path("📄 Enter file path:")
    print_success(f"Selected: {file_path}")
    print()
    
    # Get total number of horcruxes
    print_info("How many horcruxes do you want to create?")
    print(f"{Fore.LIGHTBLACK_EX}   (Between 2 and 255 fragments){Style.RESET_ALL}")
    total = get_number("🔢 Total horcruxes", 2, 255)
    print()
    
    # Get threshold
    print_info("How many horcruxes are needed to reconstruct the file?")
    print(f"{Fore.LIGHTBLACK_EX}   (This creates redundancy - fewer needed = more backup safety){Style.RESET_ALL}")
    threshold = get_number(f"🔑 Threshold (minimum {2}, maximum {total})", 2, total)
    print()
    
    # Get output directory
    print_info("Where should the horcruxes be saved?")
    print(f"{Fore.LIGHTBLACK_EX}   (Press Enter for same directory as input file){Style.RESET_ALL}")
    
    while True:
        try:
            print_prompt("📁 Output directory (or press Enter): ")
            output_dir_input = input().strip().strip('"').strip("'")
            
            if not output_dir_input:
                output_dir = None
                print(f"{Fore.LIGHTBLACK_EX}   Using input file directory{Style.RESET_ALL}")
                break
            
            # Handle common folder shortcuts (case-insensitive)
            path_lower = output_dir_input.lower().rstrip('/\\')
            common_folders = {
                'desktop': os.path.join(os.path.expanduser('~'), 'Desktop'),
                'downloads': os.path.join(os.path.expanduser('~'), 'Downloads'),
                'documents': os.path.join(os.path.expanduser('~'), 'Documents'),
                'pictures': os.path.join(os.path.expanduser('~'), 'Pictures'),
                'videos': os.path.join(os.path.expanduser('~'), 'Videos'),
                'music': os.path.join(os.path.expanduser('~'), 'Music'),
            }
            
            # Check if path is exactly a common folder name (after stripping slashes)
            if path_lower in common_folders:
                output_dir_input = common_folders[path_lower]
            # Check if path starts with a common folder name
            else:
                original_path_lower = output_dir_input.lower()
                for folder_name, folder_path in common_folders.items():
                    if original_path_lower.startswith(folder_name + '\\') or original_path_lower.startswith(folder_name + '/'):
                        # Replace the folder name with the actual path
                        remaining_path = output_dir_input[len(folder_name)+1:]
                        output_dir_input = os.path.join(folder_path, remaining_path)
                        break
            
            # Expand user home directory and environment variables
            output_dir_input = os.path.expanduser(output_dir_input)
            output_dir_input = os.path.expandvars(output_dir_input)
            
            # Validate the output directory
            abs_output_dir = os.path.abspath(output_dir_input)
            
            # Check if parent directory exists (we can create the final dir if needed)
            parent_dir = os.path.dirname(abs_output_dir) if not os.path.dirname(abs_output_dir) == abs_output_dir else abs_output_dir
            
            if not os.path.exists(parent_dir):
                print_error(f"Parent directory does not exist: {parent_dir}")
                print()
                continue
            
            # Check if it's not an existing file
            if os.path.exists(abs_output_dir) and os.path.isfile(abs_output_dir):
                print_error(f"Path is a file, not a directory: {abs_output_dir}")
                print()
                continue
            
            output_dir = abs_output_dir
            break
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception as e:
            print_error(f"Input error: {str(e)}")
            print()
    
    print()
    
    # Confirm and execute
    print(f"{Fore.YELLOW}{Style.BRIGHT}═══ SUMMARY ═══{Style.RESET_ALL}")
    print(f"  File:       {Fore.WHITE}{file_path}{Style.RESET_ALL}")
    print(f"  Total:      {Fore.WHITE}{total} horcruxes{Style.RESET_ALL}")
    print(f"  Threshold:  {Fore.WHITE}{threshold} needed to reconstruct{Style.RESET_ALL}")
    print(f"  Output:     {Fore.WHITE}{output_dir or os.path.dirname(file_path)}{Style.RESET_ALL}")
    print()
    
    confirm = get_choice("🔒 Proceed with splitting? (yes/no):", ["yes", "no", "y", "n"])
    
    if confirm in ["no", "n"]:
        print_warning("Operation cancelled.")
        return
    
    print()
    print(f"{Fore.CYAN}Encrypting and splitting file...{Style.RESET_ALL}")
    
    try:
        split(file_path, total, threshold, output_dir)
        print()
        print_success("File successfully split into horcruxes!")
        print()
        
        # Show created files
        output_location = output_dir or os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        print(f"{Fore.GREEN}Created horcruxes:{Style.RESET_ALL}")
        for i in range(1, total + 1):
            horcrux_name = f"{base_name}_{i}_of_{total}.hrcx"
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {horcrux_name}")
        
    except Exception as e:
        print()
        print_error(f"Failed to split file: {str(e)}")


def interactive_bind() -> None:
    """
    Interactive workflow for binding horcruxes back into the original file.
    
    Guides the user through:
    1. Locating horcrux files (auto-discovery or manual selection)
    2. Specifying output file location
    3. Confirming reconstruction
    """
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ BIND HORCRUXES ═══{Style.RESET_ALL}\n")
    
    # Get horcrux directory
    print_info("Where are your horcrux files located?")
    directory = get_directory_path("📁 Enter directory path:", must_exist=True)
    print()
    
    # Try to find horcrux files
    print(f"{Fore.CYAN}Searching for horcrux files...{Style.RESET_ALL}")
    
    try:
        horcrux_files = find_horcrux_files(directory)
        
        if not horcrux_files:
            print_error(f"No horcrux files found in: {directory}")
            print_info("Horcrux files should have the .hrcx extension")
            return
        
        print_success(f"Found {len(horcrux_files)} horcrux file(s)")
        print()
        
        # Show found files
        print(f"{Fore.CYAN}Found horcruxes:{Style.RESET_ALL}")
        for hf in horcrux_files:
            print(f"  {Fore.CYAN}•{Style.RESET_ALL} {os.path.basename(hf)}")
        print()
        
        # Get first horcrux to check metadata
        from hrcx.horcrux.format import read_horcrux
        header, _ = read_horcrux(horcrux_files[0])
        
        print(f"{Fore.YELLOW}{Style.BRIGHT}═══ HORCRUX INFO ═══{Style.RESET_ALL}")
        print(f"  Original file:  {Fore.WHITE}{header.original_filename}{Style.RESET_ALL}")
        print(f"  Threshold:      {Fore.WHITE}{header.threshold} horcruxes needed{Style.RESET_ALL}")
        print(f"  Total:          {Fore.WHITE}{header.total} horcruxes total{Style.RESET_ALL}")
        print(f"  Available:      {Fore.WHITE}{len(horcrux_files)} horcruxes found{Style.RESET_ALL}")
        print()
        
        # Check if we have enough
        if len(horcrux_files) < header.threshold:
            print_error(f"Not enough horcruxes! Need {header.threshold}, found {len(horcrux_files)}")
            return
        
        print_success(f"Threshold met! ({len(horcrux_files)} >= {header.threshold})")
        print()
        
        # Get output path
        print_info("Where should the reconstructed file be saved?")
        print(f"{Fore.LIGHTBLACK_EX}   (Press Enter to use: {header.original_filename}){Style.RESET_ALL}")
        
        while True:
            try:
                print_prompt("💾 Output file path (or press Enter): ")
                output_path = input().strip().strip('"').strip("'")
                
                if not output_path:
                    output_path = os.path.join(directory, header.original_filename)
                    print(f"{Fore.LIGHTBLACK_EX}   Using: {output_path}{Style.RESET_ALL}")
                    break
                
                # Handle common folder shortcuts (case-insensitive)
                output_path_lower = output_path.lower().rstrip('/\\')  # Remove trailing slashes
                common_folders = {
                    'desktop': os.path.join(os.path.expanduser('~'), 'Desktop'),
                    'downloads': os.path.join(os.path.expanduser('~'), 'Downloads'),
                    'documents': os.path.join(os.path.expanduser('~'), 'Documents'),
                    'pictures': os.path.join(os.path.expanduser('~'), 'Pictures'),
                    'videos': os.path.join(os.path.expanduser('~'), 'Videos'),
                    'music': os.path.join(os.path.expanduser('~'), 'Music'),
                }
                
                # Check if path is exactly a common folder name (after stripping slashes)
                if output_path_lower in common_folders:
                    # User just typed the folder name - append the original filename
                    output_path = os.path.join(common_folders[output_path_lower], header.original_filename)
                # Check if path starts with a common folder name
                else:
                    original_path_lower = output_path.lower()
                    for folder_name, folder_path in common_folders.items():
                        if original_path_lower.startswith(folder_name + '\\') or original_path_lower.startswith(folder_name + '/'):
                            # Replace the folder name with the actual path
                            remaining_path = output_path[len(folder_name)+1:]
                            output_path = os.path.join(folder_path, remaining_path)
                            break
                
                # Expand user home directory (~)
                output_path = os.path.expanduser(output_path)
                
                # Expand environment variables
                output_path = os.path.expandvars(output_path)
                
                # Validate output path
                output_path = os.path.abspath(output_path)
                
                # Check if parent directory exists
                parent_dir = os.path.dirname(output_path)
                if parent_dir and not os.path.exists(parent_dir):
                    print_error(f"Parent directory does not exist: {parent_dir}")
                    print()
                    continue
                
                # Check if it's not an existing directory
                if os.path.exists(output_path) and os.path.isdir(output_path):
                    print_error(f"Path is a directory, not a file: {output_path}")
                    print()
                    continue
                
                break
            except (EOFError, KeyboardInterrupt):
                raise
            except Exception as e:
                print_error(f"Input error: {str(e)}")
                print()
        
        print()
        
        # Check if file exists
        overwrite = False
        if os.path.exists(output_path):
            print_warning(f"File already exists: {output_path}")
            confirm = get_choice("⚠  Overwrite? (yes/no):", ["yes", "no", "y", "n"])
            if confirm in ["no", "n"]:
                print_warning("Operation cancelled.")
                return
            overwrite = True
            print()
        
        # Confirm and execute
        print(f"{Fore.YELLOW}{Style.BRIGHT}═══ SUMMARY ═══{Style.RESET_ALL}")
        print(f"  Horcruxes:  {Fore.WHITE}{len(horcrux_files)} files{Style.RESET_ALL}")
        print(f"  Output:     {Fore.WHITE}{output_path}{Style.RESET_ALL}")
        print()
        
        confirm = get_choice("🔓 Proceed with reconstruction? (yes/no):", ["yes", "no", "y", "n"])
        
        if confirm in ["no", "n"]:
            print_warning("Operation cancelled.")
            return
        
        print()
        print(f"{Fore.CYAN}Reconstructing file from horcruxes...{Style.RESET_ALL}")
        
        bind(horcrux_files, output_path, overwrite)
        print()
        print_success(f"File successfully reconstructed: {output_path}")
        
    except Exception as e:
        print()
        print_error(f"Failed to bind horcruxes: {str(e)}")


def main() -> None:
    """
    Main entry point for the interactive CLI.
    
    Displays the header and main menu, then routes to the appropriate workflow
    based on user selection.
    """
    try:
        print_header()
        
        # Main menu
        print(f"{Fore.CYAN}{Style.BRIGHT}═══ MAIN MENU ═══{Style.RESET_ALL}\n")
        print(f"  {Fore.GREEN}[1] SPLIT{Style.RESET_ALL}  - Encrypt and split a file into horcruxes")
        print(f"  {Fore.BLUE}[2] BIND{Style.RESET_ALL}   - Reconstruct a file from horcruxes")
        print(f"  {Fore.RED}[3] EXIT{Style.RESET_ALL}   - Quit the program")
        print()
        
        choice = get_choice("➤ Choose an option (1/2/3):", ["1", "2", "3"])
        
        if choice == "1":
            interactive_split()
        elif choice == "2":
            interactive_bind()
        elif choice == "3":
            print()
            print_info("Thank you for using Horcrux!")
            return
        
        # Ask if user wants to continue
        print()
        print()
        continue_choice = get_choice("🔄 Perform another operation? (yes/no):", ["yes", "no", "y", "n"])
        
        if continue_choice in ["yes", "y"]:
            main()  # Recursive call to restart
        else:
            print()
            print_info("Thank you for using Horcrux!")
    
    except KeyboardInterrupt:
        print()
        print()
        print_warning("Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
