'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/lib/api-client';

interface AuthContextType {
    token: string | null;
    user: { id: number; role: string } | null;
    login: (email: string, password: string, organization_slug?: string) => Promise<{ ok: boolean; error_key?: string }>;
    logout: () => void;
    isAuthenticated: boolean;
    isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [token, setToken] = useState<string | null>(null);
    const [user, setUser] = useState<{ id: number; role: string } | null>(null);

    useEffect(() => {
        // Load token from localStorage on mount
        const storedToken = localStorage.getItem('auth_token');
        const storedUser = localStorage.getItem('auth_user');

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = async (email: string, password: string, organization_slug?: string) => {
        const response = await apiClient.login(email, password, organization_slug);

        if (response.ok && response.data) {
            const { token: newToken, user_id, role } = response.data;

            setToken(newToken);
            setUser({ id: user_id, role });

            localStorage.setItem('auth_token', newToken);
            localStorage.setItem('auth_user', JSON.stringify({ id: user_id, role }));

            return { ok: true };
        }

        return { ok: false, error_key: response.error_key || 'internal_error' };
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
    };

    return (
        <AuthContext.Provider
            value={{
                token,
                user,
                login,
                logout,
                isAuthenticated: !!token,
                isAdmin: user?.role === 'Admin' || user?.role === 'Staff',
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
