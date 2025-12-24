'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import { useGame } from '../../hooks/useGame';
import { useToast } from '../../components/ui/Toast';
import confetti from 'canvas-confetti';

export default function GamePage() {
    const router = useRouter();
    const { isAuthenticated, isLoading: authLoading, user, updateUser } = useAuth();
    const {
        currentLevel,
        highestLevel,
        totalAttempts,
        successRate,
        levelInfo,
        isLoading,
        isSubmitting,
        isSubmittingPassword,
        lastResponse,
        lastPasswordResponse,
        submitPrompt,
        submitPassword,
        fetchGameStatus,
        clearLastResponse,
    } = useGame();
    const toast = useToast();

    const [prompt, setPrompt] = useState('');
    const [passwordGuess, setPasswordGuess] = useState('');

    // Redirect if not authenticated
    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/auth/login');
        }
    }, [authLoading, isAuthenticated, router]);

    // Handle prompt submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim() || isSubmitting) return;

        try {
            const response = await submitPrompt(prompt.trim());
            if (response.success) {
                toast.success(response.message);
            } else if (response.input_guard_triggered || response.output_guard_triggered) {
                toast.warning(response.message);
            }
            setPrompt('');
        } catch (err: any) {
            toast.error(err.message || 'Failed to submit prompt');
        }
    };

    // Handle password submission
    const handlePasswordSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!passwordGuess.trim() || isSubmittingPassword) return;

        try {
            const response = await submitPassword(passwordGuess.trim());
            if (response.success) {
                toast.success(response.message);
                setPasswordGuess('');
                // Celebration!
                confetti({
                    particleCount: 150,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#10B981', '#3B82F6', '#F59E0B'] // Emerald, Blue, Amber
                });

                // Clear old responses and refresh game status
                clearLastResponse();
                fetchGameStatus();

                // FORCE Update Navbar User State
                if (user) {
                    updateUser({ ...user, current_level: response.current_level });
                }
            } else {
                toast.error(response.message);
            }
        } catch (err: any) {
            toast.error(err.message || 'Failed to verify password');
        }
    };

    if (authLoading || isLoading) {
        return (
            <div className="min-h-[calc(100vh-80px)] flex items-center justify-center">
                <div className="text-center">
                    <div className="spinner w-12 h-12 mx-auto mb-4" />
                    <p className="text-dark-400">Loading game...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return null;
    }

    const isFinished = currentLevel > 8;

    return (
        <div className="min-h-[calc(100vh-80px)] py-8">
            <div className="container mx-auto px-4">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">
                            {isFinished ? '🏆 Challenge Complete!' : `Level ${currentLevel}`}
                        </h1>
                        {levelInfo && !isFinished && (
                            <p className="text-dark-400">{levelInfo.defense_description}</p>
                        )}
                    </div>

                    {/* Stats Bar */}
                    <div className="grid grid-cols-4 gap-4 mb-8">
                        <div className="glass rounded-lg p-4 text-center">
                            <div className={`text-2xl font-bold level-${currentLevel}`}>
                                {isFinished ? '✓' : currentLevel}
                            </div>
                            <div className="text-xs text-dark-400">Current Level</div>
                        </div>
                        <div className="glass rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-secondary-400">{highestLevel}</div>
                            <div className="text-xs text-dark-400">Highest Level</div>
                        </div>
                        <div className="glass rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-primary-400">{totalAttempts}</div>
                            <div className="text-xs text-dark-400">Total Attempts</div>
                        </div>
                        <div className="glass rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-emerald-400">{successRate}%</div>
                            <div className="text-xs text-dark-400">Success Rate</div>
                        </div>
                    </div>

                    {/* Level Progress */}
                    <div className="mb-8">
                        <div className="flex justify-between text-sm text-dark-400 mb-2">
                            <span>Progress</span>
                            <span>{Math.min(currentLevel - 1, 8)}/8 Levels</span>
                        </div>
                        <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 transition-all duration-500"
                                style={{ width: `${Math.min((currentLevel - 1) / 8 * 100, 100)}%` }}
                            />
                        </div>
                    </div>

                    {/* Main Game Area */}
                    {isFinished ? (
                        <div className="glass rounded-xl p-8 text-center">
                            <div className="text-6xl mb-4">🎉</div>
                            <h2 className="text-2xl font-bold text-white mb-4">
                                Congratulations, {user?.username}!
                            </h2>
                            <p className="text-dark-400 mb-6">
                                You have completed all 8 levels of the Prompty Challenge!
                            </p>
                            <button
                                onClick={() => router.push('/leaderboard')}
                                className="btn btn-primary"
                            >
                                View Leaderboard
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="grid lg:grid-cols-2 gap-6">
                                {/* Prompt Input */}
                                <div className="glass rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                        <span>🧙‍♂️</span> Talk to Prompty
                                    </h3>

                                    {levelInfo?.hint && (
                                        <div className="p-3 rounded-lg bg-secondary-500/10 border border-secondary-500/30 text-secondary-400 text-sm mb-4">
                                            💡 Hint: {levelInfo.hint}
                                        </div>
                                    )}

                                    <form onSubmit={handleSubmit}>
                                        <textarea
                                            value={prompt}
                                            onChange={(e) => setPrompt(e.target.value)}
                                            placeholder="Enter your prompt to try to extract the password..."
                                            className="textarea h-36 mb-4"
                                            disabled={isSubmitting}
                                            maxLength={5000}
                                        />
                                        <div className="flex justify-between items-center">
                                            <span className="text-xs text-dark-500">
                                                {prompt.length}/5000 characters
                                            </span>
                                            <button
                                                type="submit"
                                                disabled={isSubmitting || !prompt.trim()}
                                                className="btn btn-primary"
                                            >
                                                {isSubmitting ? (
                                                    <>
                                                        <div className="spinner w-5 h-5" />
                                                        Sending...
                                                    </>
                                                ) : (
                                                    '✨ Send Prompt'
                                                )}
                                            </button>
                                        </div>
                                    </form>
                                </div>

                                {/* Response Display */}
                                <div className="glass rounded-xl p-6">
                                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                        <span>💬</span> Prompty's Response
                                    </h3>

                                    {lastResponse ? (
                                        <div className="space-y-4">
                                            {/* Success/Failure Badge */}
                                            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm ${lastResponse.success
                                                ? 'bg-emerald-500/20 text-emerald-400'
                                                : lastResponse.input_guard_triggered || lastResponse.output_guard_triggered
                                                    ? 'bg-yellow-500/20 text-yellow-400'
                                                    : 'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {lastResponse.success ? '✓ Level Passed!' :
                                                    lastResponse.input_guard_triggered ? '🛡️ Blocked' :
                                                        lastResponse.output_guard_triggered ? '🛡️ Filtered' : '📝 Response received'}
                                            </div>

                                            {/* Response Text */}
                                            <div className="p-4 rounded-lg bg-dark-800 border border-dark-600">
                                                <p className="text-dark-200 whitespace-pre-wrap">{lastResponse.response}</p>
                                            </div>

                                            {/* Guard Info */}
                                            {lastResponse.reason && (
                                                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-sm">
                                                    ⚠️ {lastResponse.reason}
                                                </div>
                                            )}

                                            {/* Latency */}
                                            {lastResponse.ai_latency_ms && (
                                                <p className="text-xs text-dark-500">
                                                    Response time: {lastResponse.ai_latency_ms}ms
                                                </p>
                                            )}
                                        </div>
                                    ) : (
                                        <div className="h-48 flex items-center justify-center text-dark-500">
                                            <p>Prompty awaits your prompt...</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Password Submission Section */}
                            <div className="glass rounded-xl p-6">
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    <span>🔐</span> Submit Password
                                </h3>
                                <p className="text-dark-400 text-sm mb-4">
                                    Did you extract the password from Prompty? Enter it below to advance to the next level!
                                </p>
                                <form onSubmit={handlePasswordSubmit} className="flex gap-4">
                                    <input
                                        type="text"
                                        value={passwordGuess}
                                        onChange={(e) => setPasswordGuess(e.target.value)}
                                        placeholder="Enter the password you found..."
                                        className="input flex-1"
                                        disabled={isSubmittingPassword}
                                        maxLength={100}
                                    />
                                    <button
                                        type="submit"
                                        disabled={isSubmittingPassword || !passwordGuess.trim()}
                                        className="btn btn-secondary"
                                    >
                                        {isSubmittingPassword ? (
                                            <>
                                                <div className="spinner w-5 h-5" />
                                                Checking...
                                            </>
                                        ) : (
                                            '🔓 Verify Password'
                                        )}
                                    </button>
                                </form>

                                {/* Password Response */}
                                {lastPasswordResponse && (
                                    <div className={`mt-4 p-3 rounded-lg ${lastPasswordResponse.success
                                        ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400'
                                        : 'bg-red-500/20 border border-red-500/30 text-red-400'
                                        }`}>
                                        {lastPasswordResponse.message}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Level Info */}
                    {levelInfo && !isFinished && (
                        <div className="mt-8 glass rounded-xl p-6">
                            <h3 className="text-lg font-semibold text-white mb-4">Level Information</h3>
                            <div className="grid md:grid-cols-3 gap-4 text-sm">
                                <div>
                                    <span className="text-dark-400">Difficulty:</span>{' '}
                                    <span className="text-yellow-400">
                                        {'⭐'.repeat(levelInfo.difficulty_rating)}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-dark-400">Input Guard:</span>{' '}
                                    <span className="text-primary-400">{levelInfo.input_guard_type}</span>
                                </div>
                                <div>
                                    <span className="text-dark-400">Output Guard:</span>{' '}
                                    <span className="text-secondary-400">{levelInfo.output_guard_type}</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
