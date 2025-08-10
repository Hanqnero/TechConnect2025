-- Локализованные (RU) тестовые данные для sports.db
-- Сценарий очищает БД и заполняет её демонстрационными данными.
-- Примеры запуска:
--   1) Python: import sqlite3; conn=sqlite3.connect('app/database/sports.db'); conn.executescript(open('app/database/seed.sql','r',encoding='utf-8').read()); conn.commit(); conn.close()
--   2) sqlite CLI: sqlite3 app/database/sports.db ".read app/database/seed.sql"

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- Очистка данных (важен порядок из‑за внешних ключей)
DELETE FROM attendance;
DELETE FROM section_permissions;
DELETE FROM auth_links;
DELETE FROM section_members;
DELETE FROM classes;
DELETE FROM sections;
DELETE FROM users;

PRAGMA foreign_keys = ON;

-- Пользователи (студенты и преподаватели)
-- Важно: ID 1..7 сохраняются, т.к. на них ссылаются ниже и логика приложения
INSERT INTO users (id, full_name, email, role, created_at) VALUES
  (1, 'Администратор', 'admin@edu.susu.ru', 'admin', CURRENT_TIMESTAMP),
  (2, 'Иван Иванов', 'ivanov@edu.susu.ru', 'student', CURRENT_TIMESTAMP),
  (3, 'Мария Смирнова', 'smirnova@edu.susu.ru', 'student', CURRENT_TIMESTAMP),
  (4, 'Даниил Волков', 'volkov.dan@edu.susu.ru', 'student', CURRENT_TIMESTAMP),
  (5, 'Тина Петрова', 'tina@edu.susu.ru', 'teacher', CURRENT_TIMESTAMP);

-- Секции
INSERT INTO sections (id, name, description, created_at) VALUES
  (1, 'Баскетбол', 'Тренировки и участие в соревнованиях в сборной ЮУрГУ по баскетболу', CURRENT_TIMESTAMP),
  (2, 'Настольный теннис', 'Игра в настольный теннис между участниками секции', CURRENT_TIMESTAMP),
  (3, 'Дартс', 'Секция по дартсу', CURRENT_TIMESTAMP);

-- Занятия внутри секций (ISO-8601 дата/время)
INSERT INTO classes (id, section_id, date, location) VALUES
  (1, 1, '2025-08-11 16:00:00', 'Зал А'),
  (2, 1, '2025-08-13 16:00:00', 'Зал B'),
  (3, 2, '2025-08-12 17:00:00', 'Поле 1'),
  (4, 2, '2025-08-14 17:00:00', 'Поле 2'),
  (5, 3, '2025-08-15 18:00:00', 'Место секции дартса');

-- Участники секций (студенты + преподаватели)
-- Баскетбол: преподаватель Тина (5), студенты: Иван (1), Мария (2), Даниил (3)
INSERT INTO section_members (id, section_id, user_id, role) VALUES
  (1, 1, 5, 'teacher'),
  (2, 1, 2, 'student'),
  (3, 1, 3, 'student'),
  (4, 1, 4, 'student');

-- Настольный теннис: преподаватель Тина (5), студенты: Мария (3), Даниил (4)
INSERT INTO section_members (id, section_id, user_id, role) VALUES
  (5, 2, 5, 'teacher'),
  (6, 2, 3, 'student'),
  (7, 2, 4, 'student');

-- Дартс: преподаватель Тина (5), студенты: Иван (2), Даниил (4)
INSERT INTO section_members (id, section_id, user_id, role) VALUES
  (8, 3, 5, 'teacher'),
  (9, 3, 2, 'student'),
  (10, 3, 4, 'student');

-- Права доступа
-- Оставляем только 'edit_attendance' для преподавателей и администратора
INSERT INTO section_permissions (id, section_id, user_id, permission) VALUES
  -- Баскетбол (секция 1) — преподаватель Тина (5)
  (1, 1, 5, 'edit_attendance'),
  -- Настольный теннис (секция 2) — преподаватель Тина (5)
  (2, 2, 5, 'edit_attendance'),
  -- Дартс (секция 3) — преподаватель Тина (5)
  (3, 3, 5, 'edit_attendance'),
  -- Администратор (1) — 'edit_attendance' по всем секциям
  (4, 1, 1, 'edit_attendance'),
  (5, 2, 1, 'edit_attendance'),
  (6, 3, 1, 'edit_attendance');

-- Привязка логина из auth к пользователю в sports (по умолчанию только один преподаватель)
INSERT INTO auth_links (auth_login, sports_user_id) VALUES
  ('admin', 1),
  ('ivan', 2),
  ('maria', 3),
  ('daniil', 4),
  ('tina', 5);

COMMIT;
