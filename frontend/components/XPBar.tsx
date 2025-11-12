'use client';

import { calculateXPForLevel, calculateXPProgress, formatXP } from '@/lib/utils';
import { Zap } from 'lucide-react';

interface XPBarProps {
  currentXP: number;
  currentLevel: number;
  showDetails?: boolean;
  className?: string;
}

export default function XPBar({ currentXP, currentLevel, showDetails = true, className = '' }: XPBarProps) {
  const xpForCurrentLevel = (currentLevel - 1) * 100;
  const xpForNextLevel = currentLevel * 100;
  const xpIntoLevel = currentXP - xpForCurrentLevel;
  const xpNeeded = xpForNextLevel - xpForCurrentLevel;
  const progress = calculateXPProgress(currentXP, currentLevel);

  return (
    <div className={className}>
      {showDetails && (
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-purple-gradient flex items-center justify-center">
              <span className="text-sm font-bold">{currentLevel}</span>
            </div>
            <span className="text-sm font-semibold text-gray-300">Level {currentLevel}</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-gray-400">
            <Zap className="w-4 h-4 text-cyber-teal-light" />
            <span>
              {formatXP(xpIntoLevel)} / {formatXP(xpNeeded)} XP
            </span>
          </div>
        </div>
      )}

      <div className="xp-bar relative">
        <div
          className="xp-fill"
          style={{ width: `${progress}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse-slow" />
        </div>
      </div>

      {showDetails && (
        <div className="mt-2 text-xs text-gray-500 text-center">
          {xpNeeded - xpIntoLevel} XP to Level {currentLevel + 1}
        </div>
      )}
    </div>
  );
}
