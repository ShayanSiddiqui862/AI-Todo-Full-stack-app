'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { logout } = useAuth();

  const navItems = [
    { name: 'All Tasks', href: '/dashboard', icon: '📋' },
    { name: 'Completed', href: '/dashboard/completed', icon: '✅' },
    { name: 'Pending', href: '/dashboard/pending', icon: '⏳' },
    { name: 'Projects', href: '/dashboard/projects', icon: '📁' },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <aside
      className={`fixed top-16 left-0 h-[calc(100vh-4rem)] bg-black/80 backdrop-blur-md border-r border-white/10 z-40 transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="p-4">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="mb-6 text-gray-400 hover:text-white transition-colors"
        >
          {isCollapsed ? '«' : '»'} {/* Collapse/expand toggle */}
        </button>

        <nav>
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 w-full p-3 rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'bg-white/10 text-white'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  {!isCollapsed && <span>{item.name}</span>}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="absolute bottom-4 left-0 w-full px-4">
          <button
            onClick={logout}
            className="w-full py-2 px-4 text-left text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
          >
            {!isCollapsed ? 'Logout' : '🚪'}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;