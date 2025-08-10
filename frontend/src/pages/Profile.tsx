import { Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

type Section = { id: number; name: string; description?: string };

export default function Profile() {
  const navigate = useNavigate();
  const [me, setMe] = useState<{ sports_user_id: number | null; role: string | null }>({ sports_user_id: null, role: null });
  const [mySections, setMySections] = useState<Section[]>([]);
  const [availableSections, setAvailableSections] = useState<Section[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyIds, setBusyIds] = useState<Record<number, boolean>>({});

  useEffect(() => {
    (async () => {
      try {
        const who = await fetch('/api/whoami', { credentials: 'include' }).then(r => r.json()).catch(() => ({ sports_user_id: 1, role: 'student' }));
        if (who?.role !== 'student') {
          // If teacher navigates here, send to teacher profile
          navigate('/teacher/profile', { replace: true });
          return;
        }
        setMe(who);
        const [mineRes, availRes] = await Promise.all([
          fetch(`/api/sections?user_id=${who.sports_user_id}`),
          fetch(`/api/sections/available?user_id=${who.sports_user_id}`),
        ]);
        setMySections(mineRes.ok ? await mineRes.json() : []);
        setAvailableSections(availRes.ok ? await availRes.json() : []);
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  async function refreshLists() {
    if (!me.sports_user_id) return;
    const [mineRes, availRes] = await Promise.all([
      fetch(`/api/sections?user_id=${me.sports_user_id}`),
      fetch(`/api/sections/available?user_id=${me.sports_user_id}`),
    ]);
    setMySections(mineRes.ok ? await mineRes.json() : []);
    setAvailableSections(availRes.ok ? await availRes.json() : []);
  }

  async function unsubscribe(sectionId: number) {
    if (!me.sports_user_id) return;
    setBusyIds(b => ({ ...b, [sectionId]: true }));
    try {
      await fetch(`/api/sections/${sectionId}/unsubscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: me.sports_user_id }),
      });
  await refreshLists();
    } finally {
      setBusyIds(b => ({ ...b, [sectionId]: false }));
    }
  }

  async function subscribe(sectionId: number) {
    if (!me.sports_user_id) return;
    setBusyIds(b => ({ ...b, [sectionId]: true }));
    try {
      await fetch(`/api/sections/${sectionId}/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: me.sports_user_id }),
      });
  await refreshLists();
    } finally {
      setBusyIds(b => ({ ...b, [sectionId]: false }));
    }
  }

  return (
    <div className="min-h-dvh bg-gray-50 p-4 sm:p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">Профиль</h1>
          <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-700">Назад</Link>
        </header>

        <section className="rounded-xl border bg-white p-4 sm:p-6">
          <h2 className="text-sm font-semibold text-gray-700">Мои секции</h2>
          {loading ? (
            <p className="mt-4 text-gray-600">Загрузка…</p>
          ) : (
            <ul className="mt-4 space-y-2">
              {mySections.length === 0 && <li className="text-gray-600">Вы не записаны ни на одну секцию.</li>}
              {mySections.map((s) => (
                <li key={s.id} className="rounded-lg border p-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{s.name}</p>
                    {s.description && <p className="text-sm text-gray-600">{s.description}</p>}
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => unsubscribe(s.id)}
                      disabled={!!busyIds[s.id]}
                      className="rounded-md bg-gray-100 text-gray-800 ring-1 ring-gray-300 px-3 py-1.5 text-sm font-medium hover:bg-gray-200 disabled:opacity-50"
                    >Отписаться от секции</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded-xl border bg-white p-4 sm:p-6">
          <h2 className="text-sm font-semibold text-gray-700">Все секции</h2>
          {loading ? (
            <p className="mt-4 text-gray-600">Загрузка…</p>
          ) : (
            <ul className="mt-4 space-y-2">
              {availableSections.length === 0 && <li className="text-gray-600">Нет доступных секций.</li>}
              {availableSections.map((s) => (
                <li key={s.id} className="rounded-lg border p-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{s.name}</p>
                    {s.description && <p className="text-sm text-gray-600">{s.description}</p>}
                  </div>
                  <button
                    onClick={() => subscribe(s.id)}
                    disabled={!!busyIds[s.id]}
                    className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
                  >Записаться на секцию</button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
