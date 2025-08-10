import { Link, useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';

type Section = { id: number; name: string; description?: string };
 type Student = { id: number; full_name: string; email: string };

export default function SectionEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [section, setSection] = useState<Section | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const me = await fetch('/api/whoami', { credentials: 'include' }).then(r => r.json()).catch(() => ({ role: 'student' }));
        if (me?.role !== 'teacher') {
          navigate('/', { replace: true });
          return;
        }
        if (!id) return;
        const [sRes, stRes] = await Promise.all([
          fetch(`/api/sections/${id}`),
          fetch(`/api/sections/${id}/students`),
        ]);
        if (sRes.ok) setSection(await sRes.json());
        if (stRes.ok) setStudents(await stRes.json());
      } finally {
        setLoading(false);
      }
    })();
  }, [id, navigate]);

  return (
    <div className="min-h-dvh bg-gray-50 p-4 sm:p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">Редактирование секции</h1>
          <Link to="/teacher/profile" className="text-sm text-indigo-600 hover:text-indigo-700">Назад</Link>
        </header>

        <section className="rounded-xl border bg-white p-4 sm:p-6 space-y-4">
          {loading && <p className="text-gray-600">Загрузка…</p>}
          {!loading && section && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{section.name}</h2>
              {section.description && <p className="text-gray-600">{section.description}</p>}
            </div>
          )}
          <div>
            <h3 className="text-sm font-semibold text-gray-700">Ученики</h3>
            <ul className="mt-3 divide-y rounded-lg border bg-white">
              {students.map((s) => (
                <li key={s.id} className="flex items-center justify-between p-3">
                  <div>
                    <p className="font-medium">{s.full_name}</p>
                    <p className="text-sm text-gray-600">{s.email}</p>
                  </div>
                  <span className="text-xs rounded bg-gray-100 text-gray-700 px-2 py-1 ring-1 ring-gray-200">студент</span>
                </li>
              ))}
              {!loading && students.length === 0 && (
                <li className="p-3 text-gray-600">В секции пока нет студентов.</li>
              )}
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}
