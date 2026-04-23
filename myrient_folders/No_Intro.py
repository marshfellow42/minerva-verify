#!/usr/bin/env python3
from pathlib import Path

from rich.console import Console

import modules.database as database
import modules.explore as explore

# Custom modules
import modules.verifying as verifying

console = Console()

def main(root_path):
    if "ps3" in str(root_path).lower():
        console.print(f"[yellow]Skipping:[/yellow] ps3 detected in path '{root_path}'")
        return
    
    DAT_FOLDER = Path('.') / "dat" / Path(__file__).stem.replace("_", "-")
    
    cache_path = explore.get_cache_path()
    
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
            cache_path, 
            database.RA_SCHEMA, 
            Path(__file__).stem.replace("_", "-")
        )
        
if __name__ == "__main__":
    # Replace 'path/to/roms' with your actual directory or sys.argv[1]
    main('./roms')