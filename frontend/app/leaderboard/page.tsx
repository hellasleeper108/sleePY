'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { leaderboardAPI } from '@/lib/api';
import { Trophy, TrendingUp, Calendar, Target, Medal } from 'lucide-react';
import { formatXP } from '@/lib/utils';

type LeaderboardType = 'global' | 'weekly' | 'topic';

export default function LeaderboardPage() {
  const [activeTab, setActiveTab] = useState<LeaderboardType>('global');
  const [entries, setEntries] = useState<any[]>([]);
  const [userRank, setUserRank] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
    loadUserRank();
  }, [activeTab]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      let data;
      if (activeTab === 'global') {
        data = await leaderboardAPI.getGlobal();
      } else if (activeTab === 'weekly') {
        data = await leaderboardAPI.getWeekly();
      } else {
        data = await leaderboardAPI.getTopic('basics');
      }
      setEntries(data.entries || []);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserRank = async () => {
    try {
      const data = await leaderboardAPI.getMyRank();
      setUserRank(data);
    } catch (error) {
      console.error('Failed to load user rank:', error);
    }
  };

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'text-yellow-400';
    if (rank === 2) return 'text-gray-300';
    if (rank === 3) return 'text-orange-400';
    return 'text-gray-400';
  };

  const getRankIcon = (rank: number) => {
    if (rank <= 3) {
      return <Medal className={`w-6 h-6 ${getRankColor(rank)}`} />;
    }
    return <span className="text-gray-500 font-semibold">#{rank}</span>;
  };

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                <span className="glow-text">Leaderboards</span>
              </h1>
              <p className="text-gray-400">Compete with the best Python developers</p>
            </div>
            {userRank && (
              <div className="bg-cyber-gray-dark px-6 py-4 rounded-lg border border-cyber-teal shadow-cyber">
                <div className="text-sm text-gray-400 mb-1">Your Global Rank</div>
                <div className="flex items-center gap-2">
                  <Trophy className="w-6 h-6 text-cyber-teal" />
                  <span className="text-3xl font-bold text-cyber-teal-light">
                    #{userRank.global_rank || '-'}
                  </span>
                  <span className="text-gray-500 text-sm">/ {userRank.total_users}</span>
                </div>
              </div>
            )}
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-cyber-gray-medium pb-2">
            <button
              onClick={() => setActiveTab('global')}
              className={`px-6 py-3 rounded-t-lg font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'global'
                  ? 'bg-teal-gradient text-white shadow-cyber'
                  : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
              }`}
            >
              <Trophy className="w-5 h-5" />
              Global
            </button>
            <button
              onClick={() => setActiveTab('weekly')}
              className={`px-6 py-3 rounded-t-lg font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'weekly'
                  ? 'bg-teal-gradient text-white shadow-cyber'
                  : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
              }`}
            >
              <Calendar className="w-5 h-5" />
              Weekly
            </button>
            <button
              onClick={() => setActiveTab('topic')}
              className={`px-6 py-3 rounded-t-lg font-semibold transition-all flex items-center gap-2 ${
                activeTab === 'topic'
                  ? 'bg-teal-gradient text-white shadow-cyber'
                  : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
              }`}
            >
              <Target className="w-5 h-5" />
              Topic
            </button>
          </div>

          {/* Leaderboard */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-teal"></div>
            </div>
          ) : (
            <div className="cyber-card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-cyber-gray-medium">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Rank</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Player</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Level</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">
                        {activeTab === 'weekly' ? 'Weekly XP' : activeTab === 'topic' ? 'Topic XP' : 'Total XP'}
                      </th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Challenges</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-cyber-gray-medium">
                    {entries.map((entry) => (
                      <tr
                        key={entry.user_id}
                        className="hover:bg-cyber-gray-medium/50 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            {getRankIcon(entry.rank)}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-semibold text-gray-100">{entry.username}</div>
                            <div className="text-sm text-gray-400">{entry.full_name}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-purple-gradient flex items-center justify-center text-sm font-bold">
                              {entry.level}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2 text-cyber-teal-light font-semibold">
                            <TrendingUp className="w-4 h-4" />
                            {formatXP(
                              entry.weekly_xp !== undefined
                                ? entry.weekly_xp
                                : entry.topic_xp !== undefined
                                ? entry.topic_xp
                                : entry.xp
                            )}
                          </div>
                          {(entry.weekly_xp !== undefined || entry.topic_xp !== undefined) && (
                            <div className="text-xs text-gray-500 mt-1">
                              {formatXP(entry.total_xp)} total
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-gray-300">{entry.challenges_completed}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {entries.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <p>No leaderboard data available yet.</p>
                </div>
              )}
            </div>
          )}

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="cyber-card p-6">
              <h3 className="font-semibold text-lg mb-2 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-400" />
                Global Leaderboard
              </h3>
              <p className="text-sm text-gray-400">
                Ranked by total XP earned all-time. Complete challenges and earn achievements to climb the ranks!
              </p>
            </div>
            <div className="cyber-card p-6">
              <h3 className="font-semibold text-lg mb-2 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-purple-400" />
                Weekly Leaderboard
              </h3>
              <p className="text-sm text-gray-400">
                Resets every 7 days. Race to earn the most XP this week and prove you're the most active learner!
              </p>
            </div>
            <div className="cyber-card p-6">
              <h3 className="font-semibold text-lg mb-2 flex items-center gap-2">
                <Target className="w-5 h-5 text-pink-400" />
                Topic Leaderboards
              </h3>
              <p className="text-sm text-gray-400">
                Compete in specific categories like Data Structures, Algorithms, and OOP to show your expertise!
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
