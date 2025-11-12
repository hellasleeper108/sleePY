'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { analyticsAPI } from '@/lib/api';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { TrendingUp, Users, Activity, Award, Clock, Target, Loader2 } from 'lucide-react';

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyticsAPI.getDashboard();
      setDashboard(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics. Admin access required.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-cyber-teal mx-auto mb-4" />
            <p className="text-gray-400">Loading analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="cyber-card p-8 text-center">
            <h2 className="text-2xl font-bold text-red-400 mb-4">Access Denied</h2>
            <p className="text-gray-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboard) return null;

  const { engagement, time_per_challenge, completion_by_topic, weekly_active, xp_distribution } = dashboard;

  // Color palette
  const COLORS = ['#14b8a6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#6366f1'];

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">
              <span className="glow-text">Analytics Dashboard</span>
            </h1>
            <p className="text-gray-400">Comprehensive platform metrics and user engagement insights</p>
          </div>

          {/* Engagement Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="cyber-card p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="w-10 h-10 rounded-lg bg-teal-gradient flex items-center justify-center">
                  <Users className="w-6 h-6" />
                </div>
                <span className="text-xs text-gray-500">DAU</span>
              </div>
              <div className="text-2xl font-bold text-cyber-teal-light">{engagement.daily_active_users}</div>
              <div className="text-xs text-gray-400 mt-1">Daily Active Users</div>
            </div>

            <div className="cyber-card p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="w-10 h-10 rounded-lg bg-purple-gradient flex items-center justify-center">
                  <Activity className="w-6 h-6" />
                </div>
                <span className="text-xs text-gray-500">WAU</span>
              </div>
              <div className="text-2xl font-bold text-purple-400">{engagement.weekly_active_users}</div>
              <div className="text-xs text-gray-400 mt-1">Weekly Active Users</div>
            </div>

            <div className="cyber-card p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="w-10 h-10 rounded-lg bg-pink-gradient flex items-center justify-center">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <span className="text-xs text-gray-500">MAU</span>
              </div>
              <div className="text-2xl font-bold text-pink-400">{engagement.monthly_active_users}</div>
              <div className="text-xs text-gray-400 mt-1">Monthly Active Users</div>
            </div>

            <div className="cyber-card p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                  <Award className="w-6 h-6" />
                </div>
                <span className="text-xs text-gray-500">Total</span>
              </div>
              <div className="text-2xl font-bold text-yellow-400">{engagement.total_active_users}</div>
              <div className="text-xs text-gray-400 mt-1">Total Active Users</div>
            </div>
          </div>

          {/* Additional Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="cyber-card p-6">
              <div className="flex items-center gap-3 mb-2">
                <Target className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-400">Challenges Completed</span>
              </div>
              <div className="text-2xl font-bold text-green-400">{engagement.total_challenges_completed}</div>
              <div className="text-xs text-gray-500 mt-1">
                {engagement.challenges_completed_this_week} this week
              </div>
            </div>

            <div className="cyber-card p-6">
              <div className="flex items-center gap-3 mb-2">
                <Activity className="w-5 h-5 text-blue-400" />
                <span className="text-sm text-gray-400">Engagement Rate</span>
              </div>
              <div className="text-2xl font-bold text-blue-400">{engagement.engagement_rate_weekly}%</div>
              <div className="text-xs text-gray-500 mt-1">Weekly active / Total users</div>
            </div>

            <div className="cyber-card p-6">
              <div className="flex items-center gap-3 mb-2">
                <Clock className="w-5 h-5 text-purple-400" />
                <span className="text-sm text-gray-400">Avg Hints/Challenge</span>
              </div>
              <div className="text-2xl font-bold text-purple-400">{engagement.avg_hints_per_challenge}</div>
              <div className="text-xs text-gray-500 mt-1">Mentor AI usage</div>
            </div>
          </div>

          {/* Charts Row 1: Weekly Active Users & Completion by Topic */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Weekly Active Users */}
            <div className="cyber-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-cyber-teal" />
                Weekly Active Users Trend
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={weekly_active}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="week_label" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#e5e7eb' }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="active_users"
                    stroke="#14b8a6"
                    strokeWidth={2}
                    name="Active Users"
                  />
                  <Line
                    type="monotone"
                    dataKey="users_completed_challenges"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    name="Completed Challenges"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Completion by Topic */}
            <div className="cyber-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-purple-400" />
                Completion Rate by Topic
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={completion_by_topic}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="topic" stroke="#9ca3af" angle={-45} textAnchor="end" height={80} />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#e5e7eb' }}
                  />
                  <Legend />
                  <Bar dataKey="completion_rate" fill="#8b5cf6" name="Completion Rate %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Charts Row 2: Time per Challenge & XP Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Time per Challenge */}
            <div className="cyber-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-pink-400" />
                Average Time per Challenge (Top 10)
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={time_per_challenge.slice(0, 10)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="title" stroke="#9ca3af" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#e5e7eb' }}
                  />
                  <Legend />
                  <Bar dataKey="avg_time_minutes" fill="#ec4899" name="Avg Time (min)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* XP Distribution */}
            <div className="cyber-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-400" />
                XP Distribution
              </h3>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-sm text-gray-400">Total Users</div>
                  <div className="text-2xl font-bold text-gray-200">{xp_distribution.total_users}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Avg XP</div>
                  <div className="text-2xl font-bold text-cyber-teal-light">{xp_distribution.avg_xp}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Max XP</div>
                  <div className="text-2xl font-bold text-yellow-400">{xp_distribution.max_xp}</div>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={xp_distribution.distribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.bracket}: ${entry.count}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {xp_distribution.distribution.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Challenge Time Details Table */}
          <div className="cyber-card p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-cyber-teal" />
              Challenge Time Statistics
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-cyber-gray-medium">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Challenge</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Difficulty</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Category</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Attempts</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Avg Time</th>
                    <th className="px-4 py-3 text-right text-sm font-semibold text-gray-300">Completion Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-cyber-gray-medium">
                  {time_per_challenge.slice(0, 15).map((challenge: any) => (
                    <tr key={challenge.challenge_id} className="hover:bg-cyber-gray-medium/30">
                      <td className="px-4 py-3 text-sm text-gray-200">{challenge.title}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className="px-2 py-1 rounded-full text-xs bg-purple-500/20 text-purple-400">
                          {challenge.difficulty}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-400">{challenge.category}</td>
                      <td className="px-4 py-3 text-sm text-right text-gray-300">{challenge.total_attempts}</td>
                      <td className="px-4 py-3 text-sm text-right text-cyan-400">
                        {challenge.avg_time_minutes} min
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-green-400">
                        {challenge.completion_rate}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
