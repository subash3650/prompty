'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { create } from 'zustand';

// Toast types
type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
    id: string;
    message: string;
    type: ToastType;
}

// Toast store
interface ToastStore {
    toasts: Toast[];
    addToast: (message: string, type: ToastType) => void;
    removeToast: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
    toasts: [],
    addToast: (message, type) => {
        const id = Date.now().toString();
        set((state) => ({
            toasts: [...state.toasts, { id, message, type }],
        }));
        // Auto remove after 5 seconds
        setTimeout(() => {
            set((state) => ({
                toasts: state.toasts.filter((t) => t.id !== id),
            }));
        }, 5000);
    },
    removeToast: (id) => {
        set((state) => ({
            toasts: state.toasts.filter((t) => t.id !== id),
        }));
    },
}));

// Toast Component
function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
    const bgColors = {
        success: 'bg-emerald-500/20 border-emerald-500',
        error: 'bg-red-500/20 border-red-500',
        warning: 'bg-yellow-500/20 border-yellow-500',
        info: 'bg-blue-500/20 border-blue-500',
    };

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ',
    };

    return (
        <div
            className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${bgColors[toast.type]} animate-slide-up`}
        >
            <span className="text-lg">{icons[toast.type]}</span>
            <p className="flex-1 text-white">{toast.message}</p>
            <button
                onClick={onClose}
                className="text-dark-400 hover:text-white transition-colors"
            >
                ✕
            </button>
        </div>
    );
}

// Toast Container - Fixed for SSR hydration
export function ToastContainer() {
    const { toasts, removeToast } = useToastStore();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Don't render on server or before client mount
    if (!mounted) return null;

    return createPortal(
        <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
            {toasts.map((toast) => (
                <ToastItem
                    key={toast.id}
                    toast={toast}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </div>,
        document.body
    );
}

// Hook for using toasts
export function useToast() {
    const addToast = useToastStore((state) => state.addToast);

    return {
        success: (message: string) => addToast(message, 'success'),
        error: (message: string) => addToast(message, 'error'),
        warning: (message: string) => addToast(message, 'warning'),
        info: (message: string) => addToast(message, 'info'),
    };
}
