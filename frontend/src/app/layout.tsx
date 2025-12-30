import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '../components/auth/AuthProvider';
import { Navbar } from '../components/layout/Navbar';
import { ToastContainer } from '../components/ui/Toast';

export const metadata: Metadata = {
    title: 'Prompty Challenge - Prompt Injection Game',
    description: 'A real-time competitive prompt injection challenge platform. Can you extract the secret password from Prompty?',
    keywords: ['prompt injection', 'AI security', 'CTF', 'challenge', 'game'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className="min-h-screen bg-dark-900 text-white antialiased">
                <AuthProvider>
                    <div className="flex flex-col min-h-screen">
                        <Navbar />
                        <main className="flex-1">
                            {children}
                        </main>
                        <footer className="py-6 border-t border-dark-800">
                            <div className="container mx-auto px-4 text-center text-dark-400">
                                <p>© 2025 Prompty Challenge. All rights reserved.</p>
                            </div>
                        </footer>
                    </div>
                    <ToastContainer />
                </AuthProvider>
            </body>
        </html>
    );
}
