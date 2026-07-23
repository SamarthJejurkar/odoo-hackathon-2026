import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

export default function Signup() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);
    try {
      await apiService.post('auth/register', {
        full_name: fullName,
        email,
        password,
      });

      // Registration succeeds but doesn't log you in automatically —
      // send the user to login to authenticate with their new credentials.
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-900 font-sans text-surface-900 dark:text-surface-300 px-4 selection:bg-brand-teal selection:text-white transition-colors duration-200">

      <div className="w-full max-w-md bg-white dark:bg-surface-800 rounded-xl shadow-lg dark:shadow-2xl relative overflow-hidden border border-surface-200 dark:border-surface-700 p-8 sm:p-10 transition-colors duration-200">

        <div className="flex items-center gap-3 mb-10">
          <div className="w-8 h-8 bg-brand-rust flex items-center justify-center text-white font-bold text-sm tracking-tighter rounded shadow-sm">
            AF
          </div>
          <span className="font-semibold text-xl text-surface-900 dark:text-white tracking-tight">AssetFlow</span>
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-semibold dark:font-medium tracking-tight text-surface-900 dark:text-white mb-2">
            Create your account
          </h2>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            Sign up to start managing your assets.
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
              Full Name
            </label>
            <input
              id="fullName"
              name="fullName"
              type="text"
              autoComplete="name"
              placeholder="Jane Doe"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="block w-full bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-700 focus:border-brand-teal focus:ring-1 focus:ring-brand-teal py-2.5 px-3 rounded-md text-sm text-surface-900 dark:text-white placeholder:text-surface-400 dark:placeholder:text-surface-600 transition-colors outline-none shadow-sm dark:shadow-none"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="name@company.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="block w-full bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-700 focus:border-brand-teal focus:ring-1 focus:ring-brand-teal py-2.5 px-3 rounded-md text-sm text-surface-900 dark:text-white placeholder:text-surface-400 dark:placeholder:text-surface-600 transition-colors outline-none shadow-sm dark:shadow-none"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              placeholder="At least 8 characters"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="block w-full bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-700 focus:border-brand-teal focus:ring-1 focus:ring-brand-teal py-2.5 px-3 rounded-md text-sm text-surface-900 dark:text-white placeholder:text-surface-400 dark:placeholder:text-surface-600 transition-colors outline-none shadow-sm dark:shadow-none"
            />
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brand-teal hover:bg-brand-teal-hover text-white py-2.5 px-4 rounded-md text-sm font-medium transition-colors shadow-sm disabled:opacity-60"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
        </form>

        <p className="mt-8 text-center text-sm text-surface-500 dark:text-surface-400">
          Already have an account?{' '}
          <Link to="/login" className="text-brand-teal hover:text-brand-teal-hover dark:hover:text-white font-medium transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}