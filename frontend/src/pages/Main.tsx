import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

type Role = 'student' | 'teacher';

// Minimal fake calendar: past, current, next month sections as in the sketch
export default function Main() {
  const [role, setRole] = useState<Role>('student');
  const [sportsUserId, setSportsUserId] = useState<number>(1);
  const [fullName, setFullName] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [classes, setClasses] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(false);
  const [attendedDates, setAttendedDates] = useState<Set<string>>(new Set());
  const [teacherClassDates, setTeacherClassDates] = useState<Set<string>>(new Set());
  const [futureStudentDates, setFutureStudentDates] = useState<Set<string>>(new Set());
  // Guard effects until whoami finishes to avoid initial wrong user fetch and race conditions
  const [whoamiReady, setWhoamiReady] = useState(false);
  // Request guards to ignore stale responses
  const studentDatesReqRef = useRef(0);
  const teacherDatesReqRef = useRef(0);

  // Create a simple list of days for current month
  const today = new Date();
  const daysInMonth = useMemo(() => new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate(), [today]);
  const days = useMemo(() => Array.from({ length: daysInMonth }, (_, i) => i + 1), [daysInMonth]);

  function formatDate(y: number, m: number, d: number) {
    const mm = String(m).padStart(2, '0');
    const dd = String(d).padStart(2, '0');
    return `${y}-${mm}-${dd}`;
  }

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/api/whoami', { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          if (data?.sports_user_id) setSportsUserId(data.sports_user_id);
          if (data?.role) setRole(data.role);
          if (data?.full_name) setFullName(data.full_name);
        }
      } catch {}
      finally {
        // Allow downstream effects to run only after whoami attempt completes
        setWhoamiReady(true);
      }
    })();
  }, []);

  // Load attendance highlights for current month for students
  useEffect(() => {
    (async () => {
      if (!whoamiReady || !sportsUserId || role !== 'student') {
        setAttendedDates(new Set());
        setFutureStudentDates(new Set());
        return;
      }
      const reqId = ++studentDatesReqRef.current;
      const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
      try {
        const [pRes, lRes, fRes] = await Promise.all([
          fetch(`/api/attendance/dates?user_id=${sportsUserId}&month=${month}&status=present`),
          fetch(`/api/attendance/dates?user_id=${sportsUserId}&month=${month}&status=late`),
          fetch(`/api/classes/future-dates?user_id=${sportsUserId}&month=${month}`),
        ]);
        const p = pRes.ok ? await pRes.json() : { dates: [] };
        const l = lRes.ok ? await lRes.json() : { dates: [] };
        const f = fRes.ok ? await fRes.json() : { dates: [] };
        // Ignore if a newer request has started
        if (reqId !== studentDatesReqRef.current) return;
        const all = new Set<string>([...(p.dates ?? []), ...(l.dates ?? [])]);
        setAttendedDates(all);
        setFutureStudentDates(new Set((f.dates ?? []) as string[]));
      } catch {
        setAttendedDates(new Set());
        setFutureStudentDates(new Set());
      }
    })();
  }, [sportsUserId, role, whoamiReady]);

  // Load class dates for teacher to highlight
  useEffect(() => {
    (async () => {
      if (!whoamiReady || !sportsUserId || role !== 'teacher') {
        setTeacherClassDates(new Set());
        return;
      }
      const reqId = ++teacherDatesReqRef.current;
      const month = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
      try {
        const res = await fetch(`/api/classes/dates?user_id=${sportsUserId}&month=${month}`);
        const data = res.ok ? await res.json() : { dates: [] };
        if (reqId !== teacherDatesReqRef.current) return;
        setTeacherClassDates(new Set((data?.dates ?? []) as string[]));
      } catch {
        setTeacherClassDates(new Set());
      }
    })();
  }, [sportsUserId, role, whoamiReady]);

  useEffect(() => {
    let active = true;
    async function load() {
      if (!selectedDate) return;
      setLoading(true);
      try {
        const params = new URLSearchParams({ date: selectedDate, user_id: String(sportsUserId) });
        const res = await fetch(`/api/schedule?${params.toString()}`);
        const data = await res.json();
        if (!active) return;
        setClasses(data.classes || []);
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => { active = false; };
  }, [selectedDate, role, sportsUserId]);

  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
    } catch (_) {
      // ignore
    } finally {
      navigate('/login', { replace: true });
    }
  }

  return (
    <div className="min-h-dvh bg-gray-50">
      <header className="px-4 py-3 sm:px-6 border-b bg-white sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <h1 className="text-xl sm:text-2xl font-semibold text-gray-900">Роль: {role === 'student' ? 'Студент' : 'Преподаватель'}</h1>
          <div className="flex items-center gap-3">
            {role === 'teacher' ? (
              <Link to="/teacher/profile" className="rounded-lg px-3 py-2 text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-500">Профиль</Link>
            ) : (
              <Link to="/profile" className="rounded-lg px-3 py-2 text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-500">Профиль</Link>
            )}
            <button onClick={handleLogout} className="rounded-lg px-3 py-2 text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 ring-1 ring-gray-300">Выйти</button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">
        <section className="rounded-xl border bg-white p-4 sm:p-6">
          <h2 className="text-sm font-semibold text-gray-700">Привет, {fullName || 'друг'}</h2>
          <p className="text-gray-600 mt-2">Выберите дату в календаре ниже, чтобы посмотреть занятия.</p>
        </section>

        <section className="rounded-xl border bg-white p-4 sm:p-6">
          <h2 className="text-sm font-semibold text-gray-700">Текущий месяц</h2>
          <div className="mt-4 grid grid-cols-7 gap-2">
            {days.map((d) => {
              const dateKey = formatDate(today.getFullYear(), today.getMonth() + 1, d);
              const isToday = d === today.getDate();
              const isSelected = selectedDate === dateKey;
              const isAttended = role === 'student' && attendedDates.has(dateKey);
              const isFuture = role === 'student' && futureStudentDates.has(dateKey);
              const isTeachingDay = role === 'teacher' && teacherClassDates.has(dateKey);
              return (
                <button
                  key={d}
                  onClick={() => setSelectedDate(dateKey)}
                  className={`aspect-square rounded-lg text-sm font-medium ring-1 flex items-center justify-center hover:text-indigo-700 ${
                    isAttended ? 'bg-emerald-50 text-emerald-700 ring-emerald-200 hover:ring-emerald-300' : isTeachingDay ? 'bg-amber-50 text-amber-700 ring-amber-200 hover:ring-amber-300' : 'ring-gray-200 hover:ring-indigo-400'
                  } ${isFuture && !isAttended ? 'outline outline-2 outline-emerald-300' : ''} ${isToday ? 'outline outline-1 outline-indigo-300' : ''} ${isSelected ? 'outline outline-2 outline-indigo-500' : ''}`}
                  aria-pressed={isSelected}
                >
                  {d}
                </button>
              );
            })}
          </div>
        </section>

        <section className="rounded-xl border bg-white p-4 sm:p-6">
          <h2 className="text-sm font-semibold text-gray-700">{selectedDate ? `Занятия на ${selectedDate}` : 'Выберите дату'}</h2>
          <ul className="mt-4 space-y-2">
            {!selectedDate && <li className="text-gray-600">Нет выбранной даты.</li>}
            {selectedDate && loading && <li className="text-gray-600">Загрузка…</li>}
            {selectedDate && !loading && classes.length === 0 && (
              <li className="text-gray-600">Занятий нет.</li>
            )}
            {selectedDate && !loading && classes.map((c) => (
              <li key={c.id} className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="font-medium">{c.section}</p>
                  <p className="text-sm text-gray-600">{new Date(c.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · {c.location}</p>
                </div>
                {role === 'teacher' ? (
                  <Link to={`/classes/${c.id}/mark`} className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500">Отметить</Link>
                ) : c.attendance_status ? (
                  <span className="text-xs px-2 py-1 rounded bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200">отмечен</span>
                ) : (
                  <span className="text-xs px-2 py-1 rounded text-emerald-700 ring-1 ring-emerald-300">записан</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
}
