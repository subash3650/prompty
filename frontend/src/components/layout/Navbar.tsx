'use client';

import Link from 'next/link';
import { useAuth } from '../../hooks/useAuth';

export function Navbar() {
    const { isAuthenticated, user, logout, isLoading } = useAuth();

    return (
        <nav className="sticky top-0 z-50 glass border-b border-dark-700/50">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <span className="text-2xl">🧙‍♂️</span>
                        <span className="text-xl font-bold text-gradient">Prompty</span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center gap-6">
                        <Link href="/" className="text-dark-300 hover:text-white transition-colors">
                            Home
                        </Link>
                        {isAuthenticated && (
                            <Link href="/game" className="text-dark-300 hover:text-white transition-colors">
                                Play
                            </Link>
                        )}
                        <Link href="/leaderboard" className="text-dark-300 hover:text-white transition-colors">
                            Leaderboard
                        </Link>
                    </div>

                    {/* Auth Section */}
                    <div className="flex items-center gap-4">
                        {isLoading ? (
                            <div className="spinner" />
                        ) : isAuthenticated ? (
                            <>
                                {/* User Info */}
                                <div className="hidden sm:flex items-center gap-2 text-sm">
                                    <span className="text-dark-400">Level</span>
                                    <span className="text-primary-400 font-bold">{user?.current_level || 1}</span>
                                </div>

                                {/* User Menu */}
                                <div className="flex items-center gap-3">
                                    <Link
                                        href="/game"
                                        className="text-primary-400 hover:text-primary-300 font-medium"
                                    >
                                        {user?.username}
                                    </Link>
                                    <button
                                        onClick={() => logout()}
                                        className="text-dark-400 hover:text-white transition-colors text-sm"
                                    >
                                        Logout
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link href="/auth/login" className="text-dark-300 hover:text-white transition-colors">
                                    Login
                                </Link>
                                <Link href="/auth/register" className="btn btn-primary py-2 px-4 text-sm">
                                    Register
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
