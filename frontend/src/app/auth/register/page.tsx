'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/components/ui/Toast';

export default function RegisterPage() {
    const router = useRouter();
    const { register, isLoading, error, clearError } = useAuth();
    const toast = useToast();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [email, setEmail] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [validationError, setValidationError] = useState('');

    const validateForm = (): boolean => {
        if (username.length < 3) {
            setValidationError('Username must be at least 3 characters');
            return false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            setValidationError('Username can only contain letters, numbers, and underscores');
            return false;
        }
        if (password.length < 8) {
            setValidationError('Password must be at least 8 characters');
            return false;
        }
        if (password !== confirmPassword) {
            setValidationError('Passwords do not match');
            return false;
        }
        setValidationError('');
        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        clearError();

        if (!validateForm()) return;

        setIsSubmitting(true);

        try {
            await register(username, password, email || undefined);
            toast.success('Account created! Let the challenge begin!');
            router.push('/game');
        } catch (err: any) {
            toast.error(err.response?.data?.detail || 'Registration failed');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 py-8">
            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Join the Challenge</h1>
                    <p className="text-dark-400">Create your account to start playing</p>
                </div>

                {/* Register Form */}
                <form onSubmit={handleSubmit} className="glass rounded-xl p-8 space-y-6">
                    {/* Username */}
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-dark-300 mb-2">
                            Username *
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="input"
                            placeholder="Choose a username"
                            required
                            disabled={isSubmitting}
                            minLength={3}
                            maxLength={50}
                        />
                        <p className="text-xs text-dark-500 mt-1">
                            3-50 characters, letters, numbers, and underscores only
                        </p>
                    </div>

                    {/* Email (optional) */}
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium text-dark-300 mb-2">
                            Email (optional)
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="input"
                            placeholder="your@email.com"
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Password */}
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-dark-300 mb-2">
                            Password *
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input"
                            placeholder="Create a password"
                            required
                            disabled={isSubmitting}
                            minLength={8}
                        />
                        <p className="text-xs text-dark-500 mt-1">
                            Minimum 8 characters
                        </p>
                    </div>

                    {/* Confirm Password */}
                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-dark-300 mb-2">
                            Confirm Password *
                        </label>
                        <input
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            className="input"
                            placeholder="Confirm your password"
                            required
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Error Messages */}
                    {(validationError || error) && (
                        <div className="p-3 rounded-lg bg-red-500/20 border border-red-500 text-red-400 text-sm">
                            {validationError || error}
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isSubmitting || !username || !password || !confirmPassword}
                        className="btn btn-primary w-full"
                    >
                        {isSubmitting ? (
                            <>
                                <div className="spinner w-5 h-5" />
                                Creating account...
                            </>
                        ) : (
                            '🚀 Start Challenge'
                        )}
                    </button>

                    {/* Login Link */}
                    <p className="text-center text-dark-400">
                        Already have an account?{' '}
                        <Link href="/auth/login" className="text-primary-400 hover:text-primary-300">
                            Login here
                        </Link>
                    </p>
                </form>
            </div>
        </div>
    );
}
