'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { Achievement } from '@/lib/api';
import { gameAPI } from '@/lib/api';
import { Trophy, Lock, CheckCircle, Zap } from 'lucide-react';
import { formatXP } from '@/lib/utils';

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [userAchievements, setUserAchievements] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    try {
      const [allAchievements, userAchiev] = await Promise.all([
        gameAPI.getAchievements(),
        gameAPI.getUserAchievements(),
      ]);
      setAchievements(allAchievements);
      setUserAchievements(new Set(userAchiev.map((a: any) => a.achievement_id)));
    } catch (error) {
      console.error('Failed to load achievements:', error);
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

  const unlockedCount = userAchievements.size;

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                <span className="glow-text">Achievements</span>
              </h1>
              <p className="text-gray-400">Track your milestones and progress</p>
            </div>
            <div className="flex items-center gap-2 bg-cyber-gray-dark px-4 py-2 rounded-lg">
              <Trophy className="w-5 h-5 text-yellow-400" />
              <span className="text-sm">
                {unlockedCount} / {achievements.length} Unlocked
              </span>
            </div>
          </div>

          {/* Achievements Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((achievement) => {
              const isUnlocked = userAchievements.has(achievement.id);

              return (
                <div
                  key={achievement.id}
                  className={`cyber-card p-6 ${isUnlocked ? 'border-yellow-500/50 shadow-yellow-500/20' : 'opacity-75'}`}
                >
                  <div className="flex items-start gap-4">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                      isUnlocked ? 'bg-yellow-500/20 shadow-lg shadow-yellow-500/30' : 'bg-cyber-gray-medium'
                    }`}>
                      {isUnlocked ? (
                        <Trophy className="w-8 h-8 text-yellow-400" />
                      ) : (
                        <Lock className="w-8 h-8 text-gray-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-1">{achievement.name}</h3>
                      <p className="text-sm text-gray-400 mb-3">{achievement.description}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1 text-cyber-teal-light">
                          <Zap className="w-4 h-4" />
                          <span>{formatXP(achievement.xp_reward)} XP</span>
                        </div>
                        {isUnlocked && (
                          <div className="flex items-center gap-1 text-green-400">
                            <CheckCircle className="w-4 h-4" />
                            <span>Unlocked</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {achievements.length === 0 && (
            <div className="text-center py-12">
              <Trophy className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No achievements available yet.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
