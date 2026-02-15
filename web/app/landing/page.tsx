'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useI18n } from '@/lib/i18n-context';
import { useRouter } from 'next/navigation';

interface Church {
  id: number;
  name: string;
  slug: string;
  city: string;
}

export default function LandingPage() {
  const { t, locale, setLocale } = useI18n();
  const router = useRouter();
  const [selectedChurch, setSelectedChurch] = useState<Church | null>(null);
  const [churches, setChurches] = useState<Church[]>([
    {
      id: 1,
      name: 'PIBG - Primeira Igreja Brasileira de Greenville',
      slug: 'pibg-greenville',
      city: 'Greenville, SC'
    },
    {
      id: 2,
      name: 'Comunidade Cristã do Brasil',
      slug: 'comunidade-cristã',
      city: 'New York, NY'
    },
    {
      id: 3,
      name: 'Templo Pentecostal Brasileiro',
      slug: 'templo-pentecostal',
      city: 'Miami, FL'
    },
  ]);
  const [showChurchSelector, setShowChurchSelector] = useState(false);

  // Load organizations from backend public API (fallback to hardcoded list)
  useEffect(() => {
    async function loadOrgs() {
      try {
        const base = process.env.NEXT_PUBLIC_API_BASE_URL || '';
        const res = await fetch(`${base}/organizations/public`);
        const json = await res.json();
        if (json && json.ok && json.data && Array.isArray(json.data.results)) {
          setChurches(json.data.results.map((r: any) => ({ id: r.id, name: r.name, slug: r.slug, city: r.city })));
        }
      } catch (e) {
        // ignore and keep fallback list
      }
    }

    loadOrgs();
  }, []);

  const handleSelectChurch = (church: Church) => {
    setSelectedChurch(church);
    localStorage.setItem('selected_church_id', church.id.toString());
    localStorage.setItem('selected_church_slug', church.slug);
    setShowChurchSelector(false);
  };

  const handleLogin = () => {
    if (!selectedChurch) {
      alert(t('landing.select_church_error'));
      setShowChurchSelector(true);
      return;
    }
    router.push(`/login?church=${selectedChurch.slug}`);
  };

  const handleRegister = () => {
    if (!selectedChurch) {
      alert(t('landing.select_church_error'));
      setShowChurchSelector(true);
      return;
    }
    router.push(`/register?church=${selectedChurch.slug}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-blue-800 flex flex-col">
      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-2">
        <div className="max-w-md w-full space-y-6 text-center">
          {/* Logo/Branding */}
          <div className="space-y-2">
            <p className="text-2xl font-light text-white branding-font">
              {t('landing.tagline')}
            </p>
          </div>

          {/* Church Selection */}
          <div className="bg-white/90 backdrop-blur-sm rounded-xl p-6 shadow-2xl space-y-4 border border-white/20">
            <div>
              <label className="block text-sm font-semibold text-gray-800 mb-2">
                {t('landing.select_church')}
              </label>
              {selectedChurch ? (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-lg p-4 cursor-pointer hover:from-purple-100 hover:to-blue-100 transition-all" onClick={() => setShowChurchSelector(!showChurchSelector)}>
                  <p className="font-semibold text-gray-900">{selectedChurch.name}</p>
                  <p className="text-sm text-gray-600">{selectedChurch.city}</p>
                </div>
              ) : (
                <button
                  onClick={() => setShowChurchSelector(!showChurchSelector)}
                  className="w-full border-2 border-dashed border-purple-300 rounded-lg p-4 text-gray-600 hover:border-purple-400 hover:bg-purple-50/50 transition-all"
                >
                  {t('landing.click_to_select')}
                </button>
              )}
            </div>

            {/* Church Dropdown */}
            {showChurchSelector && (
              <div className="border-2 border-purple-200 rounded-lg max-h-48 overflow-y-auto space-y-2 p-2 bg-white/95">
                {churches.map((church) => (
                  <button
                    key={church.id}
                    onClick={() => handleSelectChurch(church)}
                    className={`w-full text-left p-3 rounded border-l-4 transition-all ${
                      selectedChurch?.id === church.id
                        ? 'bg-gradient-to-r from-purple-50 to-blue-50 border-l-purple-600 border border-purple-200'
                        : 'border-l-gray-300 border border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <p className="font-medium text-gray-900">{church.name}</p>
                    <p className="text-xs text-gray-500">{church.city}</p>
                  </button>
                ))}
              </div>
            )}

            {/* Authentication Buttons */}
            <div className="space-y-3 pt-4">
              <button
                onClick={handleLogin}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
              >
                {t('landing.do_login')}
              </button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white/90 text-gray-600">{t('landing.or')}</span>
                </div>
              </div>

              <button
                onClick={handleRegister}
                className="w-full border-2 border-purple-600 text-purple-600 py-3 px-4 rounded-lg font-semibold hover:bg-purple-50 transition-all"
              >
                {t('landing.do_register')}
              </button>

              {/* Social Auth Placeholders */}
              <div className="pt-4 space-y-2">
                <p className="text-xs text-gray-500 mb-3">{t('landing.next_options')}</p>
                <button
                  disabled
                  className="w-full flex items-center justify-center gap-2 bg-white border border-gray-300 py-2 px-4 rounded-lg text-gray-600 opacity-50 cursor-not-allowed"
                >
                  <span>🔍</span>
                  {t('landing.google_continue')}
                </button>
                <button
                  disabled
                  className="w-full flex items-center justify-center gap-2 bg-black text-white py-2 px-4 rounded-lg opacity-50 cursor-not-allowed"
                >
                  <span>🍎</span>
                  {t('landing.apple_continue')}
                </button>
              </div>
            </div>
          </div>

          {/* Footer Info */}
          <div className="text-blue-50 text-xs space-y-1">
            <p>{t('ui.copyright')}</p>
            <div className="flex justify-center gap-4">
              <button className="hover:text-white transition-colors">{t('landing.about')}</button>
              <button className="hover:text-white transition-colors">{t('landing.privacy')}</button>
              <button className="hover:text-white transition-colors">{t('landing.terms')}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
