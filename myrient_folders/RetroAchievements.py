#!/usr/bin/env python3
from pathlib import Path

from rich.console import Console

import modules.database as database
import modules.explore as explore

# Custom modules
import modules.verifying as verifying

console = Console()

DAT_FOLDER = Path('.') / "dat" / Path(__file__).stem

def main(root_path):
    cache_path = explore.get_cache_path()
    
    for console_folder in explore.get_surface_folders(root_path):
        folder_path = Path(root_path) / console_folder
        
        verifying.process_console_folder(
            folder_path, 
            DAT_FOLDER, 
            console_folder + ".dat", 
            cache_path, 
            database.RA_SCHEMA, 
            Path(__file__).stem
        )
        
if __name__ == "__main__":
    # Replace 'path/to/roms' with your actual directory or sys.argv[1]
    main('./roms')