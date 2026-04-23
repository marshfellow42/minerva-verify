#!/usr/bin/env python3
from pathlib import Path

from rich.console import Console

import modules.database as database
import modules.explore as explore

# Custom modules
import modules.verifying as verifying

console = Console()

def main(root_path):
    DAT_FOLDER = Path('.') / "dat" / "Touhou Project Collection"
    
    cache_path = explore.get_cache_path()
    
    for console_folder in explore.get_surface_folders(root_path):
        folder_path = Path(root_path) / console_folder
        
        print(folder_path)

        
        if folder_path.is_dir():
            for subfolder in explore.get_surface_folders(folder_path):
                subfolder_path = folder_path / subfolder
                
                try:
                    actual_dat_file = explore.autocomplete(
                        f"{folder_path.stem} - {subfolder_path.stem}",
                        folder=DAT_FOLDER
                    )
                except StopIteration:
                    console.print(f"[red]Error:[/red] No DAT file found starting with {console_folder}")
                    continue
                
                print(f"DAT Folder: {DAT_FOLDER}")
                print(f"DAT File: {actual_dat_file}")
                
                verifying.process_console_folder(
                    subfolder_path, 
                    DAT_FOLDER, 
                    actual_dat_file[0], 
                    cache_path, 
                    database.RA_SCHEMA, 
                    "Touhou Project Collection"
                )
        else:
            try:
                actual_dat_file = explore.autocomplete(
                    folder_path.stem,
                    folder=DAT_FOLDER
                )
            except StopIteration:
                console.print(f"[red]Error:[/red] No DAT file found starting with {console_folder}")
                continue
            
            print(f"DAT Folder: {DAT_FOLDER}")
            print(f"DAT File: {actual_dat_file}")
            
            verifying.process_console_folder(
                folder_path, 
                DAT_FOLDER, 
                actual_dat_file[0], 
                cache_path, 
                database.RA_SCHEMA, 
                "Touhou Project Collection"
            )
            
        
if __name__ == "__main__":
    # Replace 'path/to/roms' with your actual directory or sys.argv[1]
    main('./roms')