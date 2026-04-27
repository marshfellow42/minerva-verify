from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR.parent / "minerva.db"

print(db_path)