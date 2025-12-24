'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { leaderboardApi, LeaderboardEntry, LeaderboardResponse } from '@/services/api';

export default function LeaderboardPage() {
    const { isAuthenticated, user } = useAuth();
    const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchLeaderboard();

        // Refresh every 10 seconds
        const interval = setInterval(fetchLeaderboard, 10000);
        return () => clearInterval(interval);
    }, []);

    const fetchLeaderboard = async () => {
        try {
            const data = await leaderboardApi.getLeaderboard(100);
            setLeaderboard(data);
            setError(null);
        } catch (err: any) {
            setError('Failed to load leaderboard');
        } finally {
            setIsLoading(false);
        }
    };

    const getRankBadge = (rank: number) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    };

    const getLevelColor = (level: number) => {
        if (level >= 8) return 'text-red-500';
        if (level >= 6) return 'text-orange-400';
        if (level >= 4) return 'text-yellow-400';
        if (level >= 2) return 'text-emerald-400';
        return 'text-primary-400';
    };

    if (isLoading) {
        return (
            <div className="min-h-[calc(100vh-80px)] flex items-center justify-center">
                <div className="text-center">
                    <div className="spinner w-12 h-12 mx-auto mb-4" />
                    <p className="text-dark-400">Loading leaderboard...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[calc(100vh-80px)] py-8">
            <div className="container mx-auto px-4">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">🏆 Leaderboard</h1>
                        <p className="text-dark-400">
                            {leaderboard?.total_players || 0} players competing
                        </p>
                    </div>

                    {/* Stats Summary */}
                    <div className="grid grid-cols-3 gap-4 mb-8">
                        <div className="glass rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-primary-400">
                                {leaderboard?.total_players || 0}
                            </div>
                            <div className="text-xs text-dark-400">Total Players</div>
                        </div>
                        <div className="glass rounded-lg p-4 text-center">
                            <div className="text-2xl font-bold text-secondary-400">
                                {leaderboard?.max_level_reached || 1}
                            </div>
                            <div className="text-xs text-dark-400">Max Level Reached</div>
                        </div>
                        {isAuthenticated && leaderboard?.your_rank && (
                            <div className="glass rounded-lg p-4 text-center">
                                <div className="text-2xl font-bold text-emerald-400">
                                    #{leaderboard.your_rank}
                                </div>
                                <div className="text-xs text-dark-400">Your Rank</div>
                            </div>
                        )}
                    </div>

                    {error && (
                        <div className="p-4 rounded-lg bg-red-500/20 border border-red-500 text-red-400 text-center mb-8">
                            {error}
                        </div>
                    )}

                    {/* Leaderboard Table */}
                    <div className="glass rounded-xl overflow-hidden">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-dark-700">
                                    <th className="px-4 py-3 text-left text-xs font-medium text-dark-400 uppercase tracking-wider">
                                        Rank
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-dark-400 uppercase tracking-wider">
                                        Player
                                    </th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-dark-400 uppercase tracking-wider">
                                        Level
                                    </th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-dark-400 uppercase tracking-wider hidden sm:table-cell">
                                        Attempts
                                    </th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-dark-400 uppercase tracking-wider hidden md:table-cell">
                                        Success Rate
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-dark-700">
                                {leaderboard?.entries.map((entry) => (
                                    <tr
                                        key={entry.user_id}
                                        className={`transition-colors ${entry.is_current_user
                                                ? 'bg-primary-500/10'
                                                : 'hover:bg-dark-800/50'
                                            }`}
                                    >
                                        {/* Rank */}
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <span className={`text-lg ${entry.rank <= 3 ? 'font-bold' : ''}`}>
                                                {getRankBadge(entry.rank)}
                                            </span>
                                        </td>

                                        {/* Player */}
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <div className="flex items-center gap-2">
                                                <span className={`font-medium ${entry.is_current_user ? 'text-primary-400' : 'text-white'
                                                    }`}>
                                                    {entry.username}
                                                </span>
                                                {entry.is_current_user && (
                                                    <span className="text-xs text-primary-400">(you)</span>
                                                )}
                                            </div>
                                        </td>

                                        {/* Level */}
                                        <td className="px-4 py-4 whitespace-nowrap text-center">
                                            <span className={`font-bold ${getLevelColor(entry.highest_level_reached)}`}>
                                                {entry.highest_level_reached}
                                            </span>
                                        </td>

                                        {/* Attempts */}
                                        <td className="px-4 py-4 whitespace-nowrap text-center hidden sm:table-cell">
                                            <span className="text-dark-300">{entry.total_attempts}</span>
                                        </td>

                                        {/* Success Rate */}
                                        <td className="px-4 py-4 whitespace-nowrap text-center hidden md:table-cell">
                                            <span className="text-dark-300">{entry.success_rate.toFixed(1)}%</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {(!leaderboard?.entries || leaderboard.entries.length === 0) && (
                            <div className="py-12 text-center text-dark-400">
                                <p>No players yet. Be the first to join!</p>
                            </div>
                        )}
                    </div>

                    {/* Last Updated */}
                    <p className="text-center text-xs text-dark-500 mt-4">
                        Last updated: {new Date().toLocaleTimeString()}
                    </p>
                </div>
            </div>
        </div>
    );
}
