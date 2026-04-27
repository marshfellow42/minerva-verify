#!/usr/bin/env python3
from pathlib import Path

from rich.console import Console

import minerva_verify.modules.database as database
import minerva_verify.modules.explore as explore
import minerva_verify.modules.verifying as verifying

console = Console()

BASE_DIR = Path(__file__).resolve().parent
DAT_FOLDER = BASE_DIR.parent / "dat" / "Touhou Project Collection"

def main(root_path):
    for console_folder in explore.get_surface_folders(root_path):
        folder_path = Path(root_path) / console_folder

        files_present = len(explore.get_surface_files(folder_path))
        
        if files_present == 0:
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
                
                verifying.process_console_folder(
                    subfolder_path, 
                    DAT_FOLDER, 
                    actual_dat_file[0],
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
            
            verifying.process_console_folder(
                folder_path, 
                DAT_FOLDER, 
                actual_dat_file[0],
                database.RA_SCHEMA, 
                "Touhou Project Collection"
            )
            
        
if __name__ == "__main__":
    # Replace 'path/to/roms' with your actual directory or sys.argv[1]
    main('./roms')