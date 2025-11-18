"""
Command-line interface for Horcrux.

This module provides the CLI commands using Click.
"""

import sys

import click

from . import api
from .horcrux import find_horcrux_files
from .interactive import main as interactive_main


@click.group()
@click.version_option(version="1.0.0", prog_name="hrcx")
def main() -> None:
    """
    Horcrux - Split your files into encrypted fragments.
    
    Split files using Shamir's Secret Sharing Scheme and AES-256-GCM encryption.
    """
    pass


@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("-t", "--total", type=int, help="Total number of horcruxes to create")
@click.option("-k", "--threshold", type=int, help="Minimum horcruxes needed to reconstruct")
@click.option("-o", "--output", type=click.Path(), help="Output directory for horcruxes")
def split(file: str, total: int | None, threshold: int | None, output: str | None) -> None:
    """
    Split a file into encrypted horcruxes.
    
    Example:
        hrcx split secret.txt -t 5 -k 3
    """
    # Interactive prompts if options not provided
    if total is None:
        while True:
            try:
                total_input = click.prompt(
                    "How many horcruxes do you want to split this file into? (2-255)",
                    type=int
                )
                if 2 <= total_input <= 255:
                    total = total_input
                    break
                else:
                    click.echo("❌ Total must be between 2 and 255")
            except (ValueError, click.Abort):
                click.echo("\n❌ Operation cancelled")
                sys.exit(1)
    
    if threshold is None:
        while True:
            try:
                threshold_input = click.prompt(
                    f"How many horcruxes should be required to reconstruct the file? (2-{total})",
                    type=int
                )
                if 2 <= threshold_input <= total:
                    threshold = threshold_input
                    break
                else:
                    click.echo(f"❌ Threshold must be between 2 and {total}")
            except (ValueError, click.Abort):
                click.echo("\n❌ Operation cancelled")
                sys.exit(1)
    
    try:
        click.echo(f"\n🔒 Splitting {file}...")
        api.split(file, total=total, threshold=threshold, output_dir=output)
        click.echo(f"✅ Successfully created {total} horcruxes (threshold: {threshold})")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("directory", type=click.Path(exists=True), required=False, default=".")
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option("-f", "--force", is_flag=True, help="Overwrite existing file without prompting")
def bind(directory: str, output: str | None, force: bool) -> None:
    """
    Reconstruct the original file from horcruxes.
    
    Example:
        hrcx bind ./vault
        hrcx bind  (uses current directory)
    """
    try:
        # Find all horcrux files in directory
        click.echo(f"🔍 Looking for horcruxes in {directory}...")
        horcrux_files = find_horcrux_files(directory)
        
        if not horcrux_files:
            click.echo(f"❌ No .hrcx files found in {directory}", err=True)
            sys.exit(1)
        
        click.echo(f"Found {len(horcrux_files)} horcrux file(s)")
        
        # Bind the horcruxes
        click.echo("\n🔓 Reconstructing file...")
        api.bind(horcrux_files, output_path=output, overwrite=force)
        click.echo("✅ Successfully reconstructed file!")
        
    except FileExistsError as e:
        click.echo(f"❌ {e}", err=True)
        click.echo("Use -f/--force to overwrite", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
def interactive() -> None:
    """
    Launch interactive mode with a user-friendly GUI-like interface.
    
    Perfect for non-technical users who prefer a step-by-step wizard.
    Features beautiful ASCII art, color-coded prompts, and helpful guidance.
    """
    interactive_main()


if __name__ == "__main__":
    main()
