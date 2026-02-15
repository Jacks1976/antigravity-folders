'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';

export default function EventsPage() {
    const { isAuthenticated } = useAuth();
    const { t } = useI18n();

    const [events, setEvents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedEvent, setSelectedEvent] = useState<any>(null);
    const [rsvpLoading, setRsvpLoading] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        loadEvents();
    }, []);

    const loadEvents = async () => {
        setLoading(true);
        const result = await apiClient.listEvents({});
        if (result.ok && result.data) {
            setEvents(result.data.results);
        }
        setLoading(false);
    };

    const handleRsvp = async (eventId: number, status: string) => {
        setRsvpLoading(true);
        setMessage('');

        const result = await apiClient.rsvpEvent(eventId, status);

        if (result.ok) {
            setMessage(t('event.rsvp_saved'));
            setTimeout(() => setMessage(''), 3000);
        } else {
            setMessage(t(result.error_key || 'internal_error'));
        }

        setRsvpLoading(false);
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
                <h1 className="text-3xl font-bold text-gray-900 mb-8">{t('ui.events')}</h1>

                {message && (
                    <div className="mb-4 rounded-md bg-green-50 p-4">
                        <p className="text-sm text-green-800">{message}</p>
                    </div>
                )}

                {events.length === 0 ? (
                    <p className="text-gray-500">{t('ui.no_results')}</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {events.map((event) => (
                            <div key={event.id} className="bg-white shadow rounded-lg p-6">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-lg font-semibold text-gray-900">{event.title}</h3>
                                    {event.public && (
                                        <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                            {t('ui.public')}
                                        </span>
                                    )}
                                </div>

                                <div className="space-y-2 text-sm text-gray-600">
                                    <p>
                                        <strong>{t('ui.start')}:</strong>{' '}
                                        {new Date(event.start).toLocaleString()}
                                    </p>
                                    <p>
                                        <strong>{t('ui.end')}:</strong>{' '}
                                        {new Date(event.end).toLocaleString()}
                                    </p>
                                    {event.location && (
                                        <p>
                                            <strong>{t('ui.location')}:</strong> {event.location}
                                        </p>
                                    )}
                                    {event.description && (
                                        <p className="mt-2 text-gray-700">{event.description}</p>
                                    )}
                                </div>

                                {isAuthenticated && (
                                    <div className="mt-4 pt-4 border-t border-gray-200">
                                        <p className="text-sm font-medium text-gray-700 mb-2">{t('ui.rsvp')}:</p>
                                        <div className="flex space-x-2">
                                            <button
                                                onClick={() => handleRsvp(event.id, 'going')}
                                                disabled={rsvpLoading}
                                                className="flex-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50"
                                            >
                                                {t('ui.going')}
                                            </button>
                                            <button
                                                onClick={() => handleRsvp(event.id, 'maybe')}
                                                disabled={rsvpLoading}
                                                className="flex-1 bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700 disabled:opacity-50"
                                            >
                                                {t('ui.maybe')}
                                            </button>
                                            <button
                                                onClick={() => handleRsvp(event.id, 'not_going')}
                                                disabled={rsvpLoading}
                                                className="flex-1 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 disabled:opacity-50"
                                            >
                                                {t('ui.not_going')}
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
