'use client';

import { AuthProvider } from '@/lib/auth-context';
import { I18nProvider } from '@/lib/i18n-context';
import { ToastProvider } from '@/lib/toast-context';
import { OrganizationProvider } from '@/lib/organization-context';

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <ToastProvider>
            <I18nProvider>
                <OrganizationProvider>
                    <AuthProvider>
                        {children}
                    </AuthProvider>
                </OrganizationProvider>
            </I18nProvider>
        </ToastProvider>
    );
}
