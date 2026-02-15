'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';

export default function MembersPage() {
    const { isAuthenticated } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    const [members, setMembers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const limit = 20;

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        loadMembers();
    }, [isAuthenticated, router, offset, search]);

    const loadMembers = async () => {
        setLoading(true);
        const result = await apiClient.getDirectory({ search, limit, offset });

        if (result.ok && result.data) {
            setMembers(result.data.results);
            setHasMore(result.data.results.length === limit);
        }

        setLoading(false);
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setOffset(0);
        loadMembers();
    };

    const handleNext = () => {
        setOffset(offset + limit);
    };

    const handlePrevious = () => {
        setOffset(Math.max(0, offset - limit));
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <p className="text-gray-600">{t('ui.loading')}</p>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('ui.members')}</h1>

                {/* Search */}
                <form onSubmit={handleSearch} className="mb-6">
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder={t('ui.search')}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                        <button
                            type="submit"
                            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                        >
                            {t('ui.search')}
                        </button>
                    </div>
                </form>

                {members.length === 0 ? (
                    <p className="text-gray-500">{t('ui.no_results')}</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {members.map((member) => (
                            <div key={member.id} className="bg-white shadow rounded-lg p-6">
                                <div className="flex items-center space-x-4">
                                    <div className="flex-shrink-0">
                                        <div className="h-12 w-12 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-lg">
                                            {member.full_name?.charAt(0) || '?'}
                                        </div>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                                            {member.full_name}
                                        </h3>
                                        <p className="text-sm text-gray-500 truncate">{member.email}</p>
                                    </div>
                                </div>

                                <div className="mt-4 space-y-2 text-sm text-gray-600">
                                    {member.phone && (
                                        <p>
                                            <strong>{t('ui.phone')}:</strong> {member.phone}
                                        </p>
                                    )}
                                    {member.dob && (
                                        <p>
                                            <strong>DOB:</strong> {member.dob}
                                        </p>
                                    )}
                                    {member.bio && (
                                        <p className="text-gray-700 mt-2">{member.bio}</p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Pagination */}
                <div className="mt-6 flex justify-between items-center">
                    <button
                        onClick={handlePrevious}
                        disabled={offset === 0}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        ← {t('ui.previous')}
                    </button>

                    <span className="text-sm text-gray-600">
                        {offset + 1} - {offset + members.length}
                    </span>

                    <button
                        onClick={handleNext}
                        disabled={!hasMore}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {t('ui.next')} →
                    </button>
                </div>
            </div>
        </div>
    );
}
