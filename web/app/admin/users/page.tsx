'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function AdminUsersPage() {
    const { isAdmin, isAuthenticated } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState<string | null>(null);
    const [filter, setFilter] = useState('Pending');

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        } else if (!isAdmin) {
            router.push('/dashboard');
        } else {
            loadUsers();
        }
    }, [isAuthenticated, isAdmin, router]);

    const loadUsers = async () => {
        setLoading(true);
        // Note: API doesn't have a list users endpoint, so we'll use directory
        const result = await apiClient.getDirectory({ limit: 100, offset: 0 });
        if (result.ok && result.data) {
            setUsers(result.data.results || []);
        } else {
            showToast(result.error_key || 'internal_error');
        }
        setLoading(false);
    };

    const showToast = (key: string) => {
        setToast(key);
        setTimeout(() => setToast(null), 3000);
    };

    const handleApprove = async (email: string) => {
        const result = await apiClient.approve(email);
        if (result.ok) {
            showToast('auth.user_approved');
            loadUsers();
        } else {
            showToast(result.error_key || 'internal_error');
        }
    };

    if (!isAdmin) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    const filteredUsers = users.filter(u => filter === 'All' || u.status === filter);

    return (
        <div className="max-w-6xl mx-auto p-4">
            {toast && (
                <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded shadow-lg">
                    {t(toast)}
                </div>
            )}

            <h1 className="text-3xl font-bold mb-6">{t('ui.user_management')}</h1>

            <div className="mb-4 flex gap-2">
                <button
                    onClick={() => setFilter('Pending')}
                    className={`px-4 py-2 rounded ${filter === 'Pending' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                    {t('ui.pending_users')}
                </button>
                <button
                    onClick={() => setFilter('All')}
                    className={`px-4 py-2 rounded ${filter === 'All' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                    {t('ui.all_users')}
                </button>
            </div>

            {loading ? (
                <p>{t('ui.loading')}</p>
            ) : filteredUsers.length === 0 ? (
                <p className="text-gray-500">{t('ui.no_results')}</p>
            ) : (
                <div className="border rounded overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="text-left p-3">{t('ui.full_name')}</th>
                                <th className="text-left p-3">{t('ui.email')}</th>
                                <th className="text-left p-3">{t('ui.status')}</th>
                                <th className="text-left p-3">{t('ui.role')}</th>
                                <th className="text-left p-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredUsers.map((user) => (
                                <tr key={user.email} className="border-t">
                                    <td className="p-3">{user.full_name}</td>
                                    <td className="p-3">{user.email}</td>
                                    <td className="p-3">
                                        <span className={`px-2 py-1 rounded text-sm ${user.status === 'Active' ? 'bg-green-100 text-green-800' :
                                                user.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-red-100 text-red-800'
                                            }`}>
                                            {user.status}
                                        </span>
                                    </td>
                                    <td className="p-3">{user.role || 'Member'}</td>
                                    <td className="p-3">
                                        {user.status === 'Pending' && (
                                            <button
                                                onClick={() => handleApprove(user.email)}
                                                className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                                            >
                                                {t('ui.approve')}
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
