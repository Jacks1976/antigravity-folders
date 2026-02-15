'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { useRouter } from 'next/navigation';

export function Navigation() {
    const { isAuthenticated, logout, isAdmin } = useAuth();
    const { t, locale, setLocale } = useI18n();
    const router = useRouter();

    const handleLogout = () => {
        logout();
        router.push('/login');
    };

    return (
        <nav className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center gap-4 py-2">
                    <Link href="/" className="flex items-center">
                        <img src="/MyChurchPad_logo.png" alt="MyChurchPad" className="h-[190px] w-[190px] object-contain" />
                    </Link>

                    <div className="hidden lg:flex flex-1 justify-center px-4">
                        <p className="text-sm text-gray-600 branding-font opacity-90">{t('header.verse')}</p>
                    </div>

                    {isAuthenticated && (
                        <div className="hidden md:flex items-center space-x-4">
                            <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                {t('ui.dashboard')}
                            </Link>
                            <Link href="/events" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                {t('ui.events')}
                            </Link>
                            <Link href="/announcements" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                {t('ui.announcements')}
                            </Link>
                            <Link href="/members" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                {t('ui.members')}
                            </Link>
                            <Link href="/worship/repertoire" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                {t('ui.repertoire')}
                            </Link>
                            <Link href="/worship/schedule" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                {t('ui.schedule')}
                            </Link>
                            {isAdmin && (
                                <Link href="/admin" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">
                                    {t('ui.admin')}
                                </Link>
                            )}
                        </div>
                    )}

                    <div className="flex items-center space-x-3">
                        {/* Language Switcher */}
                        <select
                            value={locale}
                            onChange={(e) => setLocale(e.target.value as any)}
                            className="text-xs border rounded px-2 py-1"
                        >
                            <option value="pt-BR">🇧🇷 PT</option>
                            <option value="en">🇺🇸 EN</option>
                            <option value="es">🇪🇸 ES</option>
                        </select>

                        {isAuthenticated ? (
                            <button
                                onClick={handleLogout}
                                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                            >
                                {t('ui.logout')}
                            </button>
                        ) : (
                            <>
                                <Link href="/login" className="text-blue-600 hover:text-blue-700 px-3 py-2 rounded-md text-sm font-medium">
                                    {t('ui.login')}
                                </Link>
                                <Link href="/register" className="bg-blue-600 text-white hover:bg-blue-700 px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap">
                                    {t('ui.register')}
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
