'use client';

import { useEffect } from 'react';
import { X, Trophy, Zap, Star, Gift } from 'lucide-react';

export type NotificationType = 'xp' | 'level-up' | 'achievement' | 'streak' | 'loot';

export interface NotificationProps {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  xp?: number;
  onClose: (id: string) => void;
  duration?: number;
}

const getIcon = (type: NotificationType) => {
  switch (type) {
    case 'xp':
      return <Zap className="w-6 h-6 text-cyber-teal-light" />;
    case 'level-up':
      return <Star className="w-6 h-6 text-cyber-purple animate-pulse" />;
    case 'achievement':
      return <Trophy className="w-6 h-6 text-yellow-400" />;
    case 'streak':
      return <Zap className="w-6 h-6 text-orange-400" />;
    case 'loot':
      return <Gift className="w-6 h-6 text-pink-400" />;
  }
};

const getClassName = (type: NotificationType) => {
  switch (type) {
    case 'xp':
      return 'notification-success';
    case 'level-up':
      return 'notification-level-up';
    case 'achievement':
      return 'bg-yellow-500/20 border-l-4 border-yellow-500 text-gray-100 p-4 rounded-r-lg shadow-yellow-500/30 animate-slide-down';
    case 'streak':
      return 'bg-orange-500/20 border-l-4 border-orange-500 text-gray-100 p-4 rounded-r-lg shadow-orange-500/30 animate-slide-down';
    case 'loot':
      return 'bg-pink-500/20 border-l-4 border-pink-500 text-gray-100 p-4 rounded-r-lg shadow-pink-500/30 animate-slide-down';
  }
};

export default function Notification({
  id,
  type,
  title,
  message,
  xp,
  onClose,
  duration = 5000,
}: NotificationProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  return (
    <div className={`${getClassName(type)} flex items-start gap-3 min-w-[320px] max-w-md mb-3`}>
      <div className="flex-shrink-0 mt-0.5">{getIcon(type)}</div>
      <div className="flex-1">
        <div className="flex items-start justify-between">
          <h4 className="font-semibold text-lg">{title}</h4>
          <button
            onClick={() => onClose(id)}
            className="ml-2 text-gray-400 hover:text-gray-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <p className="text-sm text-gray-300 mt-1">{message}</p>
        {xp && (
          <div className="mt-2 flex items-center gap-2">
            <Zap className="w-4 h-4 text-cyber-teal-light" />
            <span className="text-cyber-teal-light font-semibold">+{xp} XP</span>
          </div>
        )}
      </div>
    </div>
  );
}
