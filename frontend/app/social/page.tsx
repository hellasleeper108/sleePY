'use client';

import { useState, useEffect } from 'react';
import Navigation from '@/components/Navigation';
import { friendsAPI } from '@/lib/api';
import { Users, UserPlus, UserMinus, Search, Trophy } from 'lucide-react';
import { formatXP } from '@/lib/utils';

export default function SocialPage() {
  const [activeTab, setActiveTab] = useState<'following' | 'followers' | 'search'>('following');
  const [following, setFollowing] = useState<any[]>([]);
  const [followers, setFollowers] = useState<any[]>([]);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [friendLeaderboard, setFriendLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    loadFriends();
    loadFriendLeaderboard();
  }, []);

  const loadFriends = async () => {
    try {
      const data = await friendsAPI.getList();
      setFollowing(data.following || []);
      setFollowers(data.followers || []);
    } catch (error) {
      console.error('Failed to load friends:', error);
    }
  };

  const loadFriendLeaderboard = async () => {
    try {
      const data = await friendsAPI.getLeaderboard();
      setFriendLeaderboard(data.entries || []);
    } catch (error) {
      console.error('Failed to load friend leaderboard:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const results = await friendsAPI.search(searchQuery);
      setSearchResults(results || []);
      setActiveTab('search');
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (userId: number) => {
    try {
      await friendsAPI.follow(userId);
      loadFriends();
      if (searchQuery) {
        handleSearch();
      }
    } catch (error) {
      console.error('Follow failed:', error);
    }
  };

  const handleUnfollow = async (userId: number) => {
    try {
      await friendsAPI.unfollow(userId);
      loadFriends();
      loadFriendLeaderboard();
    } catch (error) {
      console.error('Unfollow failed:', error);
    }
  };

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">
              <span className="glow-text">Social</span>
            </h1>
            <p className="text-gray-400">Connect with fellow Python learners</p>
          </div>

          {/* Search Bar */}
          <div className="cyber-card p-6">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search users by username or name..."
                  className="cyber-input w-full pl-10"
                />
              </div>
              <button onClick={handleSearch} disabled={loading} className="cyber-button">
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Friends List */}
            <div className="lg:col-span-2 space-y-6">
              {/* Tabs */}
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveTab('following')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    activeTab === 'following'
                      ? 'bg-teal-gradient text-white shadow-cyber'
                      : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
                  }`}
                >
                  Following ({following.length})
                </button>
                <button
                  onClick={() => setActiveTab('followers')}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                    activeTab === 'followers'
                      ? 'bg-teal-gradient text-white shadow-cyber'
                      : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
                  }`}
                >
                  Followers ({followers.length})
                </button>
                {searchResults.length > 0 && (
                  <button
                    onClick={() => setActiveTab('search')}
                    className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                      activeTab === 'search'
                        ? 'bg-teal-gradient text-white shadow-cyber'
                        : 'bg-cyber-gray-dark text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    Search Results ({searchResults.length})
                  </button>
                )}
              </div>

              {/* User List */}
              <div className="space-y-3">
                {activeTab === 'following' &&
                  following.map((user) => (
                    <div key={user.user_id} className="cyber-card-hover p-4 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-teal-gradient flex items-center justify-center text-lg font-bold">
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-semibold">{user.username}</div>
                          <div className="text-sm text-gray-400">{user.full_name}</div>
                          <div className="text-xs text-cyber-teal-light">
                            Level {user.level} • {formatXP(user.xp)} XP
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleUnfollow(user.user_id)}
                        className="px-4 py-2 bg-cyber-gray-medium hover:bg-red-500/20 border border-red-500/50 text-red-400 rounded-lg transition-colors flex items-center gap-2"
                      >
                        <UserMinus className="w-4 h-4" />
                        Unfollow
                      </button>
                    </div>
                  ))}

                {activeTab === 'followers' &&
                  followers.map((user) => (
                    <div key={user.user_id} className="cyber-card-hover p-4 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-purple-gradient flex items-center justify-center text-lg font-bold">
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-semibold">{user.username}</div>
                          <div className="text-sm text-gray-400">{user.full_name}</div>
                          <div className="text-xs text-purple-400">
                            Level {user.level} • {formatXP(user.xp)} XP
                          </div>
                        </div>
                      </div>
                      {!following.find((f) => f.user_id === user.user_id) && (
                        <button
                          onClick={() => handleFollow(user.user_id)}
                          className="cyber-button-secondary flex items-center gap-2"
                        >
                          <UserPlus className="w-4 h-4" />
                          Follow Back
                        </button>
                      )}
                    </div>
                  ))}

                {activeTab === 'search' &&
                  searchResults.map((user) => (
                    <div key={user.user_id} className="cyber-card-hover p-4 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-cyber-gray-medium flex items-center justify-center text-lg font-bold">
                          {user.username.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-semibold">{user.username}</div>
                          <div className="text-sm text-gray-400">{user.full_name}</div>
                          <div className="text-xs text-gray-500">
                            Level {user.level} • {formatXP(user.xp)} XP
                          </div>
                        </div>
                      </div>
                      {user.is_following ? (
                        <button
                          onClick={() => handleUnfollow(user.user_id)}
                          className="px-4 py-2 bg-cyber-gray-medium hover:bg-red-500/20 border border-red-500/50 text-red-400 rounded-lg transition-colors flex items-center gap-2"
                        >
                          <UserMinus className="w-4 h-4" />
                          Unfollow
                        </button>
                      ) : (
                        <button
                          onClick={() => handleFollow(user.user_id)}
                          className="cyber-button flex items-center gap-2"
                        >
                          <UserPlus className="w-4 h-4" />
                          Follow
                        </button>
                      )}
                    </div>
                  ))}

                {((activeTab === 'following' && following.length === 0) ||
                  (activeTab === 'followers' && followers.length === 0) ||
                  (activeTab === 'search' && searchResults.length === 0)) && (
                  <div className="text-center py-12 text-gray-400">
                    <Users className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                    <p>
                      {activeTab === 'following' && 'Not following anyone yet. Search for users to follow!'}
                      {activeTab === 'followers' && 'No followers yet. Keep learning and sharing your progress!'}
                      {activeTab === 'search' && 'No users found. Try a different search term.'}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Friends Leaderboard */}
            <div className="cyber-card p-6">
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-400" />
                Friends Leaderboard
              </h3>
              <div className="space-y-3">
                {friendLeaderboard.slice(0, 10).map((entry, index) => (
                  <div key={entry.user_id} className="flex items-center gap-3">
                    <div className={`w-8 text-center font-bold ${index < 3 ? 'text-yellow-400' : 'text-gray-500'}`}>
                      #{entry.rank}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm font-semibold">{entry.username}</div>
                      <div className="text-xs text-cyber-teal-light">{formatXP(entry.xp)} XP</div>
                    </div>
                    <div className="text-xs text-gray-500">Lvl {entry.level}</div>
                  </div>
                ))}
                {friendLeaderboard.length === 0 && (
                  <div className="text-sm text-gray-400 text-center py-4">
                    Follow users to see their rankings!
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
