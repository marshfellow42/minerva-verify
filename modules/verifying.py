#!/usr/bin/env python3
import zipfile
from pathlib import Path
from datetime import datetime, timezone
from lxml import etree
import pandas as pd
from rich.console import Console

# Custom modules
import modules.hashing as hashing
import modules.explore as explore
import modules.database as database

console = Console()

def parse_dat_file(dat_path):
    """
    Parses DAT file, auto-detecting if it uses //game or //machine tags.
    Returns the system name and a DataFrame of ROM data.
    """
    tree = etree.parse(str(dat_path))
    
    # 1. Get Header Info
    header = tree.xpath('//header')
    system_name = header[0].findtext('description') if header else "Unknown System"

    # 2. Auto-Detect Entry Tag
    # We check for //game first, then //machine
    entries = tree.xpath('//game')
    if not entries:
        entries = tree.xpath('//machine')
        if not entries:
            console.print(f"[yellow]Warning:[/yellow] No <game> or <machine> tags found in {dat_path.name}")
            return system_name, pd.DataFrame()

    raw_data = []
    for g in entries:
        file_nodes = g.xpath('.//rom | .//disk')
        release_node = g.find('release')
        
        for rom_node in file_nodes:
            raw_data.append({
                'game': g.get('name'),
                'rom_name': rom_node.get('name'),
                'rom_size': rom_node.get('size'),
                'rom_crc_hash': rom_node.get('crc'),
                'rom_md5_hash': rom_node.get('md5'),
                'rom_sha1_hash': rom_node.get('sha1'),
                'rom_sha256_hash': rom_node.get('sha256'),
                'region': release_node.get('region') if release_node is not None else None,
            })
    
    return system_name, pd.DataFrame(raw_data)

