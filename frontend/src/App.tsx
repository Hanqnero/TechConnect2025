import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import LoginForm from './components/LoginForm';
import Main from './pages/Main';
import Profile from './pages/Profile';
import MarkAttendance from './pages/MarkAttendance';
import TeacherProfile from './pages/TeacherProfile';
import SectionEdit from './pages/SectionEdit';

function LoginPage() {
  const navigate = useNavigate();
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/auth/me', { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          if (data?.authenticated) {
            navigate('/', { replace: true });
          }
        }
      } catch {}
    })();
  }, [navigate]);

  return (
    <div className="min-h-dvh bg-gradient-to-b from-indigo-50 to-white flex items-center justify-center p-4 relative">
      <header className="absolute top-0 left-0 right-0 px-4 py-3 sm:px-6">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-lg text-xl font-semibold text-gray-900">ЮУрГУ ❤ Спорт</h1>
          <h2 className="text-lg text-gray-400">TechConnect 2025 Hackathon</h2>
        </div>
      </header>
      <div className="w-full flex flex-col items-center gap-6">
        <img src="../assets/susu-logo.png" alt="ЮУрГУ Спорт" className="w-4/5 max-w-3xl mx-auto" />
        <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-semibold text-gray-900">С возвращением</h1>
          <p className="text-gray-500 text-sm">Войдите, чтобы продолжить</p>
        </div>
        <LoginForm />
        </div>
      </div>
    </div>
  );
}

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/auth/me', { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          setAuthenticated(!!data?.authenticated);
        } else {
          setAuthenticated(false);
        }
      } catch {
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="min-h-dvh flex items-center justify-center text-gray-600">
        Проверка сессии…
      </div>
    );
  }
  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<ProtectedRoute><Main /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
  <Route path="/teacher/profile" element={<ProtectedRoute><TeacherProfile /></ProtectedRoute>} />
  <Route path="/teacher/sections/:id/edit" element={<ProtectedRoute><SectionEdit /></ProtectedRoute>} />
      <Route path="/classes/:id/mark" element={<ProtectedRoute><MarkAttendance /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
