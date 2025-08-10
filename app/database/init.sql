CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    date DATETIME NOT NULL,
    location TEXT,
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE TABLE IF NOT EXISTS section_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(section_id, user_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'late')),
    notes TEXT,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE(class_id, student_id)
);

CREATE TABLE IF NOT EXISTS section_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    permission TEXT NOT NULL CHECK(permission IN ('manage_classes', 'edit_section', 'view_attendance', 'edit_attendance')),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(section_id, user_id, permission)
);

-- Mapping between auth service login and sports users (app-layer linkage)
CREATE TABLE IF NOT EXISTS auth_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auth_login TEXT NOT NULL UNIQUE,
    sports_user_id INTEGER NOT NULL,
    FOREIGN KEY (sports_user_id) REFERENCES users(id)
);
