# PyQuest RPG Features

PyQuest now includes comprehensive RPG-style mechanics to make learning Python more engaging and rewarding!

## 🎮 Core RPG Systems

### 1. Enhanced XP & Leveling

**New XP Formula:**
- `Level = floor(XP / 100) + 1`
- Simpler, more predictable progression
- Level thresholds:
  - Level 1: 0-99 XP
  - Level 2: 100-199 XP
  - Level 3: 200-299 XP
  - Level 10: 900-999 XP

**XP Multipliers by Difficulty:**
- Beginner: 1.0x
- Intermediate: 1.5x
- Advanced: 2.0x
- Expert: 3.0x

**Level-Up Rewards:**
- Automatic loot chest on level up
- Access to higher-level challenges
- Achievement unlocks

### 2. Loot Chest System 📦

**Chest Rarities:**
- **Common** (60% drop rate): 10-30 XP
- **Rare** (25% drop rate): 30-70 XP
- **Epic** (12% drop rate): 70-150 XP
- **Legendary** (3% drop rate): 150-300 XP

**How to Earn Chests:**
- Random drops after completing challenges (20% base rate, increases with completions)
- Level-up rewards (guaranteed)
- Streak milestone rewards
- Achievement rewards
- Special events

**Opening Chests:**
- Each chest contains random XP within its rarity range
- Opening a chest can trigger leveling
- Track all chests in `/api/game/loot-chests`

### 3. Daily Streak System 🔥

**Streak Mechanics:**
- Check in daily to maintain your streak
- Miss a day = streak resets to 1
- Consecutive days = bonus XP (5 XP per day, max 50)

**Streak Milestones:**
- 3 days: Common chest + bonus XP
- 7 days: Rare chest + bonus XP
- 14 days: Rare chest + bonus XP
- 30 days: Epic chest + bonus XP
- 60 days: Epic chest + bonus XP
- 100 days: Epic chest + bonus XP
- 365 days: Legendary chest + massive bonus XP

**Streak Bonuses:**
- Daily bonus XP: `current_streak × 5` (max 50 XP/day)
- Milestone bonus: `streak_days × 2` XP

### 4. Achievement System 🏆

**Achievement Types:**
1. **Challenge Count**: Complete X challenges
2. **XP Total**: Earn X total XP
3. **Level Reached**: Reach level X
4. **Streak Count**: Maintain X-day streak
5. **Perfect Score**: Complete challenges on first attempt
6. **Loot Collector**: Open X loot chests
7. **Category Master**: Complete all challenges in a category (future)

**17 Built-in Achievements:**

**Completion Achievements:**
- 🎯 First Steps (1 challenge) - 50 XP + chest
- ⭐ Getting Started (5 challenges) - 100 XP + chest
- 📚 Dedicated Learner (10 challenges) - 200 XP + chest
- 🏆 Challenge Master (25 challenges) - 500 XP + chest

**Level Achievements:**
- 🌟 Level Up! (Level 2) - 50 XP
- 💫 Rising Star (Level 5) - 100 XP + chest
- 🐍 Python Pro (Level 10) - 250 XP + chest

**Streak Achievements:**
- 🔥 Commitment (3-day streak) - 75 XP
- ⚡ Week Warrior (7-day streak) - 150 XP + chest
- 🌟 Unstoppable (30-day streak) - 500 XP + chest

**Performance Achievements:**
- 💯 First Try! (1 perfect score) - 100 XP
- ✨ Perfectionist (5 perfect scores) - 250 XP + chest

**Collection Achievements:**
- 📦 Treasure Hunter (10 chests opened) - 100 XP
- 💎 Hoarder (50 chests opened) - 300 XP + chest
- 💰 XP Collector (1000 total XP) - 100 XP
- 👑 XP Master (5000 total XP) - 500 XP + chest

**Secret Achievement:**
- 🎁 Secret Master (??? ) - 1000 XP + chest

**Auto-Unlock System:**
- Achievements automatically check after every action
- Instant notifications when unlocked
- Rewards granted immediately

## 🎯 New API Endpoints

### Game Mechanics (`/api/game`)

**Loot Chests:**
- `GET /api/game/loot-chests` - Get all your chests
- `POST /api/game/loot-chests/open/{chest_id}` - Open a chest

**Daily Streaks:**
- `GET /api/game/streak` - Get your current streak
- `POST /api/game/streak/checkin` - Daily check-in

**Achievements:**
- `GET /api/game/achievements` - All achievements with your progress
- `GET /api/game/achievements/unlocked` - Your unlocked achievements
- `POST /api/game/achievements/check` - Manually trigger achievement check

**Statistics:**
- `GET /api/game/stats` - Comprehensive game stats

### Enhanced Challenge Completion

When you complete a challenge, you now get:
- Difficulty-scaled XP (with multipliers)
- Chance for random loot chest drop
- Automatic achievement checks
- Level-up chest if you level up
- Notifications for all rewards

