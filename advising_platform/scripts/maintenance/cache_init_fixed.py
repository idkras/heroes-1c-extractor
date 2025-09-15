#!/usr/bin/env python3
"""
DuckDB Cache Initialization - Simplified version
Loads 49 discovered standards into DuckDB cache
"""

import os
import sys
import duckdb
from pathlib import Path

def main():
    """Initialize DuckDB cache with standards"""
    print("Initializing DuckDB standards cache...")
    
    # Connect to DuckDB
    db_path = "standards_system.duckdb"
    conn = duckdb.connect(db_path)
    
    # Create standards table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS standards (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            path VARCHAR NOT NULL,
            content TEXT,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Load standards from filesystem
    standards_dir = Path("[standards .md]")
    loaded_count = 0
    
    if standards_dir.exists():
        for md_file in standards_dir.rglob("*.md"):
            # Skip archive files
            if "[archive]" in str(md_file):
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                standard_id = str(md_file.relative_to(standards_dir))
                word_count = len(content.split())
                
                # Insert into database
                conn.execute("""
                    INSERT OR REPLACE INTO standards (id, name, path, content, word_count)
                    VALUES (?, ?, ?, ?, ?)
                """, [standard_id, md_file.stem, str(md_file), content, word_count])
                
                loaded_count += 1
                
            except Exception as e:
                print(f"Warning: Failed to load {md_file}: {e}")
    
    # Get final count
    result = conn.execute("SELECT COUNT(*) FROM standards").fetchone()
    final_count = result[0] if result else 0
    
    print(f"✅ Successfully loaded {loaded_count} standards")
    print(f"✅ Database contains {final_count} standards total")
    print(f"✅ Database: {db_path}")
    
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())