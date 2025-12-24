/**
 * Custom hook for game state.
 */

import { useEffect } from 'react';
import { useGameStore } from '@/store/gameStore';

export function useGame() {
    const {
        currentLevel,
        highestLevel,
        totalAttempts,
        successfulAttempts,
        levelInfo,
        isLoading,
        isSubmitting,
        isSubmittingPassword,
        error,
        lastResponse,
        lastPasswordResponse,
        recentAttempts,
        fetchGameStatus,
        submitPrompt,
        submitPassword,
        clearLastResponse,
        clearError,
    } = useGameStore();

    useEffect(() => {
        fetchGameStatus();
    }, []);

    const successRate = totalAttempts > 0
        ? ((successfulAttempts / totalAttempts) * 100).toFixed(1)
        : '0.0';

    return {
        currentLevel,
        highestLevel,
        totalAttempts,
        successfulAttempts,
        successRate,
        levelInfo,
        isLoading,
        isSubmitting,
        isSubmittingPassword,
        error,
        lastResponse,
        lastPasswordResponse,
        recentAttempts,
        fetchGameStatus,
        submitPrompt,
        submitPassword,
        clearLastResponse,
        clearError,
    };
}
