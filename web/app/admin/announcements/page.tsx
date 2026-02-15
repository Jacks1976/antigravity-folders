'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { useToast } from '@/lib/toast-context';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function AdminAnnouncementsPage() {
    const { isAdmin, isAuthenticated } = useAuth();
    const { t } = useI18n();
    const { success, error } = useToast();
    const router = useRouter();

    const [loading, setLoading] = useState(false);
    const [announcementForm, setAnnouncementForm] = useState({
        title: '',
        body: '',
        target_type: 'GLOBAL',
        target_id: '',
        expires_at: '',
        is_pinned: false,
    });

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        } else if (!isAdmin) {
            router.push('/dashboard');
        }
    }, [isAuthenticated, isAdmin, router]);

    const handleCreateAnnouncement = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        const result = await apiClient.postAnnouncement({
            title: announcementForm.title,
            body: announcementForm.body,
            target_type: announcementForm.target_type,
            target_id: announcementForm.target_type !== 'GLOBAL' && announcementForm.target_id
                ? parseInt(announcementForm.target_id)
                : undefined,
            expires_at: announcementForm.expires_at || undefined,
            is_pinned: announcementForm.is_pinned,
        });

        if (result.ok) {
            success('Anúncio criado com sucesso!');
            setAnnouncementForm({
                title: '',
                body: '',
                target_type: 'GLOBAL',
                target_id: '',
                expires_at: '',
                is_pinned: false,
            });
        } else {
            error(t(result.error_key || 'internal_error'));
        }
        setLoading(false);
    };

    if (!isAdmin) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    return (
        <div className="max-w-4xl mx-auto p-4">

            <h1 className="text-3xl font-bold mb-6">{t('ui.announcement_management')}</h1>

            <div className="border rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4">{t('ui.create_announcement')}</h2>
                <form onSubmit={handleCreateAnnouncement}>
                    <div className="mb-4">
                        <label className="block mb-2">{t('ui.title')}</label>
                        <input
                            type="text"
                            required
                            value={announcementForm.title}
                            onChange={(e) => setAnnouncementForm({ ...announcementForm, title: e.target.value })}
                            className="w-full px-4 py-2 border rounded"
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2">{t('ui.body')}</label>
                        <textarea
                            required
                            value={announcementForm.body}
                            onChange={(e) => setAnnouncementForm({ ...announcementForm, body: e.target.value })}
                            className="w-full px-4 py-2 border rounded"
                            rows={4}
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2">{t('ui.target_type')}</label>
                        <select
                            value={announcementForm.target_type}
                            onChange={(e) => setAnnouncementForm({ ...announcementForm, target_type: e.target.value })}
                            className="w-full px-4 py-2 border rounded"
                        >
                            <option value="GLOBAL">{t('ui.global')}</option>
                            <option value="ROLE">{t('ui.role_target')}</option>
                            <option value="MINISTRY">{t('ui.ministry_target')}</option>
                        </select>
                    </div>
                    {announcementForm.target_type !== 'GLOBAL' && (
                        <div className="mb-4">
                            <label className="block mb-2">{t('ui.target_id')}</label>
                            <input
                                type="number"
                                required
                                value={announcementForm.target_id}
                                onChange={(e) => setAnnouncementForm({ ...announcementForm, target_id: e.target.value })}
                                className="w-full px-4 py-2 border rounded"
                                placeholder="Role ID or Ministry ID"
                            />
                        </div>
                    )}
                    <div className="mb-4">
                        <label className="block mb-2">{t('ui.expires_at')} (UTC, optional)</label>
                        <input
                            type="datetime-local"
                            value={announcementForm.expires_at}
                            onChange={(e) => setAnnouncementForm({ ...announcementForm, expires_at: e.target.value ? e.target.value + ':00Z' : '' })}
                            className="w-full px-4 py-2 border rounded"
                        />
                    </div>
                    <div className="mb-4">
                        <label className="flex items-center">
                            <input
                                type="checkbox"
                                checked={announcementForm.is_pinned}
                                onChange={(e) => setAnnouncementForm({ ...announcementForm, is_pinned: e.target.checked })}
                                className="mr-2"
                            />
                            {t('ui.is_pinned')}
                        </label>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                    >
                        {loading ? t('ui.loading') : t('ui.create_announcement')}
                    </button>
                </form>
            </div>
        </div>
    );
}
