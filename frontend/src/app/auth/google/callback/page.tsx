'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../../../contexts/AuthContext';
import GlassCard from '../../../../components/ui/GlassCard';
import api from '../../../../lib/api';

import { Suspense } from 'react';

const GoogleCallbackContent = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginWithGoogle } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('Processing Google authentication...');

  useEffect(() => {
    const handleGoogleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        setStatus('error');
        setMessage(`Authentication failed: ${error}`);
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('No authorization code received from Google');
        return;
      }

      try {
        // Exchange the code for tokens via our backend
        const response = await api.completeGoogleAuth(code);

        if (response.success && response.data) {
          // Store the tokens received from backend
          const tokenData = response.data as any;

          if (tokenData.access_token) {
            localStorage.setItem('authToken', tokenData.access_token);
            localStorage.setItem('refreshToken', tokenData.refresh_token);
            api.setToken(tokenData.access_token);

            setStatus('success');
            setMessage('Authentication successful! Redirecting...');

            // Redirect to dashboard after a short delay
            setTimeout(() => {
              router.push('/dashboard');
              router.refresh();
            }, 1500);
          } else {
            setStatus('error');
            setMessage('Invalid response from server');
          }
        } else {
          setStatus('error');
          setMessage(response.error || 'Failed to complete Google authentication');
        }
      } catch (err) {
        console.error('Google callback error:', err);
        setStatus('error');
        setMessage('An error occurred during authentication');
      }
    };

    handleGoogleCallback();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-black p-4">
      <GlassCard className="w-full max-w-md p-8 text-center">
        {status === 'processing' && (
          <>
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-400">{message}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="text-4xl text-green-500 mx-auto mb-4">✓</div>
            <p className="text-green-400">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="text-4xl text-red-500 mx-auto mb-4">✗</div>
            <p className="text-red-400">{message}</p>
            <button
              onClick={() => router.push('/login')}
              className="mt-6 px-4 py-2 bg-linear-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              Return to Login
            </button>
          </>
        )}
      </GlassCard>
    </div>
  );
};

const GoogleCallbackPage = () => {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-black p-4">
        <GlassCard className="w-full max-w-md p-8 text-center">
           <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
           <p className="mt-4 text-gray-400">Loading...</p>
        </GlassCard>
      </div>
    }>
      <GoogleCallbackContent />
    </Suspense>
  );
};

export default GoogleCallbackPage;