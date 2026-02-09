'use client';

import { ReactNode } from 'react';

interface ChatProviderWrapperProps {
  children: ReactNode;
}

// Simple wrapper component - ChatKit setup is now in ChatInterface
export const ChatProviderWrapper = ({ children }: ChatProviderWrapperProps) => {
  return <>{children}</>;
};