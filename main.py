#!/usr/bin/env python3
from rich.console import Console
import modules.explore as explore
import tomllib
import typer
from myrient_folders import (
    RetroAchievements,
    Redump,
    No_Intro,
    TouhouProjectCollection
)
import settings
import sys

console = Console()

try:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
except FileNotFoundError:
    console.print("[bold red]Error:[/bold red] pyproject.toml not found.")
    sys.exit(1)

app = typer.Typer(
    name=data["project"]["name"]
)

ROMS_FOLDER = settings.ROMS_FOLDER

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    
    all_minerva_folders = list(ROMS_FOLDER.rglob("Minerva_Myrient"))
    
    if not all_minerva_folders:
        console.print("[yellow]No 'Minerva_Myrient' folders found.[/yellow]")
        return
    
    for minerva_path in all_minerva_folders:
        if not minerva_path.is_dir():
            continue
        
        try:
            # Check the immediate subfolders inside this specific Minerva_Myrient instance
            sub_folders = explore.get_surface_folders(minerva_path)
            
            for folder_name in sub_folders:
                folder_full_path = minerva_path / folder_name
                
                match folder_name:
                    case "RetroAchievements":
                        RetroAchievements.main(folder_full_path)
                    case "Redump":
                        Redump.main(folder_full_path)
                    case "No-Intro":
                        No_Intro.main(folder_full_path)
                    case "Touhou Project Collection":
                        TouhouProjectCollection.main(folder_full_path)
            
        except Exception as e:
            console.print(f"[bold red]Failed to process {minerva_path}:[/bold red] {e}")
                        
        # Insert a text here to see how many were successful and unsuccessful
        # Like: 100 Passed, 32 Failed


if __name__ == "__main__":
    app()