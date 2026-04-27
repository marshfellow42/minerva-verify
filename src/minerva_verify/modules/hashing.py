#!/usr/bin/env python3
from pathlib import Path
import subprocess
import re
import hashlib
import shutil
import zlib
import platform

def get_file_crc32(filename):
    crc = 0
    with open(filename, 'rb') as f:
        # Read in 64KB chunks
        for chunk in iter(lambda: f.read(65536), b''):
            crc = zlib.crc32(chunk, crc)
    # Return as an 8-character hex string
    return format(crc & 0xFFFFFFFF, '08X').lower()

CHD_FOLDERS = [
    "RA - Sony Playstation",
    "RA - Sony Playstation 2",
    "RA - Sega Dreamcast",
    "RA - Sega CD"
]


def get_chdman_path():
    system = platform.system()

    match system:
        case "Linux":
            system = shutil.which("chdman")
            if system:
                return system

        case "Darwin":
            system = shutil.which("chdman")
            if system:
                return system

        case "Windows":
            base_dir = Path(__file__).resolve().parent
            local = base_dir.parent / "tools" / "chdman.exe"

            # Windows + local bundled version
            if local.exists():
                return str(local)

        case _:
            raise RuntimeError("chdman not found (local or system PATH)")


def get_chd_sha1_with_chdman(path: Path):
    chdman = get_chdman_path()

    result = subprocess.run(
        [chdman, "info", "-i", str(path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    match = re.search(r"SHA1:\s*([a-fA-F0-9]+)", result.stdout)
    return match.group(1) if match else None


def should_use_chdman(path: Path):
    path = Path(path)

    return (
        path.suffix.lower() == ".chd"
        and any(folder in path.as_posix() for folder in CHD_FOLDERS)
    )


def get_sha1(file_path):
    path = Path(file_path)

    if should_use_chdman(path):
        return get_chd_sha1_with_chdman(path)

    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()

def get_md5(file_path):
    with open(file_path, "rb") as f:
        digest = hashlib.file_digest(f, "md5")
        return digest.hexdigest()
    
def get_sha256(file_path):
    with open(file_path, "rb") as f:
        digest = hashlib.file_digest(f, "sha256")
        return digest.hexdigest()