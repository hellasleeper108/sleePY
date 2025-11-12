'use client';

import { useState, useEffect } from 'react';
import { User, GameStats, DailyStreak } from '@/lib/api';
import { authAPI, gameAPI } from '@/lib/api';
import XPBar from './XPBar';
import { Trophy, Zap, Target, Flame, Gift, Award, TrendingUp } from 'lucide-react';
import { formatXP } from '@/lib/utils';

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<GameStats | null>(null);
  const [streak, setStreak] = useState<DailyStreak | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [userData, statsData, streakData] = await Promise.all([
        authAPI.getCurrentUser(),
        gameAPI.getStats(),
        gameAPI.getStreak(),
      ]);
      setUser(userData);
      setStats(statsData);
      setStreak(streakData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-teal"></div>
      </div>
    );
  }

  if (!user || !stats) {
    return (
      <div className="text-center text-gray-400 py-12">
        Failed to load dashboard. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="cyber-card p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, <span className="glow-text">{user.username}</span>
            </h1>
            <p className="text-gray-400">Ready to level up your Python skills?</p>
          </div>
          <div className="flex items-center gap-2 bg-cyber-gray-medium px-4 py-2 rounded-lg">
            <Flame className="w-5 h-5 text-orange-400" />
            <div>
              <div className="text-2xl font-bold text-orange-400">{streak?.current_streak || 0}</div>
              <div className="text-xs text-gray-400">Day Streak</div>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <XPBar currentXP={user.xp} currentLevel={user.level} />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total XP */}
        <div className="cyber-card p-6 hover:scale-105 transition-transform">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-teal-gradient flex items-center justify-center shadow-cyber">
              <Zap className="w-6 h-6" />
            </div>
            <TrendingUp className="w-5 h-5 text-cyber-teal-light" />
          </div>
          <div className="stat-value">{formatXP(stats.total_xp)}</div>
          <div className="text-sm text-gray-400 mt-1">Total XP</div>
        </div>

        {/* Challenges Completed */}
        <div className="cyber-card p-6 hover:scale-105 transition-transform">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-purple-gradient flex items-center justify-center shadow-purple">
              <Target className="w-6 h-6" />
            </div>
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <div className="stat-value text-purple-400">{stats.challenges_completed}</div>
          <div className="text-sm text-gray-400 mt-1">Challenges Completed</div>
        </div>

        {/* Achievements */}
        <div className="cyber-card p-6 hover:scale-105 transition-transform">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-yellow-500/20 flex items-center justify-center shadow-lg shadow-yellow-500/30">
              <Trophy className="w-6 h-6 text-yellow-400" />
            </div>
            <TrendingUp className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="stat-value text-yellow-400">{stats.achievements_unlocked}</div>
          <div className="text-sm text-gray-400 mt-1">Achievements</div>
        </div>

        {/* Loot Chests */}
        <div className="cyber-card p-6 hover:scale-105 transition-transform">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-pink-500/20 flex items-center justify-center shadow-lg shadow-pink-500/30">
              <Gift className="w-6 h-6 text-pink-400" />
            </div>
            <TrendingUp className="w-5 h-5 text-pink-400" />
          </div>
          <div className="stat-value text-pink-400">{stats.total_chests_opened}</div>
          <div className="text-sm text-gray-400 mt-1">Loot Chests Opened</div>
        </div>
      </div>

      {/* Streak Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Flame className="w-6 h-6 text-orange-400" />
            <h3 className="text-xl font-semibold">Daily Streak</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Current Streak</span>
              <span className="text-2xl font-bold text-orange-400">{streak?.current_streak || 0} days</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Longest Streak</span>
              <span className="text-xl font-semibold text-gray-300">{streak?.longest_streak || 0} days</span>
            </div>
            <div className="mt-4 pt-4 border-t border-cyber-gray-medium">
              <p className="text-sm text-gray-400">
                Keep your streak alive by completing challenges daily! Earn bonus XP up to 50 XP per day.
              </p>
            </div>
          </div>
        </div>

        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Award className="w-6 h-6 text-purple-400" />
            <h3 className="text-xl font-semibold">Badges Earned</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Badges</span>
              <span className="text-2xl font-bold text-purple-400">{stats.badges_earned}</span>
            </div>
            <div className="mt-4 pt-4 border-t border-cyber-gray-medium">
              <p className="text-sm text-gray-400">
                Earn badges by completing learning paths and reaching milestones. Each badge proves your mastery!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
