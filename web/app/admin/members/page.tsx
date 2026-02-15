'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function AdminMembersPage() {
    const { isAdmin, isAuthenticated } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    const [members, setMembers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState<string | null>(null);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [selectedMember, setSelectedMember] = useState<any>(null);
    const [assignForm, setAssignForm] = useState({ ministry_id: '', role: '', is_lead: false });

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        } else if (!isAdmin) {
            router.push('/dashboard');
        } else {
            loadMembers();
        }
    }, [isAuthenticated, isAdmin, router]);

    const loadMembers = async () => {
        setLoading(true);
        const result = await apiClient.getDirectory({ limit: 100, offset: 0 });
        if (result.ok && result.data) {
            setMembers(result.data.results.filter((m: any) => m.status === 'Active') || []);
        } else {
            showToast(result.error_key || 'internal_error');
        }
        setLoading(false);
    };

    const showToast = (key: string) => {
        setToast(key);
        setTimeout(() => setToast(null), 3000);
    };

    const handleAssignMinistry = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedMember) return;

        // Note: API expects user_id and ministry_id
        // This is a simplified version - you may need to adjust based on actual API
        const result = await apiClient.request('/members/assign-ministry', {
            method: 'POST',
            body: JSON.stringify({
                user_id: selectedMember.user_id,
                ministry_id: parseInt(assignForm.ministry_id),
                role: assignForm.role || undefined,
                is_lead: assignForm.is_lead,
            }),
        });

        if (result.ok) {
            showToast('ministry.assigned');
            setShowAssignModal(false);
            setSelectedMember(null);
            setAssignForm({ ministry_id: '', role: '', is_lead: false });
            loadMembers();
        } else {
            showToast(result.error_key || 'internal_error');
        }
    };

    if (!isAdmin) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    return (
        <div className="max-w-6xl mx-auto p-4">
            {toast && (
                <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded shadow-lg">
                    {t(toast)}
                </div>
            )}

            <h1 className="text-3xl font-bold mb-6">{t('ui.ministry_management')}</h1>

            {loading ? (
                <p>{t('ui.loading')}</p>
            ) : members.length === 0 ? (
                <p className="text-gray-500">{t('ui.no_results')}</p>
            ) : (
                <div className="border rounded overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-100">
                            <tr>
                                <th className="text-left p-3">{t('ui.full_name')}</th>
                                <th className="text-left p-3">{t('ui.email')}</th>
                                <th className="text-left p-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {members.map((member) => (
                                <tr key={member.email} className="border-t">
                                    <td className="p-3">{member.full_name}</td>
                                    <td className="p-3">{member.email}</td>
                                    <td className="p-3">
                                        <button
                                            onClick={() => {
                                                setSelectedMember(member);
                                                setShowAssignModal(true);
                                            }}
                                            className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                                        >
                                            {t('ui.assign_ministry')}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Assign Ministry Modal */}
            {showAssignModal && selectedMember && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h2 className="text-2xl font-bold mb-4">{t('ui.assign_ministry')}</h2>
                        <p className="mb-4 text-gray-600">{selectedMember.full_name}</p>
                        <form onSubmit={handleAssignMinistry}>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.ministry')} ID</label>
                                <input
                                    type="number"
                                    required
                                    value={assignForm.ministry_id}
                                    onChange={(e) => setAssignForm({ ...assignForm, ministry_id: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                    placeholder="1 = Worship, 2 = Tech, etc."
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.role')}</label>
                                <input
                                    type="text"
                                    value={assignForm.role}
                                    onChange={(e) => setAssignForm({ ...assignForm, role: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                    placeholder="Musician, Singer, etc."
                                />
                            </div>
                            <div className="mb-4">
                                <label className="flex items-center">
                                    <input
                                        type="checkbox"
                                        checked={assignForm.is_lead}
                                        onChange={(e) => setAssignForm({ ...assignForm, is_lead: e.target.checked })}
                                        className="mr-2"
                                    />
                                    Ministry Lead
                                </label>
                            </div>
                            <div className="flex gap-2">
                                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                    {t('ui.save')}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowAssignModal(false);
                                        setSelectedMember(null);
                                    }}
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
