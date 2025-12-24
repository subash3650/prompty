/**
 * Zustand store for game state.
 */

import { create } from 'zustand';
import { gameApi, GameStatus, PromptResponse, LevelInfo } from '../services/api';

interface Attempt {
    id: string;
    prompt: string;
    response: string;
    success: boolean;
    timestamp: Date;
}

interface PasswordResponse {
    success: boolean;
    message: string;
    current_level: number;
    is_finished: boolean;
}

interface GameState {
    // Current state
    currentLevel: number;
    highestLevel: number;
    totalAttempts: number;
    successfulAttempts: number;
    levelInfo: LevelInfo | null;

    // UI state
    isLoading: boolean;
    isSubmitting: boolean;
    isSubmittingPassword: boolean;
    error: string | null;
    lastResponse: PromptResponse | null;
    lastPasswordResponse: PasswordResponse | null;

    // History
    recentAttempts: Attempt[];

    // Actions
    fetchGameStatus: () => Promise<void>;
    submitPrompt: (prompt: string) => Promise<PromptResponse>;
    submitPassword: (password: string) => Promise<PasswordResponse>;
    clearLastResponse: () => void;
    clearError: () => void;
    reset: () => void;
}

export const useGameStore = create<GameState>((set, get) => ({
    currentLevel: 1,
    highestLevel: 1,
    totalAttempts: 0,
    successfulAttempts: 0,
    levelInfo: null,

    isLoading: true,
    isSubmitting: false,
    isSubmittingPassword: false,
    error: null,
    lastResponse: null,
    lastPasswordResponse: null,

    recentAttempts: [],

    fetchGameStatus: async () => {
        set({ isLoading: true, error: null });
        try {
            const status = await gameApi.getStatus();
            set({
                currentLevel: status.current_level,
                highestLevel: status.highest_level_reached,
                totalAttempts: status.total_attempts,
                successfulAttempts: status.successful_attempts,
                levelInfo: status.level_info || null,
                isLoading: false,
            });
        } catch (error: any) {
            set({
                error: error.response?.data?.detail || 'Failed to fetch game status',
                isLoading: false,
            });
        }
    },

    submitPrompt: async (prompt: string) => {
        const currentLevel = get().currentLevel;
        set({ isSubmitting: true, error: null });

        try {
            const response = await gameApi.submitPrompt(prompt, currentLevel);

            // Add to recent attempts
            const newAttempt: Attempt = {
                id: Date.now().toString(),
                prompt,
                response: response.response,
                success: response.success,
                timestamp: new Date(),
            };

            set((state) => ({
                isSubmitting: false,
                lastResponse: response,
                currentLevel: response.current_level,
                highestLevel: Math.max(state.highestLevel, response.current_level - (response.success ? 1 : 0)),
                totalAttempts: state.totalAttempts + 1,
                successfulAttempts: state.successfulAttempts + (response.success ? 1 : 0),
                recentAttempts: [newAttempt, ...state.recentAttempts.slice(0, 9)],
            }));

            // Refresh level info if level changed
            if (response.success) {
                const levelInfo = await gameApi.getLevelInfo(response.current_level);
                set({ levelInfo });
            }

            return response;
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || 'Failed to submit prompt';
            set({
                error: errorMessage,
                isSubmitting: false,
            });
            throw error;
        }
    },

    submitPassword: async (password: string) => {
        const currentLevel = get().currentLevel;
        // Clear previous response to avoid stale state
        set({ isSubmittingPassword: true, error: null, lastPasswordResponse: null });

        try {
            const response = await gameApi.submitPassword(password, currentLevel);

            set((state) => ({
                isSubmittingPassword: false,
                lastPasswordResponse: response,
                currentLevel: response.current_level,
                highestLevel: Math.max(state.highestLevel, response.current_level),
                successfulAttempts: response.success ? state.successfulAttempts + 1 : state.successfulAttempts,
            }));

            // Refresh level info if level changed
            if (response.success && !response.is_finished) {
                const levelInfo = await gameApi.getLevelInfo(response.current_level);
                set({ levelInfo });
            }

            return response;
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || 'Failed to submit password';
            set({
                error: errorMessage,
                isSubmittingPassword: false,
            });
            throw error;
        }
    },

    clearLastResponse: () => set({ lastResponse: null, lastPasswordResponse: null }),
    clearError: () => set({ error: null }),
    reset: () => set({
        currentLevel: 1,
        highestLevel: 1,
        totalAttempts: 0,
        successfulAttempts: 0,
        levelInfo: null,
        isLoading: true,
        isSubmitting: false,
        isSubmittingPassword: false,
        error: null,
        lastResponse: null,
        lastPasswordResponse: null,
        recentAttempts: [],
    }),
}));
