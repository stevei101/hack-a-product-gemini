import { Sparkles, Zap } from 'lucide-react';

export const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center space-x-3">
            <Sparkles className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">React + Bun + K8s</h1>
              <p className="text-sm text-gray-500">Modern, fast, and scalable</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Zap className="h-4 w-4" />
            <span>Powered by Bun</span>
          </div>
        </div>
      </div>
    </header>
  );
};
