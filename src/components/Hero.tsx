import { useState } from 'react';
import { Rocket } from 'lucide-react';

export const Hero = () => {
  const [count, setCount] = useState(0);

  return (
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
    </div>
  );
};
