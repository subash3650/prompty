/**
 * API client for the Prompty Challenge backend.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

// Create axios instance
const api: AxiosInstance = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true,
});

// Request interceptor - add auth token
api.interceptors.request.use(
    (config) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            if (typeof window !== 'undefined') {
                localStorage.removeItem('token');
                window.location.href = '/auth/login';
            }
        }
        return Promise.reject(error);
    }
);

// Types
export interface User {
    id: string;
    username: string;
    email?: string;
    current_level: number;
    highest_level_reached: number;
    total_attempts: number;
    successful_attempts: number;
    success_rate: number;
    is_admin: boolean;
    is_finished: boolean;
    created_at: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user_id: string;
    username: string;
    current_level: number;
    is_admin: boolean;
}

export interface PromptResponse {
    success: boolean;
    response: string;
    reason?: string;
    current_level: number;
    ai_latency_ms?: number;
    message: string;
    attempt_number?: number;
    input_guard_triggered: boolean;
    output_guard_triggered: boolean;
}

export interface GameStatus {
    user_id: string;
    username: string;
    current_level: number;
    highest_level_reached: number;
    total_attempts: number;
    successful_attempts: number;
    success_rate: number;
    is_finished: boolean;
    level_info?: LevelInfo;
    rank?: number;
}

export interface LevelInfo {
    level_number: number;
    defense_description: string;
    hint?: string;
    difficulty_rating: number;
    total_attempts_made: number;
    success_rate: number;
    input_guard_type: string;
    output_guard_type: string;
}

export interface LeaderboardEntry {
    rank: number;
    user_id: string;
    username: string;
    highest_level_reached: number;
    completion_time?: string;
    total_attempts: number;
    successful_attempts: number;
    success_rate: number;
    is_current_user: boolean;
}

export interface LeaderboardResponse {
    entries: LeaderboardEntry[];
    total_players: number;
    max_level_reached: number;
    your_rank?: number;
    last_updated: string;
}

// Auth API
export const authApi = {
    register: async (username: string, password: string, email?: string): Promise<LoginResponse> => {
        const { data } = await api.post<LoginResponse>('/auth/register', { username, password, email });
        return data;
    },

    login: async (username: string, password: string): Promise<LoginResponse> => {
        const { data } = await api.post<LoginResponse>('/auth/login', { username, password });
        return data;
    },

    logout: async (): Promise<void> => {
        await api.post('/auth/logout');
    },

    getMe: async (): Promise<User> => {
        const { data } = await api.get<User>('/auth/me');
        return data;
    },
};

// Game API
export const gameApi = {
    getStatus: async (): Promise<GameStatus> => {
        const { data } = await api.get<GameStatus>('/game/status');
        return data;
    },

    submitPrompt: async (prompt: string, level: number): Promise<PromptResponse> => {
        const { data } = await api.post<PromptResponse>('/game/submit-prompt', { prompt, level });
        return data;
    },

    submitPassword: async (password: string, level: number): Promise<{
        success: boolean;
        message: string;
        current_level: number;
        is_finished: boolean;
    }> => {
        const { data } = await api.post('/game/submit-password', { password, level });
        return data;
    },

    getLevelInfo: async (levelNumber: number): Promise<LevelInfo> => {
        const { data } = await api.get<LevelInfo>(`/game/levels/${levelNumber}`);
        return data;
    },

    getAttempts: async (level?: number, page: number = 1, perPage: number = 20) => {
        const params = new URLSearchParams();
        if (level) params.append('level', level.toString());
        params.append('page', page.toString());
        params.append('per_page', perPage.toString());

        const { data } = await api.get(`/game/attempts?${params}`);
        return data;
    },
};

// Leaderboard API
export const leaderboardApi = {
    getLeaderboard: async (limit: number = 100): Promise<LeaderboardResponse> => {
        const { data } = await api.get<LeaderboardResponse>(`/leaderboard?limit=${limit}`);
        return data;
    },

    getMyRank: async () => {
        const { data } = await api.get('/leaderboard/my-rank');
        return data;
    },
};

// User API
export const userApi = {
    getProfile: async (): Promise<User> => {
        const { data } = await api.get<User>('/users/me');
        return data;
    },

    getStats: async () => {
        const { data } = await api.get('/users/me/stats');
        return data;
    },
};

export default api;
