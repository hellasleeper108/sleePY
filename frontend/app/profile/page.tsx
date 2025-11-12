'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { User, Badge } from '@/lib/api';
import { authAPI } from '@/lib/api';
import XPBar from '@/components/XPBar';
import { User as UserIcon, Mail, Calendar, Award } from 'lucide-react';
import { formatRelativeDate } from '@/lib/utils';

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-teal"></div>
          </div>
        </main>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-400 py-12">
            Failed to load profile.
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Profile Header */}
          <div className="cyber-card p-8">
            <div className="flex items-start gap-6">
              <div className="w-24 h-24 rounded-full bg-teal-gradient flex items-center justify-center shadow-cyber-lg text-3xl font-bold">
                {user.username.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold mb-2">{user.full_name}</h1>
                <div className="flex items-center gap-4 text-gray-400 mb-4">
                  <div className="flex items-center gap-2">
                    <UserIcon className="w-4 h-4" />
                    <span>@{user.username}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    <span>{user.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>Joined {formatRelativeDate(user.created_at)}</span>
                  </div>
                </div>
                <XPBar currentXP={user.xp} currentLevel={user.level} />
              </div>
            </div>
          </div>

          {/* Account Settings */}
          <div className="cyber-card p-6">
            <h2 className="text-2xl font-bold mb-4">Account Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={user.full_name}
                  disabled
                  className="cyber-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user.email}
                  disabled
                  className="cyber-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={user.username}
                  disabled
                  className="cyber-input w-full"
                />
              </div>
            </div>
          </div>

          {/* Stats Summary */}
          <div className="cyber-card p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <Award className="w-6 h-6 text-cyber-teal" />
              Your Progress
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-cyber-gray-medium rounded-lg">
                <div className="text-3xl font-bold text-cyber-teal-light mb-1">{user.level}</div>
                <div className="text-sm text-gray-400">Current Level</div>
              </div>
              <div className="text-center p-4 bg-cyber-gray-medium rounded-lg">
                <div className="text-3xl font-bold text-purple-400 mb-1">{user.xp.toLocaleString()}</div>
                <div className="text-sm text-gray-400">Total XP</div>
              </div>
              <div className="text-center p-4 bg-cyber-gray-medium rounded-lg">
                <div className="text-3xl font-bold text-yellow-400 mb-1">-</div>
                <div className="text-sm text-gray-400">Achievements</div>
              </div>
              <div className="text-center p-4 bg-cyber-gray-medium rounded-lg">
                <div className="text-3xl font-bold text-pink-400 mb-1">-</div>
                <div className="text-sm text-gray-400">Badges</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
