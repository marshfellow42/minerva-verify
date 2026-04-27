from pathlib import Path

def autocomplete(partial, folder="."):
    p = Path(folder)
    partial_lower = partial.lower()

    return [
        f.name
        for f in p.iterdir()
        if f.is_file() and f.name.lower().startswith(partial_lower)
    ]

matches = autocomplete(
    "Nintendo - Wii - NKit RVZ [zstd-19-128k]",
    folder=r"C:/Users/darkm/OneDrive/Documentos/Coding/minerva-verify/dat/Redump"
)

print(matches)