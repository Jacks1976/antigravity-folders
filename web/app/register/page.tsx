'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api-client';
import { useI18n } from '@/lib/i18n-context';
import { useToast } from '@/lib/toast-context';
import { validateForm } from '@/lib/validators';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { PasswordStrengthIndicator } from '@/components/PasswordStrengthIndicator';

export default function RegisterPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const [fieldErrors, setFieldErrors] = useState<{ [key: string]: string }>({});
    const [churchSlug, setChurchSlug] = useState('');
    const [churchName, setChurchName] = useState('');

    const { t } = useI18n();
    const { success: toastSuccess, error: toastError } = useToast();
    const router = useRouter();

    useEffect(() => {
        if (typeof window === 'undefined') {
            router.push('/landing');
            return;
        }
        const params = new URLSearchParams(window.location.search);
        const church = params.get('church');
        if (church) {
            setChurchSlug(church);
            const churchMap: { [key: string]: string } = {
                'pibg-greenville': 'PIBG - Primeira Igreja Brasileira de Greenville',
                'comunidade-cristã': 'Comunidade Cristã do Brasil',
                'templo-pentecostal': 'Templo Pentecostal Brasileiro',
            };
            setChurchName(churchMap[church] || 'Sua Igreja');
        } else {
            router.push('/landing');
        }
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess(false);
        setFieldErrors({});
        setLoading(true);

        // Validar formulário
        const validationErrors = validateForm({
            email,
            fullName,
            password,
        });

        if (validationErrors.length > 0) {
            const errorsMap = validationErrors.reduce((acc, err) => {
                acc[err.field] = err.message;
                return acc;
            }, {} as { [key: string]: string });
            
            setFieldErrors(errorsMap);
            toastError(t('register.form_errors'));
            setLoading(false);
            return;
        }

        const result = await apiClient.register(email, password, fullName, churchSlug);

        if (result.ok) {
            setSuccess(true);
            setEmail('');
            setPassword('');
            setFullName('');
            toastSuccess(t('register.success'));
        } else {
            const errorMsg = t(result.error_key || 'internal_error');
            setError(errorMsg);
            toastError(errorMsg);
        }

        setLoading(false);
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        {t('ui.register')}
                    </h2>
                    {churchName && (
                        <div className="mt-4 text-center">
                            <p className="text-sm text-gray-600">{t('register.entering')}</p>
                            <p className="text-lg font-semibold text-blue-600">{churchName}</p>
                            <Link href="/landing" className="text-xs text-gray-500 hover:text-gray-700 mt-2 inline-block">
                                {t('register.change_church')}
                            </Link>
                        </div>
                    )}
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="rounded-md bg-red-50 p-4">
                            <p className="text-sm text-red-800">{error}</p>
                        </div>
                    )}

                    {success && (
                        <div className="rounded-md bg-green-50 p-4">
                            <p className="text-sm text-green-800">{t('auth.register_success')}</p>
                            <p className="text-sm text-green-700 mt-2">{t('auth.account_pending')}</p>
                        </div>
                    )}

                    <div className="rounded-md shadow-sm space-y-4">
                        <div>
                            <label htmlFor="fullName" className="sr-only">{t('ui.full_name')}</label>
                            <input
                                id="fullName"
                                name="fullName"
                                type="text"
                                required
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className={`appearance-none relative block w-full px-3 py-2 border placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                                    fieldErrors.fullName ? 'border-red-500' : 'border-gray-300'
                                }`}
                                placeholder={t('ui.full_name')}
                            />
                            {fieldErrors.fullName && (
                                <p className="mt-1 text-sm text-red-600">{fieldErrors.fullName}</p>
                            )}
                        </div>
                        <div>
                            <label htmlFor="email" className="sr-only">{t('ui.email')}</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={`appearance-none relative block w-full px-3 py-2 border placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                                    fieldErrors.email ? 'border-red-500' : 'border-gray-300'
                                }`}
                                placeholder={t('ui.email')}
                            />
                            {fieldErrors.email && (
                                <p className="mt-1 text-sm text-red-600">{fieldErrors.email}</p>
                            )}
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">{t('ui.password')}</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className={`appearance-none relative block w-full px-3 py-2 border placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                                    fieldErrors.password ? 'border-red-500' : 'border-gray-300'
                                }`}
                                placeholder={t('ui.password')}
                            />
                            {fieldErrors.password && (
                                <p className="mt-1 text-sm text-red-600">{fieldErrors.password}</p>
                            )}
                            {password && <PasswordStrengthIndicator password={password} />}
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center items-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-wait transition-all"
                        >
                            {loading ? (
                                <>
                                    <LoadingSpinner size="sm" color="white" />
                                    <span className="ml-2">{t('ui.loading')}</span>
                                </>
                            ) : (
                                t('ui.register')
                            )}
                        </button>
                    </div>

                    <div className="text-center">
                        <Link href={`/login?church=${encodeURIComponent(churchSlug)}`} className="text-blue-600 hover:text-blue-500">
                            {t('ui.login')}
                        </Link>
                    </div>
                </form>
            </div>
        </div>
    );
}
