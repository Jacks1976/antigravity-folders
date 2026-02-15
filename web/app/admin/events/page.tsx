'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { useToast } from '@/lib/toast-context';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function AdminEventsPage() {
    const { isAdmin, isAuthenticated } = useAuth();
    const { t } = useI18n();
    const { success, error } = useToast();
    const router = useRouter();

    const [events, setEvents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [eventForm, setEventForm] = useState({
        title: '',
        start_time: '',
        end_time: '',
        location: '',
        description: '',
        visibility: 'public',
        target_ministries: '',
    });

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        } else if (!isAdmin) {
            router.push('/dashboard');
        } else {
            loadEvents();
        }
    }, [isAuthenticated, isAdmin, router]);

    const loadEvents = async () => {
        setLoading(true);
        const result = await apiClient.listEvents({});
        if (result.ok && result.data) {
            setEvents(result.data.results || []);
        } else {
            error(t(result.error_key || 'internal_error'));
        }
        setLoading(false);
    };

    const handleCreateEvent = async (e: React.FormEvent) => {
        e.preventDefault();

        const ministryIds = eventForm.target_ministries
            ? eventForm.target_ministries.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
            : undefined;

        const result = await apiClient.createEvent({
            title: eventForm.title,
            start_time: eventForm.start_time,
            end_time: eventForm.end_time,
            location: eventForm.location || undefined,
            description: eventForm.description || undefined,
            visibility: eventForm.visibility,
            target_ministry_ids: ministryIds,
        });

        if (result.ok) {
            success('Evento criado com sucesso!');
            setShowCreateModal(false);
            setEventForm({
                title: '',
                start_time: '',
                end_time: '',
                location: '',
                description: '',
                visibility: 'public',
                target_ministries: '',
            });
            loadEvents();
        } else {
            error(t(result.error_key || 'internal_error'));
        }
    };

    if (!isAdmin) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    return (
        <div className="max-w-6xl mx-auto p-4">

            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">{t('ui.event_management')}</h1>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    {t('ui.create_event')}
                </button>
            </div>

            {loading ? (
                <p>{t('ui.loading')}</p>
            ) : events.length === 0 ? (
                <p className="text-gray-500">{t('ui.no_results')}</p>
            ) : (
                <div className="grid gap-4">
                    {events.map((event) => (
                        <div key={event.id} className="border rounded p-4">
                            <h3 className="font-bold text-lg">{event.title}</h3>
                            <p className="text-gray-600">{new Date(event.start_time).toLocaleString()}</p>
                            {event.location && <p className="text-sm text-gray-500">{event.location}</p>}
                            <span className={`inline-block mt-2 px-2 py-1 rounded text-sm ${event.visibility === 'public' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                                }`}>
                                {event.visibility}
                            </span>
                        </div>
                    ))}
                </div>
            )}

            {/* Create Event Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 overflow-y-auto">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full my-8">
                        <h2 className="text-2xl font-bold mb-4">{t('ui.create_event')}</h2>
                        <form onSubmit={handleCreateEvent}>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.title')}</label>
                                <input
                                    type="text"
                                    required
                                    value={eventForm.title}
                                    onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.start')} (UTC)</label>
                                <input
                                    type="datetime-local"
                                    required
                                    value={eventForm.start_time}
                                    onChange={(e) => setEventForm({ ...eventForm, start_time: e.target.value + ':00Z' })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.end')} (UTC)</label>
                                <input
                                    type="datetime-local"
                                    required
                                    value={eventForm.end_time}
                                    onChange={(e) => setEventForm({ ...eventForm, end_time: e.target.value + ':00Z' })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.location')}</label>
                                <input
                                    type="text"
                                    value={eventForm.location}
                                    onChange={(e) => setEventForm({ ...eventForm, location: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.description')}</label>
                                <textarea
                                    value={eventForm.description}
                                    onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                    rows={3}
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.visibility')}</label>
                                <select
                                    value={eventForm.visibility}
                                    onChange={(e) => setEventForm({ ...eventForm, visibility: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                >
                                    <option value="public">{t('ui.public')}</option>
                                    <option value="internal">{t('ui.internal')}</option>
                                </select>
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.target_ministries')} (comma-separated IDs)</label>
                                <input
                                    type="text"
                                    value={eventForm.target_ministries}
                                    onChange={(e) => setEventForm({ ...eventForm, target_ministries: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                    placeholder="1,2,3"
                                />
                            </div>
                            <div className="flex gap-2">
                                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                    {t('ui.save')}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
                                >
                                    {t('ui.cancel')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
