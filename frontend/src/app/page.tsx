'use client';

import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export default function HomePage() {
    const { isAuthenticated, user } = useAuth();

    return (
        <div className="min-h-[calc(100vh-80px)]">
            {/* Hero Section */}
            <section className="relative py-20 overflow-hidden">
                {/* Background gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary-900/20 via-dark-900 to-secondary-900/20" />
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary-500/10 via-transparent to-transparent" />

                <div className="container mx-auto px-4 relative z-10">
                    <div className="max-w-4xl mx-auto text-center">
                        {/* Logo/Title */}
                        <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-fade-in">
                            <span className="text-gradient">Prompty</span>{' '}
                            <span className="text-white">Challenge</span>
                        </h1>

                        {/* Subtitle */}
                        <p className="text-xl md:text-2xl text-dark-300 mb-8 animate-slide-up">
                            Can you extract the secret password from <span className="text-secondary-400 font-semibold">Gandalf</span>?
                        </p>

                        {/* Description */}
                        <p className="text-dark-400 max-w-2xl mx-auto mb-12">
                            A real-time competitive prompt injection challenge. Battle through 8 increasingly difficult levels,
                            outsmart the AI defenses, and climb the leaderboard. The first to reach the top wins!
                        </p>

                        {/* CTA Buttons */}
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            {isAuthenticated ? (
                                <>
                                    <Link href="/game" className="btn btn-primary text-lg px-8 py-4">
                                        🎮 Continue Playing
                                    </Link>
                                    <Link href="/leaderboard" className="btn btn-outline text-lg px-8 py-4">
                                        📊 View Leaderboard
                                    </Link>
                                </>
                            ) : (
                                <>
                                    <Link href="/auth/register" className="btn btn-primary text-lg px-8 py-4">
                                        🚀 Start Challenge
                                    </Link>
                                    <Link href="/auth/login" className="btn btn-outline text-lg px-8 py-4">
                                        🔑 Login
                                    </Link>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-20 bg-dark-800/30">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold text-center mb-12 text-white">
                        How It Works
                    </h2>

                    <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {/* Feature 1 */}
                        <div className="glass rounded-xl p-6 card-hover">
                            <div className="w-12 h-12 bg-primary-500/20 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">🧙‍♂️</span>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 text-white">Meet Gandalf</h3>
                            <p className="text-dark-400">
                                Gandalf guards a secret password. Your mission: craft clever prompts to extract it without triggering his defenses.
                            </p>
                        </div>

                        {/* Feature 2 */}
                        <div className="glass rounded-xl p-6 card-hover">
                            <div className="w-12 h-12 bg-secondary-500/20 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">🛡️</span>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 text-white">8 Levels of Defense</h3>
                            <p className="text-dark-400">
                                Each level adds new security measures. From no defense to adaptive AI guards that learn from your attempts.
                            </p>
                        </div>

                        {/* Feature 3 */}
                        <div className="glass rounded-xl p-6 card-hover">
                            <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">🏆</span>
                            </div>
                            <h3 className="text-xl font-semibold mb-2 text-white">Compete in Real-Time</h3>
                            <p className="text-dark-400">
                                Race against other players. The leaderboard updates live. First to the highest level with the fastest time wins!
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Level Preview */}
            <section className="py-20">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold text-center mb-12 text-white">
                        The 8 Levels
                    </h2>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
                        {[
                            { level: 1, name: 'No Defense', stars: 1 },
                            { level: 2, name: 'System Prompt', stars: 2 },
                            { level: 3, name: 'Exact Filter', stars: 3 },
                            { level: 4, name: 'Semantic Filter', stars: 4 },
                            { level: 5, name: 'Intent Classifier', stars: 4 },
                            { level: 6, name: 'Deep Analysis', stars: 5 },
                            { level: 7, name: 'Combined Guards', stars: 5 },
                            { level: 8, name: 'Adaptive AI', stars: 6 },
                        ].map(({ level, name, stars }) => (
                            <div
                                key={level}
                                className={`glass rounded-lg p-4 text-center card-hover level-${level}`}
                            >
                                <div className="text-3xl font-bold mb-1">{level}</div>
                                <div className="text-sm text-dark-400 mb-2">{name}</div>
                                <div className="text-yellow-400">
                                    {'⭐'.repeat(Math.min(stars, 5))}
                                    {stars > 5 && '🔥'}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Leaderboard Preview */}
            {isAuthenticated && user && (
                <section className="py-12 bg-dark-800/30">
                    <div className="container mx-auto px-4 text-center">
                        <div className="glass rounded-xl p-8 max-w-md mx-auto">
                            <h3 className="text-xl font-semibold mb-4">Your Progress</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="text-3xl font-bold text-primary-400">{user.current_level || 1}</div>
                                    <div className="text-sm text-dark-400">Current Level</div>
                                </div>
                                <div>
                                    <div className="text-3xl font-bold text-secondary-400">{user.total_attempts || 0}</div>
                                    <div className="text-sm text-dark-400">Total Attempts</div>
                                </div>
                            </div>
                            <Link href="/game" className="btn btn-primary w-full mt-6">
                                Continue Playing →
                            </Link>
                        </div>
                    </div>
                </section>
            )}
        </div>
    );
}
