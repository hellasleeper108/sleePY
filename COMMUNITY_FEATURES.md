# PyQuest Community Features

Comprehensive community features for competitive learning and social interaction.

## Overview

PyQuest now includes three major community systems:
1. **Leaderboards** - Global, weekly, and topic-based rankings
2. **Friend System** - Follow users and track your network
3. **Challenge Duels** - 1v1 coding competitions

All features are optimized with database indexes and caching for real-time performance.

---

## 🏆 Leaderboards

### Types of Leaderboards

**Global Leaderboard**
- Ranks all users by total XP earned all-time
- Updates automatically when users earn XP
- Cached for 5 minutes for optimal performance
- Shows user level, total XP, and challenges completed
- Top 3 get special medal indicators (🥇🥈🥉)

**Weekly Leaderboard**
- Resets every 7 days
- Tracks XP earned in the last 7 days
- Perfect for active learners to compete weekly
- Encourages consistent learning habits

**Topic Leaderboards**
- Category-specific rankings (Basics, Data Structures, Algorithms, OOP, etc.)
- Shows expertise in specific Python topics
- Displays both topic XP and total XP

### API Endpoints

```
GET /api/leaderboard/global?page=1&page_size=100
GET /api/leaderboard/weekly?page=1&page_size=100
GET /api/leaderboard/topic/{category}?page=1&page_size=100
GET /api/leaderboard/my-rank
```

### Frontend

Access at: `http://localhost:3000/leaderboard`

