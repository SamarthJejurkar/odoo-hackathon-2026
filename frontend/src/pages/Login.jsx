import React from 'react';
import { Link } from 'react-router-dom';

export default function Login() {
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
            Sign in
          </h2>
          <p className="text-sm text-surface-500 dark:text-surface-400">
            Welcome back. Please enter your details.
          </p>
        </div>

        <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
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
              className="block w-full bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-700 focus:border-brand-teal focus:ring-1 focus:ring-brand-teal py-2.5 px-3 rounded-md text-sm text-surface-900 dark:text-white placeholder:text-surface-400 dark:placeholder:text-surface-600 transition-colors outline-none shadow-sm dark:shadow-none"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="password" className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                Password
              </label>
              <a href="#" className="text-xs font-medium text-brand-teal hover:text-brand-teal-hover dark:hover:text-white transition-colors">
                Forgot password?
              </a>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              required
              className="block w-full bg-white dark:bg-surface-900 border border-surface-300 dark:border-surface-700 focus:border-brand-teal focus:ring-1 focus:ring-brand-teal py-2.5 px-3 rounded-md text-sm text-surface-900 dark:text-white placeholder:text-surface-400 dark:placeholder:text-surface-600 transition-colors outline-none shadow-sm dark:shadow-none"
            />
          </div>

          <div className="pt-4">
            <button
              type="submit"
              className="w-full bg-brand-teal hover:bg-brand-teal-hover text-white py-2.5 px-4 rounded-md text-sm font-medium transition-colors shadow-sm"
            >
              Sign in
            </button>
          </div>
        </form>

        <p className="mt-8 text-center text-sm text-surface-500 dark:text-surface-400">
          Don't have an account?{' '}
          <Link to="/signup" className="text-brand-teal hover:text-brand-teal-hover dark:hover:text-white font-medium transition-colors">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}