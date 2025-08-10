-- Users (both students and teachers)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sports sections
CREATE TABLE sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Classes within sections
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    date DATETIME NOT NULL,
    location TEXT,
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

-- Membership of users in sections (students, teachers)
CREATE TABLE section_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(section_id, user_id)
);

-- Attendance records
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('present', 'absent', 'late')),
    notes TEXT,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE(class_id, student_id)
);

-- Permissions for managing sections
CREATE TABLE section_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    permission TEXT NOT NULL CHECK(permission IN ('manage_classes', 'edit_section', 'view_attendance', 'edit_attendance')),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(section_id, user_id, permission)
);
