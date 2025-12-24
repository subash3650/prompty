/**
 * Zustand store for authentication state.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi, User, LoginResponse } from '../services/api';
import { useGameStore } from './gameStore';

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;

    // Actions
    login: (username: string, password: string) => Promise<void>;
    register: (username: string, password: string, email?: string) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
    clearError: () => void;
    updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: true,
            error: null,

            login: async (username: string, password: string) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await authApi.login(username, password);
                    localStorage.setItem('token', response.access_token);

                    const user = await authApi.getMe();

                    set({
                        token: response.access_token,
                        user,
                        isAuthenticated: true,
                        isLoading: false,
                    });
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Login failed',
                        isLoading: false,
                    });
                    throw error;
                }
            },

            register: async (username: string, password: string, email?: string) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await authApi.register(username, password, email);
                    localStorage.setItem('token', response.access_token);

                    const user = await authApi.getMe();

                    set({
                        token: response.access_token,
                        user,
                        isAuthenticated: true,
                        isLoading: false,
                    });
                } catch (error: any) {
                    set({
                        error: error.response?.data?.detail || 'Registration failed',
                        isLoading: false,
                    });
                    throw error;
                }
            },

            logout: async () => {
                try {
                    await authApi.logout();
                } catch (error) {
                    // Continue with logout even if API call fails
                }
                localStorage.removeItem('token');

                // Clear game state
                useGameStore.getState().reset();

                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                    isLoading: false,
                });
            },

            checkAuth: async () => {
                const token = localStorage.getItem('token');
                if (!token) {
                    set({ isLoading: false, isAuthenticated: false });
                    return;
                }

                try {
                    const user = await authApi.getMe();
                    set({
                        user,
                        token,
                        isAuthenticated: true,
                        isLoading: false,
                    });
                } catch (error) {
                    localStorage.removeItem('token');
                    set({
                        user: null,
                        token: null,
                        isAuthenticated: false,
                        isLoading: false,
                    });
                }
            },

            clearError: () => set({ error: null }),

            updateUser: (updates: Partial<User>) => {
                const currentUser = get().user;
                if (currentUser) {
                    set({ user: { ...currentUser, ...updates } });
                }
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ token: state.token }),
        }
    )
);
