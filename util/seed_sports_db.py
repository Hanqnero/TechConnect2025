"""
Seed the sports SQLite database by executing app/database/seed.sql.

By default, this script also applies the schema from app/database/init.sql
before seeding to ensure all tables exist (idempotent CREATEs). You can skip
applying the schema with --skip-schema.

Usage examples:
  - Use defaults (recommended):
      python util/seed_sports_db.py

  - Specify custom paths:
      python util/seed_sports_db.py --db app/database/sports.db --seed app/database/seed.sql --schema app/database/init.sql

  - Skip schema application:
      python util/seed_sports_db.py --skip-schema
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
    default_db = repo_root / "app" / "database" / "sports.db"
    default_seed = repo_root / "app" / "database" / "seed.sql"
    default_schema = repo_root / "app" / "database" / "init.sql"

    parser = argparse.ArgumentParser(description="Seed sports.db using seed.sql (and optionally apply schema).")
    parser.add_argument("--db", type=Path, default=default_db, help=f"Path to SQLite DB file (default: {default_db})")
    parser.add_argument("--seed", type=Path, default=default_seed, help=f"Path to seed.sql (default: {default_seed})")
    parser.add_argument("--schema", type=Path, default=default_schema, help=f"Path to init.sql (default: {default_schema})")
    parser.add_argument("--skip-schema", action="store_true", help="Do not apply schema before seeding")
    args = parser.parse_args()

    db_path: Path = args.db if args.db.is_absolute() else (repo_root / args.db)
    seed_path: Path = args.seed if args.seed.is_absolute() else (repo_root / args.seed)
    schema_path: Path = args.schema if args.schema.is_absolute() else (repo_root / args.schema)

    print(f"DB:     {db_path}")
    print(f"Seed:   {seed_path}")
    if not args.skip_schema:
        print(f"Schema: {schema_path}")
        print("Applying schema...")
        run_sql_script(db_path, schema_path)
    else:
        print("Skipping schema application (per flag)")

    print("Executing seed script...")
    run_sql_script(db_path, seed_path)
    print("Seeding complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
