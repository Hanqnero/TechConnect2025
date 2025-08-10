import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { ChangeEvent, FormEvent } from 'react';


type LoginFormState = {
  login: string;
  password: string;
  remember: boolean;
};

function validate(form: LoginFormState) {
  const errors: Partial<Record<keyof LoginFormState, string>> = {};
  if (!form.login) errors.login = 'Укажите логин';
  else if (form.login.length < 3) errors.login = 'Минимум 3 символа';
  if (!form.password) errors.password = 'Укажите пароль';
  else if (form.password.length < 8) errors.password = 'Минимум 8 символов';
  return errors;
}

export default function LoginForm() {
  const navigate = useNavigate();
  const [form, setForm] = useState<LoginFormState>({ login: '', password: '', remember: false });
  const [errors, setErrors] = useState<Partial<Record<keyof LoginFormState, string>>>({});
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    const savedLogin = localStorage.getItem('tc.login');
    if (savedLogin) {
      setForm((f: LoginFormState) => ({ ...f, login: savedLogin, remember: true }));
    }
  }, []);

  function onChange<K extends keyof LoginFormState>(key: K, value: LoginFormState[K]) {
    setForm((f: LoginFormState) => ({ ...f, [key]: value }));
    const v = validate({ ...form, [key]: value });
    setErrors((e: Partial<Record<keyof LoginFormState, string>>) => ({ ...e, [key]: v[key] }));
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const v = validate(form);
    setErrors(v);
    setMessage(null);
    if (Object.keys(v).length) return;
    setSubmitting(true);
    try {
      // Never store raw passwords. Send over HTTPS to your backend.
      // Tokens should be issued into httpOnly, secure cookies by the server.
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // receive/set httpOnly cookie
        body: JSON.stringify({ login: form.login, password: form.password, remember: form.remember })
      });

      if (!res.ok) {
        let detail = 'Не удалось войти. Проверьте логин/пароль.';
        try {
          const data = await res.json();
          if (data?.detail) detail = Array.isArray(data.detail) ? data.detail.map((d: any) => d.msg || d).join(', ') : String(data.detail);
        } catch {}
        throw new Error(detail);
      }

      if (form.remember) localStorage.setItem('tc.login', form.login);
      else localStorage.removeItem('tc.login');

      // Verify session and greet user
      const meRes = await fetch('/auth/me', { credentials: 'include' });
      if (meRes.ok) {
        const me = await meRes.json();
        if (me?.authenticated) {
          // Redirect to main screen after successful login
          navigate('/', { replace: true });
          return;
        }
      }
      setMessage('Вход выполнен.');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Не удалось войти. Попробуйте ещё раз.';
      setMessage(msg);
    } finally {
      setSubmitting(false);
      // Clear the password from memory quickly after submit
      setForm((f: LoginFormState) => ({ ...f, password: '' }));
    }
  }

  const isValid = !Object.keys(validate(form)).length;

  return (
    <form onSubmit={onSubmit} className="rounded-2xl bg-white p-4 sm:p-6 shadow-sm ring-1 ring-gray-900/5">
      <div className="space-y-4">
        <div>
          <label htmlFor="login" className="block text-sm font-medium text-gray-800">Логин</label>
          <input
            id="login"
            name="login"
            type="text"
            inputMode="text"
            autoComplete="username"
            className="mt-2 block w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="ваш логин"
            value={form.login}
            onChange={(e: ChangeEvent<HTMLInputElement>) => onChange('login', e.target.value)}
            aria-invalid={!!errors.login}
            aria-describedby={errors.login ? 'login-error' : undefined}
          />
          {errors.login && (
            <p id="login-error" className="mt-2 text-sm text-red-600">{errors.login}</p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-800">Пароль</label>
          <div className="mt-2 relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              className="block w-full rounded-lg border border-gray-300 bg-white px-3 py-3 pr-12 text-base text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="••••••••"
              value={form.password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => onChange('password', e.target.value)}
              aria-invalid={!!errors.password}
              aria-describedby={errors.password ? 'password-error' : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword((s) => !s)}
              className="absolute inset-y-0 right-2 my-1 inline-flex items-center rounded-md px-2 text-sm font-medium text-gray-600 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}
              aria-pressed={showPassword}
            >
              {showPassword ? 'Скрыть' : 'Показать'}
            </button>
          </div>
          {errors.password && (
            <p id="password-error" className="mt-2 text-sm text-red-600">{errors.password}</p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <label className="inline-flex items-center gap-3">
            <input
              id="remember"
              name="remember"
              type="checkbox"
              className="h-5 w-5 accent-indigo-600"
              checked={form.remember}
              onChange={(e: ChangeEvent<HTMLInputElement>) => onChange('remember', e.target.checked)}
            />
            <span className="text-sm text-gray-700">Запомнить меня на этом устройстве</span>
          </label>
          <a className="text-sm font-medium text-indigo-600 hover:text-indigo-700 active:text-indigo-800" href="#" onClick={(e) => e.preventDefault()}>
            Забыли пароль?
          </a>
        </div>

        {message && (
          <p role="status" aria-live="polite" className="text-sm text-gray-600">{message}</p>
        )}

        <button
          type="submit"
          disabled={submitting || !isValid}
          className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 text-base font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting && (
            <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
          )}
          Войти
        </button>
      </div>
    </form>
  );
}