## 🧪 Game Engine

All RPG logic is centralized in `app/services/game_engine.py`:

**GameEngine Class:**
- `calculate_xp_for_challenge()` - XP calculation with multipliers
- `calculate_level_from_xp()` - Level calculation
- `award_xp()` - XP awarding with level-up handling
- `generate_loot_chest()` - Create loot chests
- `open_loot_chest()` - Open chests and award rewards
- `process_daily_checkin()` - Handle daily streaks
- `check_and_award_achievements()` - Auto-check achievements
- `get_user_stats()` - Comprehensive stat calculation
- `roll_random_chest_drop()` - Determine chest drops

**GameSimulator Class:**
- `simulate_user_progression()` - Test multi-day progression
- `test_loot_system()` - Test chest generation and opening

## 🧪 Testing

### Run Simulation Tests:

```bash
python test_game_simulation.py
```

This will:
- Simulate 7 days of progression (3 challenges/day)
- Test loot chest system (20 chests)
- Simulate 14 days of intense play (5 challenges/day)
- Show achievements unlocked
- Display streak mechanics
- Test level-up rewards

### Manual Testing:

```python
from app.db.session import SessionLocal
from app.services.game_engine import GameEngine, GameSimulator

db = SessionLocal()

# Test progression
GameSimulator.simulate_user_progression(
    db=db,
    username="test_user",
    days=7,
    challenges_per_day=3
)

# Test loot
GameSimulator.test_loot_system(
    db=db,
    username="test_user",
    num_chests=20
)
```

## 📊 Database Models

**New Models:**
1. **LootChest**: Track user loot chests
   - Rarity levels (Common, Rare, Epic, Legendary)
   - XP rewards
   - Open/unopened status

2. **DailyStreak**: Track consecutive activity days
   - Current streak
   - Longest streak
   - Last activity date
   - Auto-reset on miss

3. **Achievement**: Define unlockable achievements
   - Type and criteria
   - XP rewards
   - Loot chest grants
   - Secret flag

4. **UserAchievement**: Track unlocked achievements
   - User-achievement mapping
   - Unlock timestamp
   - Notification status

## 🎮 Gameplay Loop

1. **Complete Challenge**
   - Submit code
   - Earn XP (with difficulty multiplier)
   - Chance for loot chest drop
   - Achievements auto-check
   - Level up if threshold reached

2. **Daily Check-In**
   - Visit the platform
   - POST to `/api/game/streak/checkin`
   - Maintain streak or start new one
   - Earn bonus XP for consecutive days
   - Milestone rewards at key streaks

3. **Open Loot Chests**
   - Check `/api/game/loot-chests`
   - Open chests when ready
   - Get random XP rewards
   - Possibly level up from chest XP

4. **Track Progress**
   - Check `/api/game/stats` for overview
   - View `/api/game/achievements` for goals
   - Monitor streak in `/api/game/streak`
   - Climb the leaderboard

## 💡 Pro Tips

1. **Maximize XP Gains:**
   - Complete higher difficulty challenges (up to 3x XP!)
   - Maintain daily streaks (up to 50 bonus XP/day)
   - Open loot chests strategically
   - Unlock achievements for bonus XP

2. **Optimize Streaks:**
   - Check in every day
   - Aim for milestone days (3, 7, 30, etc.)
   - Streak rewards stack with regular XP

3. **Loot Strategy:**
   - Chests stack - save them for dry spells
   - Higher completion count = higher drop rates
   - Level-up chests are guaranteed
   - Achievement chests are often higher rarity

4. **Achievement Hunting:**
   - Check progress frequently
   - Some achievements grant loot chests
   - Secret achievements exist!
   - Perfect scores count (first attempt completions)

## 🔮 Future Enhancements

Potential additions:
- Boss challenges with mega rewards
- Seasonal events with limited-time achievements
- Guild/team systems
- PvP challenges
- Item shop (spend XP on cosmetics)
- Achievement showcases and badges
- Streak recovery tokens
- Challenge mastery levels

## 📈 Sample Progression

**Day 1:**
- Complete 3 beginner challenges: 30 XP
- Daily check-in streak: +5 XP
- First challenge achievement: +50 XP + chest
- Open chest: +20 XP
- **Total: 105 XP (Level 2!)**

**Day 7:**
- 7-day streak achievement: +150 XP + rare chest
- Week milestone: rare chest
- 5 challenges: ~75 XP
- Open 3 chests: ~60 XP
- **Estimated total: ~800 XP (Level 8-9)**

**Day 30:**
- 30-day streak: epic chest + 500 XP
- Dozens of challenges completed
- Multiple achievements unlocked
- **Estimated total: 3000-5000 XP (Level 30-50)**

---

**Ready to embark on your PyQuest adventure? Start coding and level up! 🚀**
