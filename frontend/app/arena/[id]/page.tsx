'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import MentorAI from '@/components/MentorAI';
import { challengeAPI, progressAPI } from '@/lib/api';
import { Challenge } from '@/lib/api';
import { getDifficultyBadgeColor, formatXP } from '@/lib/utils';
import {
  Code,
  Play,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowLeft,
  Zap,
  TrendingUp
} from 'lucide-react';
import Link from 'next/link';

export default function ArenaPage() {
  const params = useParams();
  const router = useRouter();
  const challengeId = parseInt(params.id as string);

  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [code, setCode] = useState('');
  const [output, setOutput] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChallenge();
  }, [challengeId]);

  const loadChallenge = async () => {
    try {
      const data = await challengeAPI.getById(challengeId);
      setChallenge(data);
      setCode(data.starter_code || '# Write your solution here\n');
    } catch (err: any) {
      setError('Failed to load challenge');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!code.trim()) {
      setOutput('Please write some code first!');
      return;
    }

    setIsSubmitting(true);
    setOutput('');
    setResult(null);
    setError(null);

    try {
      const response = await progressAPI.submitCode(challengeId, code);
      setResult(response);

      if (response.success) {
        setOutput(
          `✅ ${response.message}\n\n` +
          `XP Earned: ${response.xp_earned}\n` +
          `Attempts: ${response.attempts}\n` +
          (response.leveled_up ? `\n🎉 LEVEL UP! You're now level ${response.new_level}!\n` : '') +
          (response.loot_dropped ? `\n🎁 Loot chest dropped! Rarity: ${response.loot_dropped.rarity}\n` : '') +
          (response.bonus_xp ? `\n${response.bonus_xp.message}\n` : '') +
          (response.achievements_unlocked?.length ? `\n🏆 New achievements unlocked: ${response.achievements_unlocked.map((a: any) => a.name).join(', ')}\n` : '')
        );
      } else {
        setOutput(`❌ ${response.message}\n\nAttempts: ${response.attempts}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Submission failed');
      setOutput('❌ Submission failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-teal"></div>
        </div>
      </div>
    );
  }

  if (!challenge) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Challenge not found</h1>
            <Link href="/quests" className="cyber-button inline-flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Quests
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <Link
              href="/quests"
              className="flex items-center gap-2 text-gray-400 hover:text-gray-200 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Quests
            </Link>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getDifficultyBadgeColor(challenge.difficulty)}`}>
                {challenge.difficulty.toUpperCase()}
              </span>
              <div className="flex items-center gap-1 text-cyber-teal-light font-semibold">
                <Zap className="w-4 h-4" />
                <span>{formatXP(challenge.xp_reward)} XP</span>
              </div>
            </div>
          </div>

          {/* Challenge Title */}
          <div>
            <h1 className="text-3xl font-bold mb-2">
              <span className="glow-text">{challenge.title}</span>
            </h1>
            <p className="text-gray-400">{challenge.description}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Instructions and Mentor */}
            <div className="space-y-6">
              {/* Instructions */}
              <div className="cyber-card p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Code className="w-5 h-5 text-cyber-teal" />
                  Instructions
                </h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-gray-300 whitespace-pre-line">{challenge.instructions}</p>
                </div>
              </div>

              {/* Mentor AI */}
              <MentorAI
                challengeId={challengeId}
                userCode={code}
                errorMessage={error || undefined}
              />
            </div>

            {/* Right Column - Code Editor and Output */}
            <div className="space-y-6">
              {/* Code Editor */}
              <div className="cyber-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    <Code className="w-5 h-5 text-purple-400" />
                    Code Editor
                  </h2>
                  <button
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="cyber-button flex items-center gap-2"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Submit Solution
                      </>
                    )}
                  </button>
                </div>

                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full h-[400px] bg-cyber-gray-dark text-gray-100 font-mono text-sm p-4 rounded-lg border border-cyber-gray-medium focus:border-cyber-teal focus:outline-none resize-none"
                  placeholder="Write your Python code here..."
                  spellCheck={false}
                />
              </div>

              {/* Output */}
              {output && (
                <div className="cyber-card p-6">
                  <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    {result?.success ? (
                      <CheckCircle2 className="w-5 h-5 text-green-400" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-400" />
                    )}
                    Output
                  </h2>
                  <pre className="bg-cyber-gray-dark text-gray-100 p-4 rounded-lg border border-cyber-gray-medium overflow-x-auto whitespace-pre-wrap">
                    {output}
                  </pre>

                  {result?.bonus_xp && (
                    <div className="mt-4 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-green-400" />
                        <span className="text-sm font-semibold text-green-400">
                          Bonus XP Earned!
                        </span>
                      </div>
                      <div className="text-sm text-gray-300">
                        <p>Base XP: {result.bonus_xp.base_xp}</p>
                        <p>Bonus: +{result.bonus_xp.bonus_percentage}% ({result.bonus_xp.multiplier}x)</p>
                        <p className="font-semibold text-green-400">Total XP: {result.bonus_xp.total_xp}</p>
                        <p className="text-xs text-gray-400 mt-2">
                          You used {result.bonus_xp.hints_used} hint{result.bonus_xp.hints_used !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
