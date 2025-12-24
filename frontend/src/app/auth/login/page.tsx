'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '../../../hooks/useAuth';
import { useToast } from '../../../components/ui/Toast';

export default function LoginPage() {
    const router = useRouter();
    const { login, isLoading, error, clearError } = useAuth();
    const toast = useToast();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();
        setIsSubmitting(true);

        try {
            await login(username, password);
            toast.success('Welcome back!');
            router.push('/game');
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Login failed');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
                    <p className="text-dark-400">Login to continue your challenge</p>
                </div>

                {/* Login Form */}
                <form onSubmit={handleSubmit} className="glass rounded-xl p-8 space-y-6">
                    {/* Username */}
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-dark-300 mb-2">
                            Username
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="input"
                            placeholder="Enter your username"
                            required
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Password */}
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-dark-300 mb-2">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input"
                            placeholder="Enter your password"
                            required
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="p-3 rounded-lg bg-red-500/20 border border-red-500 text-red-400 text-sm">
                            {error}
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isSubmitting || !username || !password}
                        className="btn btn-primary w-full"
                    >
                        {isSubmitting ? (
                            <>
                                <div className="spinner w-5 h-5" />
                                Logging in...
                            </>
                        ) : (
                            'Login'
                        )}
                    </button>

                    {/* Register Link */}
                    <p className="text-center text-dark-400">
                        Don't have an account?{' '}
                        <Link href="/auth/register" className="text-primary-400 hover:text-primary-300">
                            Register here
                        </Link>
                    </p>
                </form>
            </div>
        </div>
    );
}
