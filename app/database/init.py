import sqlite3
from pathlib import Path

def init_db(db_path="sports.db", schema_path="init.sql"):
    # Resolve paths relative to this file's directory
    base_dir = Path(__file__).resolve().parent

    db_file = Path(db_path)
    if not db_file.is_absolute():
        db_file = base_dir / db_file

    schema_file = Path(schema_path)
    if not schema_file.is_absolute():
        schema_file = base_dir / schema_file

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
