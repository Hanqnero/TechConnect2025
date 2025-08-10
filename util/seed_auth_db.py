"""
Seed the auth SQLite database (app/data/auth.db) from app/auth/seed.sql.

Usage:
  python util/seed_auth_db.py
  python util/seed_auth_db.py --db app/data/auth.db --seed app/auth/seed.sql
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def run_sql_script(db_path: Path, sql_path: Path) -> None:
    if not sql_path.is_file():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = sql_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    default_db = repo_root / "app" / "data" / "auth.db"
    default_seed = repo_root / "app" / "auth" / "seed.sql"

    parser = argparse.ArgumentParser(description="Seed auth.db using app/auth/seed.sql")
    parser.add_argument("--db", type=Path, default=default_db, help=f"Path to auth SQLite DB (default: {default_db})")
    parser.add_argument("--seed", type=Path, default=default_seed, help=f"Path to auth seed SQL (default: {default_seed})")
    args = parser.parse_args()

    db_path: Path = args.db if args.db.is_absolute() else (repo_root / args.db)
    seed_path: Path = args.seed if args.seed.is_absolute() else (repo_root / args.seed)

    print(f"DB:   {db_path}")
    print(f"Seed: {seed_path}")
    run_sql_script(db_path, seed_path)
    print("Auth DB seeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
