'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Locale = 'pt-BR' | 'en' | 'es';

interface I18nContextType {
    locale: Locale;
    setLocale: (locale: Locale) => void;
    t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

const translations: Record<Locale, Record<string, string>> = {
    'pt-BR': require('@/messages/pt-BR.json'),
    'en': require('@/messages/en.json'),
    'es': require('@/messages/es.json'),
};

export function I18nProvider({ children }: { children: ReactNode }) {
    const [locale, setLocaleState] = useState<Locale>('pt-BR');

    useEffect(() => {
        // Load locale from localStorage
        const stored = localStorage.getItem('locale') as Locale;
        if (stored && ['pt-BR', 'en', 'es'].includes(stored)) {
            setLocaleState(stored);
        }
    }, []);

    const setLocale = (newLocale: Locale) => {
        setLocaleState(newLocale);
        localStorage.setItem('locale', newLocale);
    };

    const t = (key: string): string => {
        return translations[locale][key] || key;
    };

    return (
        <I18nContext.Provider value={{ locale, setLocale, t }}>
            {children}
        </I18nContext.Provider>
    );
}

export function useI18n() {
    const context = useContext(I18nContext);
    if (context === undefined) {
        throw new Error('useI18n must be used within an I18nProvider');
    }
    return context;
}
