# PyQuest Frontend

A modern, cyberpunk-themed React/Next.js frontend for the PyQuest gamified Python learning platform.

## Features

### Dashboard
- **User Stats Overview**: Real-time display of XP, level, challenges completed, achievements, and more
- **XP Progress Bar**: Animated progress bar showing advancement toward next level
- **Daily Streak Tracker**: Track consecutive days of activity with bonus XP rewards
- **Stat Cards**: Beautiful cards showing total XP, challenges, achievements, and loot chests

### Quest Board
- **Challenge Browser**: View all available coding challenges with filtering
- **Difficulty Indicators**: Color-coded badges for beginner, intermediate, advanced, and expert levels
- **Progress Tracking**: See completed challenges and attempts
- **XP Rewards**: Clear display of XP rewards for each challenge
- **Category Filters**: Filter by challenge category (basics, data structures, algorithms, etc.)

### Learning Paths
- **Structured Courses**: Complete learning paths on Python topics
- **Interactive Lessons**: Markdown-rendered lessons with syntax highlighting
- **Progress Tracking**: Visual progress bars showing completion percentage
- **Lesson Navigation**: Easy navigation between lessons
- **XP Rewards**: Earn XP for completing lessons

### Notification System
- **Real-time Notifications**: Toast notifications for all game events
- **Multiple Types**: XP gain, level-ups, achievements, streaks, and loot
- **Auto-dismiss**: Notifications automatically disappear after 5 seconds
- **Animated Entries**: Smooth slide-down animations

### Achievements
- **Achievement Gallery**: View all available achievements
- **Progress Indicators**: See unlocked vs locked achievements
- **XP Rewards**: Display XP rewards for each achievement

### Profile
- **User Information**: View account details and stats
- **Level Progress**: Current level and XP with visual progress bar
- **Stats Summary**: Quick overview of progress metrics

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Markdown**: react-markdown
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Design System

### Cyberpunk Theme
The UI features a dark cyberpunk aesthetic with:
- **Primary Colors**: Teal (#0d9488) and Purple (#6b46c1)
- **Background**: Dark navy (#0a0e27) with gradient overlays
- **Accents**: Pink, yellow, and orange for special elements
- **Animations**: Glowing effects, smooth transitions, and pulsing elements

### Components
- **cyber-card**: Base card component with dark background and border
- **cyber-button**: Primary action button with teal gradient
- **cyber-button-secondary**: Secondary button with purple gradient
- **xp-bar**: Animated XP progress bar with glow effect
- **notification-***: Notification components with type-specific styling

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- PyQuest backend running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                      # Next.js app directory
│   ├── layout.tsx           # Root layout with NotificationProvider
│   ├── page.tsx             # Dashboard page
│   ├── globals.css          # Global styles and Tailwind
│   ├── quests/              # Quest Board pages
│   ├── paths/               # Learning Paths pages
│   ├── achievements/        # Achievements page
│   └── profile/             # Profile page
├── components/              # React components
│   ├── Dashboard.tsx        # Main dashboard component
│   ├── QuestBoard.tsx       # Challenge browser
│   ├── LessonViewer.tsx     # Lesson viewer with markdown
│   ├── XPBar.tsx            # XP progress bar
│   ├── Navigation.tsx       # Top navigation bar
│   ├── Notification.tsx     # Toast notification component
│   └── NotificationContainer.tsx  # Notification manager
├── lib/                     # Utilities and API
│   ├── api.ts              # API client and type definitions
│   └── utils.ts            # Utility functions
├── public/                  # Static assets
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

## API Integration

The frontend integrates with the PyQuest FastAPI backend through the following endpoints:

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/users/me` - Get current user

### Challenges
- `GET /api/challenges` - List all challenges
- `GET /api/challenges/{id}` - Get challenge details

### Progress
- `GET /api/progress/me` - Get user progress
- `POST /api/progress/submit` - Submit code solution

### Game Mechanics
- `GET /api/game/stats` - Get user stats
- `GET /api/game/streak` - Get daily streak
- `POST /api/game/checkin` - Daily check-in
- `GET /api/game/chests` - Get loot chests
- `POST /api/game/chests/{id}/open` - Open loot chest
- `GET /api/game/achievements` - List achievements
- `GET /api/game/achievements/user` - Get user achievements

### Learning Paths
- `GET /api/paths` - List learning paths
- `GET /api/paths/{id}` - Get path details
- `GET /api/paths/{id}/lessons` - Get lessons for path
- `POST /api/paths/{id}/lessons/{lesson_id}/complete` - Complete lesson

## Features in Detail

### XP System
- Level = floor(XP / 100) + 1
- Visual progress bar shows advancement within current level
- Animated transitions when earning XP
- Level-up notifications with special effects

### Notifications
The notification system supports multiple types:
- **XP**: Teal notification for XP gains
- **Level-up**: Purple notification with star icon
- **Achievement**: Yellow notification with trophy icon
- **Streak**: Orange notification with flame icon
- **Loot**: Pink notification with gift icon

### Responsive Design
- Mobile-first approach
- Responsive grid layouts
- Adaptive navigation
- Touch-friendly interface

## Customization

### Theme Colors
Edit `tailwind.config.ts` to customize the color scheme:

```typescript
colors: {
  cyber: {
    dark: '#0a0e27',      // Main background
    teal: '#0d9488',      // Primary accent
    purple: '#6b46c1',    // Secondary accent
    // ... more colors
  }
}
```

### Animations
Customize animations in `app/globals.css`:

```css
@layer components {
  .cyber-button {
    @apply px-6 py-3 bg-teal-gradient ... ;
  }
}
```

## Development

### Adding New Pages
1. Create a new directory in `app/`
2. Add a `page.tsx` file
3. Import and use Navigation component
4. Add route to Navigation component

### Adding New Components
1. Create component in `components/`
2. Use TypeScript for type safety
3. Follow the cyber-* naming convention for themed components
4. Import utilities from `@/lib/utils`

### API Integration
1. Add type definitions to `lib/api.ts`
2. Create API methods in respective API objects
3. Use in components with `useEffect` and state management

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Code splitting with Next.js App Router
- Lazy loading of components
- Optimized images and assets
- Minimal bundle size with tree shaking

## License

This project is part of the PyQuest platform.
