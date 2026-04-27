#!/usr/bin/env python3
from pathlib import Path

from rich.console import Console

import minerva_verify.modules.database as database
import minerva_verify.modules.explore as explore
import minerva_verify.modules.verifying as verifying

console = Console()

BASE_DIR = Path(__file__).resolve().parent
DAT_FOLDER = BASE_DIR.parent / "dat" / Path(__file__).stem

def main(root_path):
    for console_folder in explore.get_surface_folders(root_path):
        folder_path = Path(root_path) / console_folder
        
        verifying.process_console_folder(
            folder_path, 
            DAT_FOLDER, 
            console_folder + ".dat",
            database.RA_SCHEMA, 
            Path(__file__).stem
        )
        
if __name__ == "__main__":
    # Replace 'path/to/roms' with your actual directory or sys.argv[1]
    main('./roms')