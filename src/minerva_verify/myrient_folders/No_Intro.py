#!/usr/bin/env python3
from pathlib import Path

from rich.console import Console

import minerva_verify.modules.database as database
import minerva_verify.modules.explore as explore
import minerva_verify.modules.verifying as verifying

console = Console()

BASE_DIR = Path(__file__).resolve().parent
DAT_FOLDER = BASE_DIR.parent / "dat" / Path(__file__).stem.replace("_", "-")

def main(root_path, project_name, author_name):
    if "ps3" in str(root_path).lower():
        console.print(f"[yellow]Skipping:[/yellow] ps3 detected in path '{root_path}'")
        return
    
    for console_folder in explore.get_surface_folders(root_path):
        folder_path = Path(root_path) / console_folder
        
        try:
            actual_dat_file = explore.autocomplete(
                console_folder,
                folder=DAT_FOLDER
            )
        except StopIteration:
            console.print(f"[red]Error:[/red] No DAT file found starting with {console_folder}")
            continue
        
        verifying.process_console_folder(
            folder_path, 
            DAT_FOLDER, 
            actual_dat_file[0],
            database.RA_SCHEMA, 
            Path(__file__).stem.replace("_", "-"),
            project_name,
            author_name
        )
        
if __name__ == "__main__":
    # Replace 'path/to/roms' with your actual directory or sys.argv[1]
    main('./roms')