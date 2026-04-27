from pathlib import Path

file_path = Path("C:/Users/darkm/OneDrive/Documentos/Roms/touhou/Minerva_Myrient/Touhou Project Collection/Official Content/Games/[TH6] Koumakyou ~ The Embodiment of Scarlet Devil/English/log.txt")
size_in_bytes = file_path.stat().st_size

print(size_in_bytes)