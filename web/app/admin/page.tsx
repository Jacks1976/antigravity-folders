'use client';

import { useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useI18n } from '@/lib/i18n-context';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default function AdminPage() {
    const { isAdmin, isAuthenticated } = useAuth();
    const { t } = useI18n();
    const router = useRouter();

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        } else if (!isAdmin) {
            router.push('/dashboard');
        }
    }, [isAuthenticated, isAdmin, router]);

    if (!isAdmin) {
        return <div className="p-8">{t('ui.loading')}</div>;
    }

    const adminSections = [
        { title: t('ui.user_management'), href: '/admin/users', description: 'Approve pending users and manage user status' },
        { title: t('ui.ministry_management'), href: '/admin/members', description: 'Assign ministries and roles to members' },
        { title: t('ui.event_management'), href: '/admin/events', description: 'Create and manage church events' },
        { title: t('ui.announcement_management'), href: '/admin/announcements', description: 'Create targeted announcements' },
    ];

return (
    <div className="max-w-6xl mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">{t('ui.admin')}</h1>

        <div className="grid gap-4 md:grid-cols-2">
            {adminSections.map((section) => (
                <Link
                    key={section.href}
                    href={section.href}
                    className="border rounded-lg p-6 hover:bg-gray-50 hover:shadow-md transition"
                >
                    <h2 className="text-xl font-bold mb-2">{section.title}</h2>
                    <p className="text-gray-600">{section.description}</p>
                </Link>
            ))}
        </div>
    </div>
);
}
