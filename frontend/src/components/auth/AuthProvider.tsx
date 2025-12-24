'use client';

import { createContext, useContext, useEffect, ReactNode } from 'react';
import { useAuthStore } from '../../store/authStore';

const AuthContext = createContext<null>(null);

interface AuthProviderProps {
    children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
    const checkAuth = useAuthStore((state) => state.checkAuth);

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    return (
        <AuthContext.Provider value={null}>
            {children}
        </AuthContext.Provider>
    );
}
