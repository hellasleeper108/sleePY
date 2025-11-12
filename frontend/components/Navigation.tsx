'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Target, BookOpen, Trophy, User, LogOut } from 'lucide-react';

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', icon: Home, label: 'Dashboard' },
    { href: '/quests', icon: Target, label: 'Quest Board' },
    { href: '/paths', icon: BookOpen, label: 'Learning Paths' },
    { href: '/achievements', icon: Trophy, label: 'Achievements' },
    { href: '/profile', icon: User, label: 'Profile' },
  ];

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <nav className="bg-cyber-gray-dark border-b border-cyber-gray-medium">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg bg-teal-gradient flex items-center justify-center shadow-cyber">
              <Target className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold glow-text">PyQuest</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    active
                      ? 'bg-teal-gradient text-white shadow-cyber'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-cyber-gray-medium'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="hidden md:inline">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* User Menu */}
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-cyber-gray-medium transition-all">
            <LogOut className="w-5 h-5" />
            <span className="hidden md:inline">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
