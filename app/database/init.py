import sqlite3
from pathlib import Path

def init_db(db_path="sports.db", schema_path="init.sql"):
    # Resolve DB under app/data and schema under app/database by default
    data_dir = Path(__file__).resolve().parent.parent / 'data'
    schema_dir = Path(__file__).resolve().parent  # app/database

    db_file = Path(db_path)
    if not db_file.is_absolute():
        db_file = data_dir / db_file

    schema_file = Path(schema_path)
    if not schema_file.is_absolute():
        schema_file = schema_dir / schema_file

    # Read schema from file
    if not schema_file.is_file():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    schema_sql = schema_file.read_text(encoding="utf-8")

    # Ensure DB directory exists and initialize
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()

    print(f"Database initialized at {db_file} using {schema_file}")

if __name__ == "__main__":
    init_db()

def seed_db(db_path="sports.db", seed_path="seed.sql"):
    """Load seed data into an existing DB created with init.sql."""
    data_dir = Path(__file__).resolve().parent.parent / 'data'
    seeds_dir = Path(__file__).resolve().parent  # app/database

    db_file = Path(db_path)
    if not db_file.is_absolute():
        db_file = data_dir / db_file

    seed_file = Path(seed_path)
    if not seed_file.is_absolute():
        seed_file = seeds_dir / seed_file

    if not seed_file.is_file():
        raise FileNotFoundError(f"Seed file not found: {seed_file}")

    sql = seed_file.read_text(encoding="utf-8")
    conn = sqlite3.connect(str(db_file))
    try:
        conn.executescript(sql)
        conn.commit()
        print(f"Database seeded at {db_file} using {seed_file}")
    finally:
        conn.close()
