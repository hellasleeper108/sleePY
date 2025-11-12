'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Lesson, LearningPath } from '@/lib/api';
import { pathAPI } from '@/lib/api';
import { ChevronLeft, ChevronRight, CheckCircle, BookOpen, Zap } from 'lucide-react';
import { useNotifications } from './NotificationContainer';
import { formatXP } from '@/lib/utils';

interface LessonViewerProps {
  pathId: number;
}

export default function LessonViewer({ pathId }: LessonViewerProps) {
  const [path, setPath] = useState<LearningPath | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const [completedLessons, setCompletedLessons] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const { showNotification } = useNotifications();

  useEffect(() => {
    loadPath();
  }, [pathId]);

  const loadPath = async () => {
    try {
      const [pathData, lessonsData] = await Promise.all([
        pathAPI.getById(pathId),
        pathAPI.getLessons(pathId),
      ]);
      setPath(pathData.path);
      setLessons(lessonsData);
      // Load completed lessons from progress
      const completed = new Set(
        pathData.lessons_progress
          ?.filter((p: any) => p.is_completed)
          .map((p: any) => p.lesson_id) || []
      );
      setCompletedLessons(completed);
    } catch (error) {
      console.error('Failed to load learning path:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentLesson = lessons[currentLessonIndex];

  const handleCompleteLesson = async () => {
    if (!currentLesson || completedLessons.has(currentLesson.id)) return;

    try {
      const result = await pathAPI.completeLesson(pathId, currentLesson.id);

      setCompletedLessons(new Set([...completedLessons, currentLesson.id]));

      showNotification(
        'xp',
        'Lesson Completed!',
        `You earned ${result.xp_earned} XP for completing "${currentLesson.title}"`,
        result.xp_earned
      );

      if (result.leveled_up) {
        showNotification(
          'level-up',
          'Level Up!',
          `Congratulations! You reached level ${result.new_level}!`
        );
      }

      // Auto-advance to next lesson
      if (currentLessonIndex < lessons.length - 1) {
        setTimeout(() => {
          setCurrentLessonIndex(currentLessonIndex + 1);
        }, 1500);
      }
    } catch (error) {
      console.error('Failed to complete lesson:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyber-teal"></div>
      </div>
    );
  }

  if (!path || !currentLesson) {
    return (
      <div className="text-center text-gray-400 py-12">
        Learning path not found.
      </div>
    );
  }

  const progress = (completedLessons.size / lessons.length) * 100;
  const isCurrentLessonCompleted = completedLessons.has(currentLesson.id);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Path Header */}
      <div className="cyber-card p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">{path.title}</h1>
            <p className="text-gray-400">{path.description}</p>
          </div>
          <div className="flex items-center gap-2 bg-cyber-gray-medium px-4 py-2 rounded-lg">
            <BookOpen className="w-5 h-5 text-cyber-teal" />
            <span className="text-sm">
              {completedLessons.size} / {lessons.length} Lessons
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Course Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="xp-bar">
            <div className="xp-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      </div>

      {/* Lesson Navigation */}
      <div className="cyber-card p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentLessonIndex(Math.max(0, currentLessonIndex - 1))}
            disabled={currentLessonIndex === 0}
            className="flex items-center gap-2 px-4 py-2 bg-cyber-gray-medium rounded-lg hover:bg-cyber-gray-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5" />
            Previous
          </button>

          <div className="text-center">
            <div className="text-sm text-gray-400">Lesson {currentLessonIndex + 1} of {lessons.length}</div>
            <div className="font-semibold">{currentLesson.title}</div>
          </div>

          <button
            onClick={() => setCurrentLessonIndex(Math.min(lessons.length - 1, currentLessonIndex + 1))}
            disabled={currentLessonIndex === lessons.length - 1}
            className="flex items-center gap-2 px-4 py-2 bg-cyber-gray-medium rounded-lg hover:bg-cyber-gray-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Lesson Content */}
      <div className="cyber-card p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">{currentLesson.title}</h2>
          {isCurrentLessonCompleted && (
            <div className="flex items-center gap-2 text-green-400">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm font-semibold">Completed</span>
            </div>
          )}
        </div>

        <div className="prose prose-invert prose-teal max-w-none">
          <ReactMarkdown
            components={{
              h1: ({ children }) => <h1 className="text-3xl font-bold text-cyber-teal-light mb-4">{children}</h1>,
              h2: ({ children }) => <h2 className="text-2xl font-bold text-gray-200 mt-6 mb-3">{children}</h2>,
              h3: ({ children }) => <h3 className="text-xl font-semibold text-gray-300 mt-4 mb-2">{children}</h3>,
              p: ({ children }) => <p className="text-gray-300 leading-relaxed mb-4">{children}</p>,
              code: ({ className, children }) => {
                const isInline = !className;
                return isInline ? (
                  <code className="bg-cyber-gray-medium text-cyber-teal px-2 py-1 rounded text-sm font-mono">
                    {children}
                  </code>
                ) : (
                  <code className="block bg-cyber-darker p-4 rounded-lg text-sm font-mono overflow-x-auto border border-cyber-gray-medium">
                    {children}
                  </code>
                );
              },
              ul: ({ children }) => <ul className="list-disc list-inside text-gray-300 space-y-2 mb-4">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal list-inside text-gray-300 space-y-2 mb-4">{children}</ol>,
              li: ({ children }) => <li className="ml-4">{children}</li>,
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-cyber-teal pl-4 italic text-gray-400 my-4">
                  {children}
                </blockquote>
              ),
            }}
          >
            {currentLesson.content}
          </ReactMarkdown>
        </div>
      </div>

      {/* Complete Lesson Button */}
      {!isCurrentLessonCompleted && (
        <div className="cyber-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-semibold text-lg mb-1">Ready to continue?</div>
              <div className="text-sm text-gray-400">
                Complete this lesson to earn {formatXP(currentLesson.xp_reward)} XP
              </div>
            </div>
            <button onClick={handleCompleteLesson} className="cyber-button flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              Complete Lesson
              <div className="flex items-center gap-1 ml-2">
                <Zap className="w-4 h-4" />
                +{formatXP(currentLesson.xp_reward)}
              </div>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
