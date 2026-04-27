import hashlib
import os

def get_sha1(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found. Check your path."

    with open(file_path, "rb") as f:
        # file_digest is optimized for file-like objects
        digest = hashlib.file_digest(f, "sha1")
        return digest.hexdigest()

# Pro-tip: Use a raw string (r"path") for Windows paths
path = r"C:/Users/darkm/OneDrive/Documentos/Roms/ps2/Minerva_Myrient/RetroAchievements/RA - Sony Playstation 2/Dragon Ball Z - Budokai Tenkaichi 3 (USA) (En,Ja).chd"

print(f"SHA-1: {get_sha1(path)}")