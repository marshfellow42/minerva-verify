import struct

def read_chd_sha1(path):
    with open(path, "rb") as f:
        header = f.read(200)  # read enough

    if not header.startswith(b'MComprHD'):
        raise ValueError("Not a CHD file")

    # Version is big-endian uint32 at offset 12 (not 8)
    version = struct.unpack(">I", header[12:16])[0]

    if version != 5:
        raise NotImplementedError(f"CHD version {version} not supported")

    # SHA1 offsets for v5 (corrected)
    raw_sha1 = header[96:116]
    data_sha1 = header[116:136]

    return {
        "raw_sha1": raw_sha1.hex(),
        "data_sha1": data_sha1.hex()
    }

print(read_chd_sha1("C:/Users/darkm/OneDrive/Documentos/Roms/psx/Minerva_Myrient/RetroAchievements/RA - Sony Playstation/Tomb Raider (USA).chd"))