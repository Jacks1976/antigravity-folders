import Link from 'next/link';

export default function NotFound() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="text-center">
                <h1 className="text-6xl font-extrabold text-gray-900">404</h1>
                <p className="mt-4 text-lg text-gray-600">Página não encontrada</p>
                <Link href="/" className="mt-6 inline-block px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                    Voltar ao início
                </Link>
            </div>
        </div>
    );
}
