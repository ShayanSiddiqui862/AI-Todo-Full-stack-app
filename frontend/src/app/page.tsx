export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-black font-sans">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-center py-16 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Hero Section with large 'FOCUSFLOW' title */}
          <h1 className="text-6xl md:text-8xl font-bold mb-8 gradient-text tracking-tight">
            FOCUSFLOW
          </h1>

          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Your productivity companion for focused task management. Streamline your workflow and achieve more with our intuitive interface.
          </p>

          {/* Gradient 'Get Started' button */}
          <a
            href="/login"
            className="inline-block px-8 py-4 text-lg font-semibold text-white rounded-full gradient-bg hover:opacity-90 transition-opacity duration-200 shadow-lg shadow-blue-500/20"
          >
            Get Started
          </a>
        </div>

        {/* Additional marketing content */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="glass-card p-6">
            <h3 className="text-xl font-semibold mb-3">Focus Mode</h3>
            <p className="text-gray-300">Minimize distractions and concentrate on what matters most.</p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-xl font-semibold mb-3">Smart Organization</h3>
            <p className="text-gray-300">Intelligent task categorization and prioritization tools.</p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-xl font-semibold mb-3">Cross-Device Sync</h3>
            <p className="text-gray-300">Access your tasks anywhere, anytime, on any device.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
