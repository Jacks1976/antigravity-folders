'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';

export default function AnnouncementsPage() {
    const { isAuthenticated } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    const [announcements, setAnnouncements] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const limit = 20;

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        loadAnnouncements();
    }, [isAuthenticated, router, offset]);

    const loadAnnouncements = async () => {
        setLoading(true);
        const result = await apiClient.getAnnouncementsFeed({ limit, offset });

        if (result.ok && result.data) {
            setAnnouncements(result.data.results);
            setHasMore(result.data.results.length === limit);
        }

        setLoading(false);
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
        <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('ui.announcements')}</h1>

                {announcements.length === 0 ? (
                    <p className="text-gray-500">{t('ui.no_results')}</p>
                ) : (
                    <div className="space-y-4">
                        {announcements.map((announcement) => (
                            <div key={announcement.id} className="bg-white shadow rounded-lg p-6">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        {announcement.is_pinned && (
                                            <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded mb-2">
                                                📌 {t('ui.pinned')}
                                            </span>
                                        )}
                                        <h3 className="text-lg font-semibold text-gray-900">{announcement.title}</h3>
                                        {announcement.body && (
                                            <p className="mt-2 text-gray-700">{announcement.body}</p>
                                        )}
                                        <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                                            <span>{new Date(announcement.created_at).toLocaleDateString()}</span>
                                            <span className="text-blue-600">{announcement.target_type}</span>
                                        </div>
                                    </div>
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
                        {offset + 1} - {offset + announcements.length}
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