def extract_and_verify(zip_path, cache_path, df_dat, system_name, database_schema, database_table_name):
    """Extracts all files (including those in subdirs) from a zip and verifies them."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if zip_ref.testzip() is not None:
                console.print(f"[red]Corrupt ZIP detected:[/red] {zip_path.name}")
                return

            # Get list of all file entries (skipping directory-only entries)
            file_list = [f for f in zip_ref.infolist() if not f.is_dir()]
            
            zip_stem = zip_path.stem
            
            console.print(f"[bold yellow][FILE][/bold yellow] {zip_path.stem}")

            for file_info in file_list:
                # 1. Extract the file
                # zip_ref.extract handles creating subfolders inside cache_path automatically
                zip_ref.extract(file_info, path=cache_path)
                extracted_path = cache_path / file_info.filename

                # 2. Determine the "ROM name" for DAT lookup
                # Usually, DATs match the filename only, not the internal ZIP path.
                # If your DAT includes paths, use file_info.filename. 
                # If it's just the filename, use Path(file_info.filename).name
                internal_name = file_info.filename

                # 3. Verify
                verify_file(
                    df_dat, 
                    system_name, 
                    internal_name, 
                    extracted_path, 
                    database_schema, 
                    database_table_name,
                    zip_stem=zip_stem
                )
                
                # 4. Cleanup the file
                extracted_path.unlink(missing_ok=True)
                
                # 5. Cleanup empty parent directories in cache to keep it tidy
                for parent in extracted_path.parents:
                    if parent == cache_path:
                        break
                    try:
                        parent.rmdir()  # Only deletes if the directory is empty
                    except OSError:
                        break 

    except Exception as e:
        console.print(f"[red]Error processing {zip_path.name}: {e}[/red]")

def verify_file(df_dat, system_name, game_internal_name, file_path, database_schema, database_table_name, zip_stem=None):
    """
    Verifies a file. Missing DAT hashes result in NULL (None) in the database.
    """
                
    # 1. Lookup in DAT
    if zip_stem:
        # Filter where ROM name matches AND the parent Game/Machine name matches the ZIP name
        dat_row = df_dat[(df_dat['rom_name'] == game_internal_name) & 
                        (df_dat['game'] == zip_stem)]
    else:
        # Fallback for loose files not inside a zip
        dat_row = df_dat[df_dat['rom_name'] == game_internal_name]

    if dat_row.empty:
        console.print(f"[yellow]File {game_internal_name} (Set: {zip_stem}) not found in DAT.[/yellow]")
        return

    expected = dat_row.iloc[0]
    
    check_map = {
        'rom_size': (lambda p: str(p.stat().st_size), 'size_check'),
        'rom_crc_hash': (lambda p: hashing.get_file_crc32(p), 'crc_check'),
        'rom_md5_hash': (lambda p: hashing.get_md5(p), 'md5_check'),
        'rom_sha1_hash': (lambda p: hashing.get_sha1(p), 'sha1_check'),
        'rom_sha256_hash': (lambda p: hashing.get_sha256(p), 'sha256_check')
    }

    actual_values = {}
    # Initialize checks as None (will become NULL in SQL)
    checks = {'size_check': None, 'crc_check': None, 'sha1_check': None, 'md5_check': None, 'sha256_check': None}
    verification_results = []

    # 2. Dynamic Verification
    for dat_key, (hash_func, check_key) in check_map.items():
        expected_val = expected.get(dat_key)
        
        if expected_val and pd.notna(expected_val):
            actual_val = hash_func(file_path)
            actual_values[dat_key] = actual_val
            
            # Perform comparison
            passed = 1 if str(actual_val).lower() == str(expected_val).lower() else 0
            checks[check_key] = passed
            verification_results.append(passed)
        else:
            # Not in DAT? Keep it None/NULL
            actual_values[dat_key] = None

    # 3. Overall Status Determination
    # If no hashes were provided, it's technically a "Success" by default (nothing failed)
    is_valid = all(verification_results) if verification_results else True
    status_text = "[green]Success[/green]" if is_valid else "[red]Failed[/red]"

    # 4. Map values for Database
    value_map = {
        "game_name": expected.get('game'),
        "rom_name": game_internal_name,
        "rom_system": system_name,
        "dat_game_size": expected.get('rom_size'),
        "dat_crc_hash": expected.get('rom_crc_hash'),
        "dat_md5_hash": expected.get('rom_md5_hash'),
        "dat_sha1_hash": expected.get('rom_sha1_hash'),
        "dat_sha256_hash": expected.get('rom_sha256_hash'),
        "game_actual_size": actual_values.get('rom_size'),
        "game_crc_hash": actual_values.get('rom_crc_hash'),
        "game_md5_hash": actual_values.get('rom_md5_hash'),
        "game_sha1_hash": actual_values.get('rom_sha1_hash'),
        "game_sha256_hash": actual_values.get('rom_sha256_hash'),
        "game_size_check": checks['size_check'],
        "crc_check": checks['crc_check'],
        "md5_check": checks['md5_check'],
        "sha1_check": checks['sha1_check'],
        "sha256_check": checks['sha256_check'],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    data_tuple = tuple(value_map.get(col[0]) for col in database_schema)
    database.main(database_table_name, data_tuple)
    
    console.print(f"[{status_text}] {game_internal_name}")

def process_console_folder(folder_path, dat_folder, dat_filename, cache_path, database_schema, database_table_name):
    """High-level orchestration for a specific console folder."""
    dat_path = dat_folder / dat_filename
    if not dat_path.exists():
        console.print(f"[red]DAT file not found:[/red] {dat_path}")
        return

    system_name, df_dat = parse_dat_file(dat_path)
    
    console.print(f"[bold blue]INFO[/bold blue]: Checking {system_name} folder")
    
    for relative_path_str in explore.get_all_files(folder_path):
        file_path = folder_path / relative_path_str
        
        clean_file_name = Path(relative_path_str).name

        if explore.check_extension(file_path) == "application/x-zip-compressed":
            extract_and_verify(file_path, cache_path, df_dat, system_name, database_schema, database_table_name)
        else:
            verify_file(df_dat, system_name, clean_file_name, file_path, database_schema, database_table_name)