Features:
- Tabbed interface switching between Global/Weekly/Topic
- User's current rank displayed in header
- Color-coded rankings (gold for #1, silver for #2, bronze for #3)
- Responsive table with pagination
- Real-time updates from cached data

### Performance Optimizations

**Database Indexes:**
- `users.xp` - indexed for fast ORDER BY queries
- `progress.completed_at` - indexed for weekly queries
- Composite index on `progress(user_id, is_completed, completed_at)`

**Caching:**
- In-memory cache with 5-minute TTL
- Auto-invalidates on XP changes
- Production-ready for Redis integration
- Bulk user data fetching to minimize queries

---

## 👥 Friend System

### Features

**Follow/Unfollow**
- One-way follow system (Twitter-style)
- Follow users to track their progress
- Get followed by others who admire your work

**User Search**
- Search by username or full name
- Real-time search results
- Shows if you're already following them
- Quick follow/unfollow buttons

**Friend Lists**
- View who you're following
- View who follows you
- See friend stats (level, XP, challenges)
- Friend leaderboard (compare with friends)

### API Endpoints

```
POST /api/friends/follow             # Follow a user
DELETE /api/friends/unfollow/{id}    # Unfollow a user
GET /api/friends/following           # List users you follow
GET /api/friends/followers           # List your followers
GET /api/friends/list                # Complete friend list
GET /api/friends/search?query=...    # Search for users
GET /api/friends/leaderboard         # Friends-only leaderboard
```

### Frontend

Access at: `http://localhost:3000/social`

Features:
- Search bar for finding new users
- Tabs for Following/Followers/Search Results
- User cards with avatars, stats, and action buttons
- Friends leaderboard sidebar (top 10)
- Follow back suggestions
- Real-time follower/following counts

### Database Model

```python
class Friendship:
    follower_id: int      # User who follows
    following_id: int     # User being followed
    created_at: datetime
    is_active: bool
```

**Indexes:**
- `idx_follower` on `follower_id`
- `idx_following` on `following_id`
- `idx_active_friendships` composite index
- Unique constraint on `(follower_id, following_id)`

---

## ⚔️ Challenge Duels

### How Duels Work

1. **Challenge**: User A challenges User B to a duel on a specific challenge
2. **Accept**: User B has 24 hours to accept the duel
3. **Compete**: Both users solve the challenge as fast as possible
4. **Winner**: Fastest correct solution wins bonus XP
5. **Rewards**: Winner gets full XP stake, loser gets half

### Duel States

- `PENDING` - Waiting for opponent to accept
- `ACTIVE` - Both accepted, competition in progress
- `COMPLETED` - Finished with results
- `CANCELLED` - Cancelled by challenger
- `EXPIRED` - Not accepted within 24 hours

### XP Stakes

- Default stake: 50 XP (configurable 10-500)
- Winner receives: Full stake (e.g., 50 XP)
- Loser receives: Half stake (e.g., 25 XP)
- Tie: Both get half stake

### API Endpoints

```
POST /api/duels/create         # Create new duel
POST /api/duels/accept         # Accept duel invitation
POST /api/duels/submit         # Submit solution with completion time
GET /api/duels/my-duels        # List your duels
GET /api/duels/pending         # Pending invitations
DELETE /api/duels/cancel/{id}  # Cancel a duel
```

### Database Model

```python
class Duel:
    challenge_id: int
    challenger_id: int
    opponent_id: int
    status: DuelStatus
    xp_stake: int
    challenger_completion_time: float  # Seconds
    opponent_completion_time: float
    winner_id: int
    created_at: datetime
    accepted_at: datetime
    expires_at: datetime
    completed_at: datetime
```

**Indexes:**
- `idx_duel_challenger` on `(challenger_id, status)`
- `idx_duel_opponent` on `(opponent_id, status)`
- `idx_duel_active` on `(status, created_at)`

### Usage Example

```python
# User 1 challenges User 2 to challenge #5 with 100 XP stake
duel = duelsAPI.create(
    opponent_id=2,
    challenge_id=5,
    xp_stake=100
)

# User 2 accepts the challenge
duelsAPI.accept(duel_id=duel.id)

# User 1 completes in 45.2 seconds
duelsAPI.submit(
    duel_id=duel.id,
    completion_time=45.2,
    code="def solution():\n    return 'Hello'"
)

# User 2 completes in 52.8 seconds
duelsAPI.submit(
    duel_id=duel.id,
    completion_time=52.8,
    code="def solution():\n    return 'Hello'"
)

# User 1 wins! Gets 100 XP, User 2 gets 50 XP
```

---

## 🚀 Performance Features

### Auto-Updating Leaderboards

When a user earns XP:
1. `GameEngine.award_xp()` is called
2. User's XP and level are updated
3. `LeaderboardService.invalidate_cache()` is triggered
4. Next leaderboard request fetches fresh data
5. New data is cached for 5 minutes

This ensures leaderboards are always up-to-date without performance impact.

### Query Optimizations

**Global Leaderboard:**
```sql
SELECT * FROM users
WHERE is_active = TRUE
ORDER BY xp DESC, id DESC
LIMIT 100 OFFSET 0;
-- Uses index on users.xp
```

**Weekly Leaderboard:**
```sql
SELECT user_id, SUM(xp_earned) as weekly_xp
FROM progress
WHERE is_completed = TRUE
  AND completed_at >= NOW() - INTERVAL '7 days'
GROUP BY user_id
ORDER BY weekly_xp DESC
LIMIT 100;
-- Uses composite index on progress(user_id, is_completed, completed_at)
```

**Friends Leaderboard:**
```sql
SELECT u.*
FROM users u
JOIN friendships f ON u.id = f.following_id
WHERE f.follower_id = ? AND f.is_active = TRUE
ORDER BY u.xp DESC
LIMIT 50;
-- Uses indexes on friendships and users.xp
```

### Caching Strategy

```python
class LeaderboardCache:
    ttl = 300  # 5 minutes

    def get(key):
        # Return cached value if not expired

    def set(key, value):
        # Cache with timestamp

    def invalidate(key):
        # Clear specific cache

    def clear():
        # Clear all cache
```

---

## 📊 API Summary

### Leaderboard API
- `GET /api/leaderboard/global` - Global rankings
- `GET /api/leaderboard/weekly` - Weekly rankings
- `GET /api/leaderboard/topic/{category}` - Topic-specific
- `GET /api/leaderboard/my-rank` - User's ranks

### Friends API
- `POST /api/friends/follow` - Follow user
- `DELETE /api/friends/unfollow/{id}` - Unfollow
- `GET /api/friends/following` - Following list
- `GET /api/friends/followers` - Followers list
- `GET /api/friends/list` - Complete friend data
- `GET /api/friends/search?query=...` - Search users
- `GET /api/friends/leaderboard` - Friends rankings

### Duels API
- `POST /api/duels/create` - Create duel
- `POST /api/duels/accept` - Accept duel
- `POST /api/duels/submit` - Submit solution
- `GET /api/duels/my-duels` - List duels
- `GET /api/duels/pending` - Pending invitations
- `DELETE /api/duels/cancel/{id}` - Cancel duel

---

## 🎨 Frontend Components

### Leaderboard Page
**Location:** `/frontend/app/leaderboard/page.tsx`

Features:
- Tabbed interface (Global/Weekly/Topic)
- Ranked table with medals for top 3
- User rank display in header
- Pagination support
- Loading states
- Info cards explaining each type

### Social Page
**Location:** `/frontend/app/social/page.tsx`

Features:
- User search with real-time results
- Following/Followers tabs
- Friend cards with stats
- Follow/Unfollow buttons
- Friends leaderboard sidebar
- Empty states for each view

### Navigation
Updated with:
- Leaderboard link (TrendingUp icon)
- Social link (Users icon)
- Active state highlighting
- Mobile-responsive layout

---

## 🔧 Setup & Usage

### Backend Setup

1. **Database Migration**
   The new tables will be created automatically:
   - `friendships`
   - `duels`

2. **Start Backend**
   ```bash
   python main.py
   ```

3. **Access API Docs**
   http://localhost:8000/docs

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend**
   ```bash
   npm run dev
   ```

3. **Access Pages**
   - Leaderboard: http://localhost:3000/leaderboard
   - Social: http://localhost:3000/social

### Testing

```bash
# Test leaderboard
curl http://localhost:8000/api/leaderboard/global

# Test friends
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/friends/list

# Test duels
curl -H "Authorization: Bearer YOUR_TOKEN" \
  -X POST http://localhost:8000/api/duels/create \
  -d '{"opponent_id": 2, "challenge_id": 1, "xp_stake": 50}'
```

---

## 📈 Future Enhancements

Potential additions:
- **Real-time Duels**: WebSocket support for live competitions
- **Team Challenges**: Group competitions
- **Duel Tournaments**: Bracket-style competitions
- **Activity Feed**: See friend completions and achievements
- **Private Messages**: Chat with friends
- **Duel Replays**: Review past duels
- **Seasonal Leaderboards**: Monthly/yearly rankings
- **Topic Badges**: Badges for topic mastery
- **Challenge of the Day**: Global daily challenge

---

## 🎯 Key Benefits

1. **Motivation**: Compete with others to stay motivated
2. **Social Learning**: Learn from friends and top performers
3. **Real-time Rankings**: See your progress compared to others
4. **Fair Competition**: Duels ensure equal starting conditions
5. **Performance**: Optimized queries with caching
6. **Scalability**: Ready for thousands of users

---

## 📝 Notes

- Leaderboard cache: 5 minutes (configurable)
- Duel expiration: 24 hours (configurable)
- XP stakes: 10-500 range (configurable)
- Friend system: One-way follows (like Twitter)
- All features work with existing authentication

Happy coding and competing! 🚀
