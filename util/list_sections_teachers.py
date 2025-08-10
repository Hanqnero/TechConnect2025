import os
import sys
import sqlite3

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "app",
    "database",
    "sports.db",
)

MANAGE_PERMISSIONS = ("manage_classes", "edit_section")

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_sections_with_managers(conn: sqlite3.Connection):
    sql = """
        SELECT
            s.id,
            s.name,
            -- Use DISTINCT with single-arg GROUP_CONCAT (SQLite limitation) and then
            -- replace the default comma separator with '; ' for readability.
            COALESCE(
                REPLACE(
                    GROUP_CONCAT(DISTINCT u.full_name || ' <' || u.email || '>'),
                    ',',
                    '; '
                ),
                ''
            ) AS teachers
        FROM sections s
        LEFT JOIN section_permissions sp
            ON sp.section_id = s.id
            AND sp.permission IN (?, ?)
        LEFT JOIN users u
            ON u.id = sp.user_id
            AND u.role = 'teacher'
        GROUP BY s.id, s.name
        ORDER BY s.name;
    """
    return conn.execute(sql, MANAGE_PERMISSIONS).fetchall()

def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB_PATH
    if not os.path.isfile(db_path):
        print(f"Database not found: {db_path}")
        sys.exit(1)

    try:
        with get_connection(db_path) as conn:
            rows = fetch_sections_with_managers(conn)
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        sys.exit(2)

    if not rows:
        print("No sections found.")
        return

    for row in rows:
        teachers = row["teachers"].strip()
        print(f"Section: {row['name']} (id {row['id']})")
        print(f"  Managers: {teachers if teachers else 'None'}")

if __name__ == "__main__":
    main()
