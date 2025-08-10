#!/usr/bin/env python3
r"""
List all users from a SQLite DB (sports.db).
Usage:
  python list_users.py --db path\to\sports.db
If --db is omitted, it tries ./sports.db
"""
import argparse
import sqlite3
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="List users from sports.db")
    parser.add_argument("--db", default="sports.db", help="Path to sports.db (default: ./sports.db)")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    try:
        conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        cur = conn.cursor()

        # Check that users table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND lower(name)='users'")
        if not cur.fetchone():
            print("Table 'users' not found.", file=sys.stderr)
            # Show available tables to help debugging
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            print(f"Available tables: {tables}", file=sys.stderr)
            sys.exit(2)

        # Fetch all users; print columns dynamically
        cur.execute("SELECT * FROM users ORDER BY id")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]

        # Print header
        print(" | ".join(cols))
        print("-" * (len(" | ".join(cols)) + 2))

        for row in rows:
            print(" | ".join(str(v) if v is not None else "" for v in row))
    except sqlite3.Error as e:
        print(f"SQLite error: {e}", file=sys.stderr)
        sys.exit(3)
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()