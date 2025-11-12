'use client';

import { useState, useEffect } from 'react';
import { Challenge, Progress } from '@/lib/api';
import { challengeAPI, progressAPI } from '@/lib/api';
import { getDifficultyBadgeColor, formatXP } from '@/lib/utils';
import { Zap, Lock, CheckCircle2, Target, Code } from 'lucide-react';
import Link from 'next/link';

interface ChallengeWithProgress extends Challenge {
  progress?: Progress;
}

export default function QuestBoard() {
  const [challenges, setChallenges] = useState<ChallengeWithProgress[]>([]);
  const [filter, setFilter] = useState<'all' | 'available' | 'completed'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChallenges();
  }, []);

  const loadChallenges = async () => {
    try {
      const [challengesData, progressData] = await Promise.all([
        challengeAPI.getAll(),
        progressAPI.getMyProgress(),
      ]);

      // Merge challenges with progress
      const merged = challengesData.map((challenge) => ({
        ...challenge,
        progress: progressData.find((p) => p.challenge_id === challenge.id),
      }));

      setChallenges(merged);
    } catch (error) {
      console.error('Failed to load challenges:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredChallenges = challenges.filter((challenge) => {
    if (filter === 'completed') return challenge.progress?.is_completed;
    if (filter === 'available') return !challenge.progress?.is_completed;
    return true;
  });

  const stats = {
    total: challenges.length,
    completed: challenges.filter((c) => c.progress?.is_completed).length,
    available: challenges.filter((c) => !c.progress?.is_completed).length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-teal"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold mb-2">
            <span className="glow-text">Quest Board</span>
          </h2>
          <p className="text-gray-400">Choose your next coding challenge</p>
        </div>
        <div className="flex items-center gap-2 bg-cyber-gray-dark px-4 py-2 rounded-lg">
          <Target className="w-5 h-5 text-cyber-teal" />
          <span className="text-sm text-gray-400">
            {stats.completed} / {stats.total} Completed
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-semibold transition-all ${
            filter === 'all'
              ? 'bg-teal-gradient text-white shadow-cyber'
              : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
          }`}
        >
          All ({stats.total})
        </button>
        <button
          onClick={() => setFilter('available')}
          className={`px-4 py-2 rounded-lg font-semibold transition-all ${
            filter === 'available'
              ? 'bg-teal-gradient text-white shadow-cyber'
              : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
          }`}
        >
          Available ({stats.available})
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded-lg font-semibold transition-all ${
            filter === 'completed'
              ? 'bg-teal-gradient text-white shadow-cyber'
              : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
          }`}
        >
          Completed ({stats.completed})
        </button>
      </div>

      {/* Challenges Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredChallenges.map((challenge) => {
          const isCompleted = challenge.progress?.is_completed;
          const isLocked = false; // You can implement level requirements here

          return (
            <Link
              key={challenge.id}
              href={`/arena/${challenge.id}`}
              className={`cyber-card-hover p-6 block ${isLocked ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-semibold">{challenge.title}</h3>
                    {isCompleted && (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    )}
                    {isLocked && (
                      <Lock className="w-5 h-5 text-gray-500" />
                    )}
                  </div>
                  <p className="text-sm text-gray-400 line-clamp-2">{challenge.description}</p>
                </div>
                <div className="ml-4">
                  <div className="w-12 h-12 rounded-lg bg-purple-gradient flex items-center justify-center shadow-purple">
                    <Code className="w-6 h-6" />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getDifficultyBadgeColor(challenge.difficulty)}`}>
                    {challenge.difficulty.toUpperCase()}
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyber-gray-medium text-gray-300">
                    {challenge.category.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center gap-1 text-cyber-teal-light font-semibold">
                  <Zap className="w-4 h-4" />
                  <span>{formatXP(challenge.xp_reward)} XP</span>
                </div>
              </div>

              {challenge.progress && !isCompleted && (
                <div className="mt-4 pt-4 border-t border-cyber-gray-medium">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Attempts: {challenge.progress.attempts}</span>
                    <span className="text-yellow-400">In Progress</span>
                  </div>
                </div>
              )}

              {isCompleted && challenge.progress && (
                <div className="mt-4 pt-4 border-t border-cyber-gray-medium">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-green-400 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" />
                      Completed
                    </span>
                    <span className="text-gray-400">
                      {formatXP(challenge.progress.xp_earned)} XP earned
                    </span>
                  </div>
                </div>
              )}
            </Link>
          );
        })}
      </div>

      {filteredChallenges.length === 0 && (
        <div className="text-center py-12">
          <Target className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No challenges found in this category.</p>
        </div>
      )}
    </div>
  );
}
