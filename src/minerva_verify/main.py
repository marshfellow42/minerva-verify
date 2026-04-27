#!/usr/bin/env python3
from rich.console import Console
import minerva_verify.modules.explore as explore
import tomllib
import typer
from minerva_verify.myrient_folders import (
    RetroAchievements,
    Redump,
    No_Intro,
    TouhouProjectCollection
)
import minerva_verify.settings as settings
import sys
import subprocess
import platform
import shutil
from pathlib import Path

console = Console()

try:
    ROOT = Path(__file__).resolve().parents[2]
    with open(ROOT / "pyproject.toml", "rb") as f:
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
        
@app.command(help="Update the system and the app.")
def update():
    def is_repo_up_to_date():
        try:
            # Update the local cache of the remote repo
            subprocess.run(["git", "fetch"], check=True, capture_output=True)
            
            # Compare local HEAD to the upstream branch
            # rev-list --count HEAD..@{u} counts commits that exist on remote but not locally
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..@{u}"],
                check=True,
                capture_output=True,
                text=True
            )
            
            # If count is '0', we are up to date
            return int(result.stdout.strip()) == 0
        except Exception:
            # If git isn't initialized or there's no upstream, assume we proceed
            return False
    
    system = platform.system()

    match system:
        case "Linux":
            distro = platform.freedesktop_os_release().get("ID", "").lower()
            
            match distro:
                case "ubuntu" | "debian":
                    subprocess.run(["sudo", "apt", "update"], check=False)
                    subprocess.run(["sudo", "apt", "upgrade", "-y"], check=False)
                case "arch":
                    if shutil.which("yay"):
                        sys_cmd = ["yay", "-Syu", "--noconfirm"]
                    else:
                        sys_cmd = ["sudo", "pacman", "-Syu", "--noconfirm"]
                case "fedora":
                    sys_cmd = ["sudo", "dnf", "upgrade", "--refresh"]
                case _:
                    print(f"Linux distribution '{distro}' is not supported.")
                    return

        case "Darwin":
            subprocess.run(["brew", "update"], check=False)
            subprocess.run(["brew", "upgrade"], check=False)

        case "Windows":
            print("Windows is not supported.")
            sys.exit(1)

        case _:
            print(f"Operating system '{system}' is not supported.")
            sys.exit(1)
            
    subprocess.run(sys_cmd, check=False, capture_output=True, text=True)
    
    if is_repo_up_to_date():
        console.print("[yellow]No git updates found. Skipping update.[/yellow]")
        return
    else:
        subprocess.run(["git", "pull"], check=False, capture_output=True, text=True)

        subprocess.run(["uv", "tool", "install", ".", "--force"], check=False, capture_output=True, text=True)

@app.command(help="Show the version number for the app.")
def version():
    print(data["project"]["version"])

if __name__ == "__main__":
    app()