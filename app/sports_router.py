from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Literal, Optional
import sqlite3
from pathlib import Path
from pydantic import BaseModel
from .database.init import init_db, seed_db
from .auth.security import get_current_user_optional

DB_PATH = Path(__file__).resolve().parent / 'data' / 'sports.db'

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

router = APIRouter(prefix='/api', tags=['sports'])

@router.on_event('startup')
def _ensure_db():
    # Initialize schema and seed once if empty
    created = False
    if not DB_PATH.exists():
        init_db(db_path=str(DB_PATH), schema_path=str(Path(__file__).resolve().parent / 'database' / 'init.sql'))
        created = True
    # seed when created or when sections table is empty
    with _conn() as c:
        try:
            cnt = c.execute('SELECT COUNT(1) FROM sections').fetchone()[0]
        except sqlite3.OperationalError:
            cnt = 0
    if created or cnt == 0:
        seed_db(db_path=str(DB_PATH), seed_path=str(Path(__file__).resolve().parent / 'database' / 'seed.sql'))

def _resolve_sports_user_from_login(login: str) -> tuple[Optional[int], Optional[str]]:
    """Resolve sports user by auth login using DB table auth_links.
    Returns (sports_user_id, role) or (None, None) if not found.
    """
    key = (login or '').strip().lower()
    if not key:
        return None, None
    with _conn() as c:
        row = c.execute("SELECT sports_user_id FROM auth_links WHERE auth_login = ?", (key,)).fetchone()
        if not row:
            return None, None
        user_id = int(row[0])
        u = c.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
        role = (u[0].lower() if u else None)
        return user_id, role

@router.get('/whoami')
def whoami(user = Depends(get_current_user_optional)):
    # Require authentication to resolve actual sports user mapping
    if not (user and user.get('login')):
        return { 'sports_user_id': None, 'role': None, 'full_name': None }
    sport_id, role = _resolve_sports_user_from_login(user['login'])
    with _conn() as c:
        if sport_id is None:
            return { 'sports_user_id': None, 'role': None, 'full_name': None }
        row = c.execute('SELECT full_name, role FROM users WHERE id = ?', (sport_id,)).fetchone()
        full_name = row['full_name'] if row else None
        db_role = row['role'].lower() if row else role
    return { 'sports_user_id': sport_id, 'role': db_role, 'full_name': full_name }

def _get_user_role(conn: sqlite3.Connection, user_id: int) -> str:
    row = conn.execute('SELECT role FROM users WHERE id = ?', (user_id,)).fetchone()
    r = (row['role'] if row else 'student').lower()
    return 'teacher' if r == 'teacher' else 'student'

@router.get('/sections')
def sections(user_id: int = Query(...)):
    sql = (
        "SELECT s.id, s.name, s.description FROM sections s "
        "JOIN section_members m ON m.section_id = s.id "
        "WHERE m.user_id = ? AND m.role = ? ORDER BY s.name"
    )
    with _conn() as c:
        role = _get_user_role(c, user_id)
        rows = c.execute(sql, (user_id, role)).fetchall()
        return [dict(r) for r in rows]

@router.get('/schedule')
def schedule(
    date: str = Query(..., description='YYYY-MM-DD'),
    user_id: int = Query(...),
):
    # normalize date to YYYY-MM-DD
    if len(date) < 10:
        raise HTTPException(status_code=400, detail='Дата должна быть в формате YYYY-MM-DD')
    with _conn() as c:
        role = _get_user_role(c, user_id)
        where_member_role = role
        if role == 'student':
            sql = (
                "SELECT c.id, c.section_id, s.name AS section, c.date, c.location, "
                "IFNULL(a.status, '') AS attendance_status "
                "FROM classes c "
                "JOIN sections s ON s.id = c.section_id "
                "JOIN section_members m ON m.section_id = c.section_id AND m.role = ? AND m.user_id = ? "
                "LEFT JOIN attendance a ON a.class_id = c.id AND a.student_id = ? "
                "WHERE date(c.date) = date(?) "
                "ORDER BY c.date"
            )
            rows = c.execute(sql, (where_member_role, user_id, user_id, date)).fetchall()
        else:
            sql = (
                "SELECT c.id, c.section_id, s.name AS section, c.date, c.location "
                "FROM classes c "
                "JOIN sections s ON s.id = c.section_id "
                "JOIN section_members m ON m.section_id = c.section_id AND m.role = ? AND m.user_id = ? "
                "WHERE date(c.date) = date(?) "
                "ORDER BY c.date"
            )
            rows = c.execute(sql, (where_member_role, user_id, date)).fetchall()
        return {"date": date, "role": role, "classes": [dict(r) for r in rows]}

