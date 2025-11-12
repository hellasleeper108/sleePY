import Navigation from '@/components/Navigation';
import QuestBoard from '@/components/QuestBoard';

export default function QuestsPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <QuestBoard />
      </main>
    </div>
  );
}
