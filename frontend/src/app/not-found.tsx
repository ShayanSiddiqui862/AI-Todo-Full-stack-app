import Link from 'next/link';
import GlassCard from '@/components/ui/GlassCard';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-black p-4">
      <GlassCard className="text-center p-8 max-w-md w-full">
        <h2 className="text-6xl font-bold gradient-text mb-4">404</h2>
        <h3 className="text-2xl font-semibold text-white mb-4">Page Not Found</h3>
        <p className="text-gray-400 mb-6">
          Sorry, we couldn't find the page you're looking for.
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium rounded-lg hover:opacity-90 transition-opacity"
        >
          Go Back Home
        </Link>
      </GlassCard>
    </div>
  );
}