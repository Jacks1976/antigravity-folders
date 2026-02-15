'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';

export default function SchedulePage() {
    const { user, token } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    const [plans, setPlans] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreatePlan, setShowCreatePlan] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState<any>(null);
    const [toast, setToast] = useState<string | null>(null);

    const [planForm, setPlanForm] = useState({ date: '', notes: '' });

    useEffect(() => {
        if (!token) {
            router.push('/login');
            return;
        }
        loadPlans();
    }, [token]);

    const loadPlans = async () => {
        setLoading(true);
        const result = await apiClient.listPlans({});
        if (result.ok && result.data) {
            setPlans(result.data.results || []);
        } else {
            showToast(result.error_key || 'internal_error');
        }
        setLoading(false);
    };

    const showToast = (key: string) => {
        setToast(key);
        setTimeout(() => setToast(null), 3000);
    };

    const handleCreatePlan = async (e: React.FormEvent) => {
        e.preventDefault();
        const result = await apiClient.createPlan({
            date: planForm.date,
            notes: planForm.notes || undefined,
        });

        if (result.ok) {
            showToast('schedule.plan_created');
            setShowCreatePlan(false);
            setPlanForm({ date: '', notes: '' });
            loadPlans();
        } else {
            showToast(result.error_key || 'internal_error');
        }
    };

    const handleUpdateRosterStatus = async (rosterId: number, status: string) => {
        const result = await apiClient.updateRosterStatus(rosterId, status);
        if (result.ok) {
            showToast('schedule.roster_updated');
            loadPlans();
        } else {
            showToast(result.error_key || 'internal_error');
        }
    };

    if (loading) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    return (
        <div className="max-w-6xl mx-auto p-4">
            {toast && (
                <div className="fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded shadow-lg">
                    {t(toast)}
                </div>
            )}

            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">{t('ui.schedule')}</h1>
                <button
                    onClick={() => setShowCreatePlan(true)}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    {t('ui.create_plan')}
                </button>
            </div>

            {plans.length === 0 ? (
                <p className="text-gray-500">{t('ui.no_results')}</p>
            ) : (
                <div className="grid gap-4">
                    {plans.map((plan) => (
                        <div
                            key={plan.id}
                            className="border rounded p-4 hover:bg-gray-50 cursor-pointer"
                            onClick={() => setSelectedPlan(plan)}
                        >
                            <h3 className="font-bold text-lg">{new Date(plan.date).toLocaleDateString()}</h3>
                            {plan.notes && <p className="text-gray-600 mt-2">{plan.notes}</p>}
                        </div>
                    ))}
                </div>
            )}

            {/* Create Plan Modal */}
            {showCreatePlan && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h2 className="text-2xl font-bold mb-4">{t('ui.create_plan')}</h2>
                        <form onSubmit={handleCreatePlan}>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.date')}</label>
                                <input
                                    type="date"
                                    required
                                    value={planForm.date}
                                    onChange={(e) => setPlanForm({ ...planForm, date: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                />
                            </div>
                            <div className="mb-4">
                                <label className="block mb-2">{t('ui.notes')}</label>
                                <textarea
                                    value={planForm.notes}
                                    onChange={(e) => setPlanForm({ ...planForm, notes: e.target.value })}
                                    className="w-full px-4 py-2 border rounded"
                                    rows={3}
                                />
                            </div>
                            <div className="flex gap-2">
                                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                    {t('ui.save')}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowCreatePlan(false)}
                                    className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
                                >
                                    {t('ui.cancel')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Plan Detail Modal */}
            {selectedPlan && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-2xl font-bold">{new Date(selectedPlan.date).toLocaleDateString()}</h2>
                                {selectedPlan.notes && <p className="text-gray-600">{selectedPlan.notes}</p>}
                            </div>
                            <button onClick={() => setSelectedPlan(null)} className="text-2xl">&times;</button>
                        </div>

                        <div className="mt-6">
                            <h3 className="font-bold text-lg mb-3">{t('ui.setlist')}</h3>
                            <p className="text-gray-500 text-sm">{t('ui.no_results')}</p>
                        </div>

                        <div className="mt-6">
                            <h3 className="font-bold text-lg mb-3">{t('ui.roster')}</h3>
                            <p className="text-gray-500 text-sm">{t('ui.no_results')}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
