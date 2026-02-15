import './globals.css';
import { Navigation } from '@/components/Navigation';
import { Providers } from './providers';
import { ToastContainer } from '@/components/ToastContainer';
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="pt-BR">
            <body className="bg-gray-100">
                <ErrorBoundary>
                    <Providers>
                        <Navigation />
                        <main>{children}</main>
                        <ToastContainer />
                    </Providers>
                </ErrorBoundary>
            </body>
        </html>
    );
}
