'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

export default function Home() {
    const { isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
        // If already authenticated, go to dashboard
        // Otherwise go to landing page
        if (isAuthenticated) {
            router.push('/dashboard');
        } else {
            router.push('/landing');
        }
    }, [isAuthenticated, router]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900">ChurchHub</h1>
                <p className="mt-4 text-gray-600">Carregando...</p>
            </div>
        </div>
    );
}
