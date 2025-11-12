'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { LearningPath } from '@/lib/api';
import { pathAPI } from '@/lib/api';
import { BookOpen, Clock, Zap, Award } from 'lucide-react';
import { getDifficultyBadgeColor, formatXP } from '@/lib/utils';
import Link from 'next/link';

export default function PathsPage() {
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPaths();
  }, []);

  const loadPaths = async () => {
    try {
      const data = await pathAPI.getAll();
      setPaths(data);
    } catch (error) {
      console.error('Failed to load learning paths:', error);
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

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">
              <span className="glow-text">Learning Paths</span>
            </h1>
            <p className="text-gray-400">Structured courses to master Python concepts</p>
          </div>

          {/* Paths Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {paths.map((path) => (
              <Link
                key={path.id}
                href={`/paths/${path.id}`}
                className="cyber-card-hover p-6 block"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold mb-2">{path.title}</h3>
                    <p className="text-sm text-gray-400 line-clamp-2">{path.description}</p>
                  </div>
                  <div className="ml-4">
                    <div className="w-12 h-12 rounded-lg bg-purple-gradient flex items-center justify-center shadow-purple">
                      <BookOpen className="w-6 h-6" />
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 mb-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getDifficultyBadgeColor(path.difficulty)}`}>
                    {path.difficulty.toUpperCase()}
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyber-gray-medium text-gray-300">
                    {path.topic.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-cyber-gray-medium">
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Clock className="w-4 h-4" />
                    <span>{path.estimated_hours}h</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-cyber-teal-light">
                    <Zap className="w-4 h-4" />
                    <span>{formatXP(path.xp_reward)} XP</span>
                  </div>
                  {path.badge_id && (
                    <div className="flex items-center gap-2 text-sm text-purple-400 col-span-2">
                      <Award className="w-4 h-4" />
                      <span>Earn exclusive badge</span>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>

          {paths.length === 0 && (
            <div className="text-center py-12">
              <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">No learning paths available yet.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