@router.get('/attendance/dates')
def attendance_dates(
    user_id: int = Query(...),
    month: str = Query(..., description='YYYY-MM'),
    status: Literal['present','absent','late'] = Query('present')
):
    """Return distinct dates (YYYY-MM-DD) in the given month when the user has attendance with the specified status.
    Intended for student calendar highlighting.
    """
    if len(month) != 7 or month[4] != '-':
        raise HTTPException(status_code=400, detail='Месяц должен быть в формате YYYY-MM')
    sql = (
        "SELECT DISTINCT date(c.date) AS d "
        "FROM attendance a "
        "JOIN classes c ON c.id = a.class_id "
        "WHERE a.student_id = ? AND a.status = ? AND strftime('%Y-%m', c.date) = ? "
        "ORDER BY d"
    )
    with _conn() as c:
        rows = c.execute(sql, (user_id, status, month)).fetchall()
        return {"month": month, "status": status, "dates": [r["d"] for r in rows]}

@router.get('/classes/dates')
def classes_dates(
    user_id: int = Query(...),
    month: str = Query(..., description='YYYY-MM'),
):
    """Return distinct dates (YYYY-MM-DD) within the month when the user has classes
    in sections according to their role membership (student or teacher).
    """
    if len(month) != 7 or month[4] != '-':
        raise HTTPException(status_code=400, detail='Месяц должен быть в формате YYYY-MM')
    with _conn() as c:
        role = _get_user_role(c, user_id)
        sql = (
            "SELECT DISTINCT date(c.date) AS d "
            "FROM classes c "
            "JOIN section_members m ON m.section_id = c.section_id "
            "WHERE m.user_id = ? AND m.role = ? AND strftime('%Y-%m', c.date) = ? "
            "ORDER BY d"
        )
        rows = c.execute(sql, (user_id, role, month)).fetchall()
        return {"month": month, "role": role, "dates": [r["d"] for r in rows]}

@router.get('/classes/future-dates')
def classes_future_dates(
    user_id: int = Query(...),
    month: str = Query(..., description='YYYY-MM'),
):
    """Return distinct future class dates in the given month for a student's sections.
    Used to draw an outline for upcoming classes on the calendar.
    """
    if len(month) != 7 or month[4] != '-':
        raise HTTPException(status_code=400, detail='Месяц должен быть в формате YYYY-MM')
    with _conn() as c:
        role = _get_user_role(c, user_id)
        # Only apply to students per spec
        if role != 'student':
            return {"month": month, "role": role, "dates": []}
        sql = (
            "SELECT DISTINCT date(c.date) AS d "
            "FROM classes c "
            "JOIN section_members m ON m.section_id = c.section_id AND m.role = 'student' "
            "WHERE m.user_id = ? AND strftime('%Y-%m', c.date) = ? AND datetime(c.date) >= datetime('now') "
            "ORDER BY d"
        )
        rows = c.execute(sql, (user_id, month)).fetchall()
        return {"month": month, "dates": [r["d"] for r in rows]}

@router.get('/teacher/sections')
def teacher_sections(user_id: int = Query(...)):
    """List sections where the teacher has edit permissions."""
    sql = (
        "SELECT DISTINCT s.id, s.name, s.description "
        "FROM sections s "
    "JOIN section_permissions p ON p.section_id = s.id "
    "WHERE p.user_id = ? AND p.permission IN ('edit_section','edit_attendance') "
        "ORDER BY s.name"
    )
    with _conn() as c:
        rows = c.execute(sql, (user_id,)).fetchall()
        return [dict(r) for r in rows]

@router.get('/sections/all')
def sections_all():
    with _conn() as c:
        rows = c.execute('SELECT id, name, description FROM sections ORDER BY name').fetchall()
        return [dict(r) for r in rows]

