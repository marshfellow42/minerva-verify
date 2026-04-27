#!/usr/bin/env python3
import tomllib
from pathlib import Path
from platformdirs import user_config_dir
import platform
import sys

with open("pyproject.toml", "rb") as f:
    project_data = tomllib.load(f)
    
system = platform.system()

match system:
    case "Linux":
        # XDG_CONFIG_ENV
        pass

    case "Darwin":
        sys_cmd = ["brew", "update", "&&", "brew", "upgrade"]

    case "Windows":
        appdata_path = Path(user_config_dir(appname=project_data["project"]["name"], appauthor=False, roaming=True))
        appdata_path.mkdir(parents=True, exist_ok=True)
        
        # config file in appdata/roaming/minerva-verify

        config_path = appdata_path / "config.toml"

    case _:
        print(f"Operating system '{system}' is not supported.")
        sys.exit(1)

with open(config_path, "rb") as f:
    data = tomllib.load(f)

roms_config = data.get("ROMS_FOLDER")

ROMS_FOLDER = Path(roms_config) if roms_config else Path.home() / "Roms"