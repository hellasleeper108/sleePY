import Navigation from '@/components/Navigation';
import LessonViewer from '@/components/LessonViewer';

export default function PathDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LessonViewer pathId={parseInt(params.id)} />
      </main>
    </div>
  );
}
