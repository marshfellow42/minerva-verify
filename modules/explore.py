#!/usr/bin/env python3
from pathlib import Path
import mimetypes
import tomllib
from platformdirs import user_cache_path

def get_cache_path():
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    
    path = user_cache_path(
        appname=data["project"]["name"], 
        appauthor=data["project"]["authors"][0]["name"]
    )
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_surface_folders(directory_path):
    path = Path(directory_path)
    return [item.name for item in path.iterdir() if item.is_dir()]

def get_all_files(directory_path):
    path = Path(directory_path)
    return [str(item.relative_to(path)) for item in path.rglob("*") if item.is_file()]

def check_extension(filepath):
    mime_type, encoding = mimetypes.guess_type(filepath)
    return mime_type

def autocomplete(partial, folder="."):
    p = Path(folder)
    partial_lower = partial.lower()

    return [
        f.name
        for f in p.iterdir()
        if f.is_file() and f.name.lower().startswith(partial_lower)
    ]