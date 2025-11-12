import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  xp: number;
  level: number;
  is_active: boolean;
  created_at: string;
}

export interface Challenge {
  id: number;
  title: string;
  description: string;
  instructions: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  category: string;
  xp_reward: number;
  required_level: number;
  is_active: boolean;
  starter_code?: string;
  test_cases?: string;
}

export interface Progress {
  id: number;
  user_id: number;
  challenge_id: number;
  is_completed: boolean;
  attempts: number;
  xp_earned: number;
  completed_at?: string;
}

export interface Badge {
  id: number;
  name: string;
  description: string;
  icon: string;
  xp_requirement: number;
}

export interface LootChest {
  id: number;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  xp_reward: number;
  is_opened: boolean;
  earned_reason: string;
  earned_at: string;
}

export interface DailyStreak {
  id: number;
  user_id: number;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  achievement_type: string;
  threshold: number;
  xp_reward: number;
}

export interface LearningPath {
  id: number;
  title: string;
  description: string;
  topic: string;
  difficulty: string;
  estimated_hours: number;
  xp_reward: number;
  badge_id?: number;
  is_active: boolean;
}

export interface Lesson {
  id: number;
  learning_path_id: number;
  title: string;
  content: string;
  lesson_type: string;
  order: number;
  xp_reward: number;
}

export interface GameStats {
  total_xp: number;
  current_level: number;
  challenges_completed: number;
  achievements_unlocked: number;
  current_streak: number;
  longest_streak: number;
  total_chests_opened: number;
  badges_earned: number;
}

// API Methods
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  register: async (username: string, email: string, password: string, full_name: string) => {
    const response = await api.post('/api/auth/register', {
      username,
      email,
      password,
      full_name,
    });
    return response.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/api/users/me');
    return response.data;
  },
};

export const challengeAPI = {
  getAll: async (): Promise<Challenge[]> => {
    const response = await api.get('/api/challenges');
    return response.data;
  },
  getById: async (id: number): Promise<Challenge> => {
    const response = await api.get(`/api/challenges/${id}`);
    return response.data;
  },
};

export const progressAPI = {
  getMyProgress: async (): Promise<Progress[]> => {
    const response = await api.get('/api/progress/me');
    return response.data;
  },
  submitCode: async (challengeId: number, code: string) => {
    const response = await api.post('/api/progress/submit', {
      challenge_id: challengeId,
      code,
    });
    return response.data;
  },
};

export const gameAPI = {
  getStats: async (): Promise<GameStats> => {
    const response = await api.get('/api/game/stats');
    return response.data;
  },
  getStreak: async (): Promise<DailyStreak> => {
    const response = await api.get('/api/game/streak');
    return response.data;
  },
  checkIn: async () => {
    const response = await api.post('/api/game/checkin');
    return response.data;
  },
  getChests: async (): Promise<LootChest[]> => {
    const response = await api.get('/api/game/chests');
    return response.data;
  },
  openChest: async (chestId: number) => {
    const response = await api.post(`/api/game/chests/${chestId}/open`);
    return response.data;
  },
  getAchievements: async (): Promise<Achievement[]> => {
    const response = await api.get('/api/game/achievements');
    return response.data;
  },
  getUserAchievements: async () => {
    const response = await api.get('/api/game/achievements/user');
    return response.data;
  },
};

export const pathAPI = {
  getAll: async (): Promise<LearningPath[]> => {
    const response = await api.get('/api/paths');
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get(`/api/paths/${id}`);
    return response.data;
  },
  getLessons: async (pathId: number): Promise<Lesson[]> => {
    const response = await api.get(`/api/paths/${pathId}/lessons`);
    return response.data;
  },
  completeLesson: async (pathId: number, lessonId: number) => {
    const response = await api.post(`/api/paths/${pathId}/lessons/${lessonId}/complete`);
    return response.data;
  },
};

// Community API
export const friendsAPI = {
  follow: async (userId: number) => {
    const response = await api.post('/api/friends/follow', { following_id: userId });
    return response.data;
  },
  unfollow: async (userId: number) => {
    const response = await api.delete(`/api/friends/unfollow/${userId}`);
    return response.data;
  },
  getFollowing: async () => {
    const response = await api.get('/api/friends/following');
    return response.data;
  },
  getFollowers: async () => {
    const response = await api.get('/api/friends/followers');
    return response.data;
  },
  getList: async () => {
    const response = await api.get('/api/friends/list');
    return response.data;
  },
  search: async (query: string) => {
    const response = await api.get(`/api/friends/search?query=${encodeURIComponent(query)}`);
    return response.data;
  },
  getLeaderboard: async () => {
    const response = await api.get('/api/friends/leaderboard');
    return response.data;
  },
};

export const duelsAPI = {
  create: async (opponentId: number, challengeId: number, xpStake: number = 50) => {
    const response = await api.post('/api/duels/create', {
      opponent_id: opponentId,
      challenge_id: challengeId,
      xp_stake: xpStake,
    });
    return response.data;
  },
  accept: async (duelId: number) => {
    const response = await api.post('/api/duels/accept', { duel_id: duelId });
    return response.data;
  },
  submit: async (duelId: number, completionTime: number, code: string) => {
    const response = await api.post('/api/duels/submit', {
      duel_id: duelId,
      completion_time: completionTime,
      code,
    });
    return response.data;
  },
  getMyDuels: async (statusFilter?: string) => {
    const params = statusFilter ? `?status_filter=${statusFilter}` : '';
    const response = await api.get(`/api/duels/my-duels${params}`);
    return response.data;
  },
  getPending: async () => {
    const response = await api.get('/api/duels/pending');
    return response.data;
  },
  cancel: async (duelId: number) => {
    const response = await api.delete(`/api/duels/cancel/${duelId}`);
    return response.data;
  },
};

export const leaderboardAPI = {
  getGlobal: async (page: number = 1, pageSize: number = 100) => {
    const response = await api.get(`/api/leaderboard/global?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  getWeekly: async (page: number = 1, pageSize: number = 100) => {
    const response = await api.get(`/api/leaderboard/weekly?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  getTopic: async (category: string, page: number = 1, pageSize: number = 100) => {
    const response = await api.get(`/api/leaderboard/topic/${category}?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  getMyRank: async () => {
    const response = await api.get('/api/leaderboard/my-rank');
    return response.data;
  },
};

// Mentor AI API
export const mentorAPI = {
  getHint: async (challengeId: number, userCode?: string, errorMessage?: string) => {
    const response = await api.post('/api/mentor/hint', {
      challenge_id: challengeId,
      user_code: userCode,
      error_message: errorMessage,
    });
    return response.data;
  },
  getStatistics: async (challengeId: number) => {
    const response = await api.get(`/api/mentor/statistics/${challengeId}`);
    return response.data;
  },
  getConfig: async () => {
    const response = await api.get('/api/mentor/config');
    return response.data;
  },
  checkAvailable: async () => {
    const response = await api.get('/api/mentor/available');
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/api/mentor/hints/history');
    return response.data;
  },
};

export default api;
