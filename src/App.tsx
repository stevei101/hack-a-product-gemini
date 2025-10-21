import { useState } from 'react';
import { Sparkles, Rocket, Zap } from 'lucide-react';

export default function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="mb-8">
            <Rocket className="h-16 w-16 text-blue-600 mx-auto mb-4" />
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Welcome to the Future
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              A clean, minimalist React + TypeScript app built with Bun, 
              containerized with Docker, and deployed on Kubernetes with Helm.
            </p>
          </div>

          {/* Interactive Demo */}
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Interactive Counter
            </h3>
            <div className="text-6xl font-bold text-blue-600 mb-6">
              {count}
            </div>
            <button
              onClick={() => setCount(count + 1)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              Increment
            </button>
          </div>

          {/* Features */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 mb-4">
                <Zap className="h-8 w-8 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Bun Runtime</h3>
              <p className="text-gray-600">
                Lightning-fast builds and package management with Bun's native TypeScript support.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 mb-4">
                <Sparkles className="h-8 w-8 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Docker Containerized</h3>
              <p className="text-gray-600">
                Multi-stage Docker builds for optimized, lightweight production images.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 mb-4">
                <Rocket className="h-8 w-8 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Kubernetes Ready</h3>
              <p className="text-gray-600">
                Helm charts for declarative, scalable deployments on any Kubernetes cluster.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500">
            <p>Built with ❤️ using React, Bun, Docker, and Kubernetes</p>
          </div>
        </div>
      </footer>
    </div>
  );
}