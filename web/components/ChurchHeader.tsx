'use client';

import Link from 'next/link';

export default function ChurchHeader() {
    return (
        <header className="w-full bg-white p-6 rounded-lg shadow flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">

            {/* LOGO + TÍTULO */}
            <div className="flex items-center gap-6 flex-shrink-0">

                {/* Container do logo para garantir tamanho */}
                <div className="h-auto w-auto flex items-center justify-start flex-shrink-0 gap-4">
                    <img
                        src="/pad2.png"
                        alt="Hub Pad Church"
                        className="object-contain h-[180px] w-[180px]"
                    />

                    {/* Título do App + Igreja selecionada */}
                    <div className="flex flex-col">
                        <h1 className="text-xl font-extrabold text-gray-900 leading-tight branding-font">
                            Hub • Pad • Church
                        </h1>
                        <p className="text-sm text-gray-600 -mt-1 italic branding-font">
                            {/* organization name will be injected by parent or context */}
                            the Church in your hands
                        </p>
                    </div>
                </div>
            </div>

            {/* AÇÕES RÁPIDAS */}
            <div className="flex gap-4 sm:gap-6 text-base font-medium">

                <a
                    href="https://www.bible.com/pt"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-500 transition-colors"
                >
                    📖 Bíblia Online
                </a>

                <Link
                    href="/events"
                    className="text-gray-700 hover:text-gray-900 transition-colors"
                >
                    📅 Agenda
                </Link>

            </div>
        </header>
    );
}
