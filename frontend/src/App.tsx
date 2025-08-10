import LoginForm from './components/LoginForm';

export default function App() {
  return (
    <div className="min-h-dvh bg-gradient-to-b from-indigo-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-2 h-12 w-12 rounded-xl bg-indigo-600/10 flex items-center justify-center">
            <span className="text-xl font-semibold text-indigo-600">TC</span>
          </div>
          <h1 className="text-xl font-semibold text-gray-900">Welcome back</h1>
          <p className="text-gray-500 text-sm">Sign in to continue</p>
        </div>
        <LoginForm />
        <p className="mt-6 text-xs text-center text-gray-500">
          By continuing you agree to our Terms and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
