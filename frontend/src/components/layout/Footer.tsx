import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-black border-t border-white/10 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <div className="text-xl font-bold gradient-text">FocusFlow</div>
            <p className="text-gray-500 text-sm mt-1">Your productivity companion</p>
          </div>

          <div className="flex flex-wrap justify-center gap-6">
            <a href="/about" className="text-gray-400 hover:text-white transition-colors text-sm">
              About
            </a>
            <a href="/features" className="text-gray-400 hover:text-white transition-colors text-sm">
              Features
            </a>
            <a href="/pricing" className="text-gray-400 hover:text-white transition-colors text-sm">
              Pricing
            </a>
            <a href="/privacy" className="text-gray-400 hover:text-white transition-colors text-sm">
              Privacy
            </a>
            <a href="/terms" className="text-gray-400 hover:text-white transition-colors text-sm">
              Terms
            </a>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-white/10 text-center">
          <p className="text-gray-500 text-sm">
            © {new Date().getFullYear()} FocusFlow. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;