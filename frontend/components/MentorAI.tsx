'use client';

import { useState } from 'react';
import { mentorAPI } from '@/lib/api';
import { Lightbulb, Loader2, AlertCircle, TrendingUp } from 'lucide-react';

interface MentorAIProps {
  challengeId: number;
  userCode?: string;
  errorMessage?: string;
}

interface HintData {
  hint_text: string;
  hint_number: number;
  bonus_multiplier: number;
  bonus_percentage: number;
  message: string;
}

export default function MentorAI({ challengeId, userCode, errorMessage }: MentorAIProps) {
  const [hint, setHint] = useState<HintData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hintCount, setHintCount] = useState(0);

  const handleGetHint = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await mentorAPI.getHint(challengeId, userCode, errorMessage);
      setHint(response);
      setHintCount(response.hint_number);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get hint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getBonusColor = (percentage: number) => {
    if (percentage >= 20) return 'text-green-400';
    if (percentage >= 10) return 'text-yellow-400';
    if (percentage >= 5) return 'text-orange-400';
    return 'text-gray-400';
  };

  return (
    <div className="cyber-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-purple-gradient flex items-center justify-center">
            <Lightbulb className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Mentor AI</h3>
            <p className="text-sm text-gray-400">Get hints without losing bonus XP</p>
          </div>
        </div>
        <button
          onClick={handleGetHint}
          disabled={loading}
          className="cyber-button flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Thinking...
            </>
          ) : (
            <>
              <Lightbulb className="w-4 h-4" />
              Ask Mentor
            </>
          )}
        </button>
      </div>

      {/* Bonus XP indicator */}
      {hintCount > 0 && hint && (
        <div className="flex items-center gap-2 p-3 bg-cyber-gray-medium rounded-lg border border-cyber-teal-dark">
          <TrendingUp className={`w-5 h-5 ${getBonusColor(hint.bonus_percentage)}`} />
          <div className="flex-1">
            <div className="text-sm font-semibold">
              {hint.bonus_percentage > 0 ? (
                <span className={getBonusColor(hint.bonus_percentage)}>
                  +{hint.bonus_percentage}% XP Bonus
                </span>
              ) : (
                <span className="text-gray-400">No bonus XP (3+ hints used)</span>
              )}
            </div>
            <div className="text-xs text-gray-500">
              {hintCount} hint{hintCount !== 1 ? 's' : ''} used • Multiplier: {hint.bonus_multiplier}x
            </div>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="text-sm font-semibold text-red-400">Error</div>
            <div className="text-sm text-red-300">{error}</div>
          </div>
        </div>
      )}

      {/* Hint display */}
      {hint && !loading && (
        <div className="space-y-3">
          <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-semibold text-purple-400">
                Hint #{hint.hint_number}
              </span>
            </div>
            <p className="text-gray-200 leading-relaxed">{hint.hint_text}</p>
          </div>

          {hint.message && (
            <div className="text-sm text-center text-gray-400 italic">{hint.message}</div>
          )}
        </div>
      )}

      {/* Info text */}
      {!hint && !loading && (
        <div className="text-sm text-gray-400 text-center p-4 bg-cyber-gray-medium rounded-lg">
          <p>
            Need help? Ask the Mentor AI for hints!
            <br />
            <span className="text-cyber-teal-light">
              Fewer hints = More bonus XP when you complete the challenge
            </span>
          </p>
          <div className="mt-2 text-xs text-gray-500">
            0 hints: +20% XP • 1 hint: +10% XP • 2 hints: +5% XP • 3+ hints: No bonus
          </div>
        </div>
      )}
    </div>
  );
}
