import { Link, useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

type Student = { id: number; full_name: string; status?: string };

export default function MarkAttendance() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [students, setStudents] = useState<Student[]>([]);
  const [checked, setChecked] = useState<Record<number, boolean>>({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      if (!id) return;
      // Guard: only teachers can mark attendance
      try {
        const me = await fetch('/api/whoami', { credentials: 'include' }).then(r => r.json()).catch(() => ({ role: 'student' }));
        if (me?.role !== 'teacher') {
          navigate('/', { replace: true });
          return;
        }
      } catch {}
      const res = await fetch(`/api/classes/${id}/students`);
      const data = await res.json();
      setStudents(data);
      const pre: Record<number, boolean> = {};
      data.forEach((s: Student) => { if (s.status === 'present') pre[s.id] = true; });
      setChecked(pre);
    }
    load();
  }, [id, navigate]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    const student_ids = Object.entries(checked).filter(([, v]) => v).map(([k]) => Number(k));
    setSubmitting(true);
    try {
      await fetch(`/api/classes/${id}/attendance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ student_ids, status: 'present', replace: true }),
      });
      history.back();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-dvh bg-gray-50 p-4 sm:p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">Отметить на занятии · #{id}</h1>
          <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-700">Назад</Link>
        </header>
        <form className="rounded-xl border bg-white p-4 sm:p-6 space-y-4" onSubmit={onSubmit}>
          <ul className="divide-y">
            {students.map((s) => (
              <li key={s.id} className="flex items-center justify-between py-3">
                <span className="text-gray-800">{s.full_name}</span>
                <input
                  type="checkbox"
                  className="h-5 w-5 accent-indigo-600"
                  checked={!!checked[s.id]}
                  onChange={(e) => setChecked((m) => ({ ...m, [s.id]: e.target.checked }))}
                />
              </li>
            ))}
          </ul>
          <button className="rounded-lg bg-indigo-600 px-4 py-2 text-white font-medium hover:bg-indigo-500 disabled:opacity-50" type="submit" disabled={submitting}>
            {submitting ? 'Сохранение…' : 'Отправить посещаемость'}
          </button>
        </form>
      </div>
    </div>
  );
}
