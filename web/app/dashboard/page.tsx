'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { useOrganization } from '@/lib/organization-context';
import { apiClient } from '@/lib/api-client';
import Link from 'next/link';

export default function DashboardPage() {
    const { isAuthenticated } = useAuth();
    const { t } = useI18n();
    const { organization } = useOrganization();
    const router = useRouter();

    const [events, setEvents] = useState<any[]>([]);
    const [announcements, setAnnouncements] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
            return;
        }

        loadData();
    }, [isAuthenticated, router]);

    const loadData = async () => {
        setLoading(true);

        const now = new Date().toISOString();

        const eventsResult = await apiClient.listEvents({ from: now });
        if (eventsResult.ok && eventsResult.data) {
            setEvents(eventsResult.data.results.slice(0, 3));
        }

        const announcementsResult = await apiClient.getAnnouncementsFeed({ limit: 5 });
        if (announcementsResult.ok && announcementsResult.data) {
            setAnnouncements(announcementsResult.data.results);
        }

        setLoading(false);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <p className="text-gray-600">{t('ui.loading')}</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <h1 className="text-3xl font-bold text-gray-900">
                        {organization?.name || t('dashboard.church_name_default')}
                    </h1>
                    <p className="text-gray-600 mt-2">
                        {t('ui.welcome_back')}
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <p className="text-gray-600">{t('ui.loading')}</p>
                    </div>
                ) : (
                    <>
                        {/* Quick Actions Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                            <Link
                                href="/events"
                                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow text-center"
                            >
                                <div className="text-3xl mb-3">📅</div>
                                <h3 className="font-semibold text-gray-900">{t('dashboard.events')}</h3>
                                <p className="text-sm text-gray-600 mt-1">{t('dashboard.view_upcoming')}</p>
                            </Link>

                            <Link
                                href="/announcements"
                                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow text-center"
                            >
                                <div className="text-3xl mb-3">📢</div>
                                <h3 className="font-semibold text-gray-900">{t('dashboard.announcements')}</h3>
                                <p className="text-sm text-gray-600 mt-1">{t('dashboard.latest_announcements')}</p>
                            </Link>

                            <Link
                                href="/members"
                                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow text-center"
                            >
                                <div className="text-3xl mb-3">👥</div>
                                <h3 className="font-semibold text-gray-900">{t('dashboard.members')}</h3>
                                <p className="text-sm text-gray-600 mt-1">{t('dashboard.church_contacts')}</p>
                            </Link>
                        </div>

                        {/* Content Cards */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Upcoming Events */}
                            <div className="bg-white rounded-lg shadow p-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h2 className="text-lg font-semibold text-gray-900">
                                        {t('dashboard.upcoming_events')}
                                    </h2>
                                    <Link href="/events" className="text-sm text-blue-600 hover:text-blue-700">
                                        {t('dashboard.view_all')}
                                    </Link>
                                </div>

                                {events.length === 0 ? (
                                    <p className="text-gray-500 text-sm">{t('ui.no_results')}</p>
                                ) : (
                                    <div className="space-y-3">
                                        {events.map((event) => (
                                            <div key={event.id} className="pb-3 border-b border-gray-100 last:border-0">
                                                <h3 className="font-medium text-gray-900 text-sm">{event.title}</h3>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    {new Date(event.start).toLocaleDateString()} {new Date(event.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </p>
                                                {event.location && (
                                                    <p className="text-xs text-gray-600">{event.location}</p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Latest Announcements */}
                            <div className="bg-white rounded-lg shadow p-6">
                                <div className="flex justify-between items-center mb-4">
                                    <h2 className="text-lg font-semibold text-gray-900">
                                        {t('dashboard.recent_announcements')}
                                    </h2>
                                    <Link href="/announcements" className="text-sm text-blue-600 hover:text-blue-700">
                                        {t('dashboard.view_all')}
                                    </Link>
                                </div>

                                {announcements.length === 0 ? (
                                    <p className="text-gray-500 text-sm">{t('ui.no_results')}</p>
                                ) : (
                                    <div className="space-y-3">
                                        {announcements.map((announcement) => (
                                            <div key={announcement.id} className="pb-3 border-b border-gray-100 last:border-0">
                                                {announcement.is_pinned && (
                                                    <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded mb-2">
                                                        {t('ui.pinned')}
                                                    </span>
                                                )}
                                                <h3 className="font-medium text-gray-900 text-sm">
                                                    {announcement.title}
                                                </h3>
                                                {announcement.body && (
                                                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                                                        {announcement.body}
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
