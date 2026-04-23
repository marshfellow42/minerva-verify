#!/usr/bin/env python3
import sqlite3
from pathlib import Path

def get_db_connection(db_name="minerva.db"):
    """Handles database connection and pathing."""
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir.parent / db_name
    return sqlite3.connect(db_path)

def create_table(cursor, table_name, schema):
    columns_sql = ", ".join([f'"{name}" {dtype}' for name, dtype in schema])
    query = f'CREATE TABLE IF NOT EXISTS "{table_name}" (id INTEGER PRIMARY KEY, {columns_sql})'
    cursor.execute(query)

def upsert_data(cursor, table_name, schema, data_tuple, conflict_col="dat_sha1_hash"):
    cols = [item[0] for item in schema]
    
    # Wrap column names in double quotes for safety
    quoted_cols = [f'"{c}"' for c in cols]
    col_names = ", ".join(quoted_cols)
    placeholders = ", ".join(["?"] * len(cols))
    
    # Wrap column names in the SET part
    update_set = ", ".join([f'"{c}"=excluded."{c}"' for c in cols if c != conflict_col])
    
    # Wrap column names in the WHERE part
    check_cols = [c for c in cols if c.endswith("_check")]
    update_where = " OR ".join([f'"{c}" = 0' for c in check_cols])
    
    # Construct the final query with quoted table name and conflict column
    sql = f"""
        INSERT INTO "{table_name}" ({col_names}) 
        VALUES ({placeholders})
        ON CONFLICT("{conflict_col}") DO UPDATE SET {update_set}
        WHERE {update_where}
    """
    cursor.execute(sql, data_tuple)
    
# --- Usage Example ---

RA_SCHEMA = [
    ("game_name", "TEXT"),
    ("rom_name", "TEXT"),
    ("rom_system", "TEXT"),
    ("dat_game_size", "TEXT"),
    ("dat_crc_hash", "TEXT"),
    ("dat_sha1_hash", "TEXT UNIQUE"),
    ("dat_md5_hash", "TEXT"),
    ("game_actual_size", "TEXT"),
    ("game_crc_hash", "TEXT"),
    ("game_sha1_hash", "TEXT"),
    ("game_md5_hash", "TEXT"),
    ("game_size_check", "INTEGER"),
    ("crc_check", "INTEGER"),
    ("sha1_check", "INTEGER"),
    ("md5_check", "INTEGER"),
    ("timestamp", "TEXT")
]

def main(collection_name, data):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        create_table(cursor, collection_name, RA_SCHEMA)
        upsert_data(cursor, collection_name, RA_SCHEMA, data)
        
        conn.commit()

if __name__ == "__main__":
    main()