import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

type Section = { id: number; name: string; description?: string };

export default function TeacherProfile() {
  const navigate = useNavigate();
  const [sections, setSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const me = await fetch('/api/whoami', { credentials: 'include' }).then(r => r.json()).catch(() => ({ role: 'student' }));
        if (me?.role !== 'teacher') {
          navigate('/', { replace: true });
          return;
        }
        const res = await fetch(`/api/teacher/sections?user_id=${me.sports_user_id}`);
        const data = await res.json();
        setSections(data || []);
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  return (
    <div className="min-h-dvh bg-gray-50 p-4 sm:p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">Профиль учителя</h1>
          <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-700">Назад</Link>
        </header>

        <section className="rounded-xl border bg-white p-4 sm:p-6">
          <h2 className="text-sm font-semibold text-gray-700">Секции с правом редактирования</h2>
          {loading ? (
            <p className="mt-4 text-gray-600">Загрузка…</p>
          ) : (
            <ul className="mt-4 space-y-2">
              {sections.length === 0 && (
                <li className="text-gray-600">Нет доступных секций.</li>
              )}
              {sections.map((s) => (
                <li key={s.id} className="rounded-lg border p-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{s.name}</p>
                    {s.description && <p className="text-sm text-gray-600">{s.description}</p>}
                  </div>
                  <Link to={`/teacher/sections/${s.id}/edit`} className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500">Редактировать</Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