@router.get('/sections/available')
def sections_available(user_id: int = Query(...)):
    """List sections where the given student is NOT currently a member as a student."""
    sql = (
        "SELECT s.id, s.name, s.description FROM sections s "
        "WHERE s.id NOT IN (SELECT section_id FROM section_members WHERE user_id = ? AND role = 'student') "
        "ORDER BY s.name"
    )
    with _conn() as c:
        rows = c.execute(sql, (user_id,)).fetchall()
        return [dict(r) for r in rows]

@router.get('/sections/{section_id}')
def section_detail(section_id: int):
    with _conn() as c:
        row = c.execute('SELECT id, name, description FROM sections WHERE id = ?', (section_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Секция не найдена')
        return dict(row)

@router.get('/sections/{section_id}/students')
def section_students(section_id: int):
    sql = (
        "SELECT u.id, u.full_name, u.email "
        "FROM section_members m "
        "JOIN users u ON u.id = m.user_id "
        "WHERE m.section_id = ? AND m.role = 'student' "
        "ORDER BY u.full_name"
    )
    with _conn() as c:
        rows = c.execute(sql, (section_id,)).fetchall()
        return [dict(r) for r in rows]

@router.get('/classes/{class_id}/students')
def class_students(class_id: int):
    sql = (
        "SELECT u.id, u.full_name, u.email, IFNULL(a.status, '') AS status "
        "FROM classes c "
        "JOIN section_members m ON m.section_id = c.section_id AND m.role='student' "
        "JOIN users u ON u.id = m.user_id "
        "LEFT JOIN attendance a ON a.class_id = c.id AND a.student_id = u.id "
        "WHERE c.id = ? ORDER BY u.full_name"
    )
    with _conn() as c:
        rows = c.execute(sql, (class_id,)).fetchall()
        return [dict(r) for r in rows]

class AttendanceRequest(BaseModel):
    student_ids: List[int]
    status: Literal['present','absent','late'] = 'present'
    notes: Optional[str] = None
    replace: Optional[bool] = False

@router.post('/classes/{class_id}/attendance')
def set_attendance(class_id: int, payload: AttendanceRequest):
    if not payload.student_ids:
        # allow empty list when replace=true to clear existing 'present' marks
        if not payload.replace:
            raise HTTPException(status_code=400, detail='Необходимо указать student_ids')
    sql = (
        "INSERT INTO attendance (class_id, student_id, status, notes) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(class_id, student_id) DO UPDATE SET status=excluded.status, notes=excluded.notes"
    )
    with _conn() as c:
        cur = c.cursor()
        for sid in payload.student_ids:
            cur.execute(sql, (class_id, sid, payload.status, payload.notes))
        # If replace mode, remove 'present' attendance for students not in the list
        if payload.replace:
            if payload.student_ids:
                q = (
                    "DELETE FROM attendance WHERE class_id = ? AND status = 'present' AND student_id NOT IN (" +
                    ",".join(["?"] * len(payload.student_ids)) + ")"
                )
                cur.execute(q, (class_id, *payload.student_ids))
            else:
                # No students checked: clear all 'present' marks for the class
                cur.execute("DELETE FROM attendance WHERE class_id = ? AND status = 'present'", (class_id,))
        c.commit()
    return {"class_id": class_id, "updated": len(payload.student_ids), "status": payload.status, "replace": payload.replace}


class MembershipChange(BaseModel):
    user_id: int

@router.post('/sections/{section_id}/subscribe')
def subscribe_section(section_id: int, payload: MembershipChange):
    with _conn() as c:
        # Ensure user is a student from users table; default to student if missing
        role = _get_user_role(c, payload.user_id)
        if role != 'student':
            # Allow non-students to subscribe as students? We'll restrict per spec.
            raise HTTPException(status_code=400, detail='Только студенты могут записываться на секции')
        try:
            c.execute(
                'INSERT INTO section_members (section_id, user_id, role) VALUES (?, ?, ?)',
                (section_id, payload.user_id, 'student')
            )
            c.commit()
        except sqlite3.IntegrityError:
            # Already a member or foreign key issue
            pass
    return {"section_id": section_id, "user_id": payload.user_id, "subscribed": True}

@router.post('/sections/{section_id}/unsubscribe')
def unsubscribe_section(section_id: int, payload: MembershipChange):
    with _conn() as c:
        c.execute(
            'DELETE FROM section_members WHERE section_id = ? AND user_id = ? AND role = \"student\"',
            (section_id, payload.user_id)
        )
        c.commit()
    return {"section_id": section_id, "user_id": payload.user_id, "subscribed": False}
