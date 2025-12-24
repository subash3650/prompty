/**
 * Custom hook for authentication.
 */

import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

export function useAuth() {
    const {
        user,
        token,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        checkAuth,
        clearError,
        updateUser,
    } = useAuthStore();

    useEffect(() => {
        checkAuth();
    }, []);

    return {
        user,
        token,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        checkAuth,
        clearError,
        updateUser,
    };
}
