import React from "react";
import { createRoot } from "react-dom/client";
import { Sparkles, Rocket, Zap } from 'lucide-react';
import "./index.css";

import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { FeatureCard } from './components/FeatureCard';
import { Footer } from './components/Footer';

const App = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Hero />

        {/* Features Section */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Zap className="h-8 w-8 mx-auto" />}
            title="Bun Runtime"
            description="Lightning-fast builds and package management with Bun's native TypeScript support."
          />
          <FeatureCard
            icon={<Sparkles className="h-8 w-8 mx-auto" />}
            title="Docker Containerized"
            description="Multi-stage Docker builds for optimized, lightweight production images."
          />
          <FeatureCard
            icon={<Rocket className="h-8 w-8 mx-auto" />}
            title="Kubernetes Ready"
            description="Helm charts for declarative, scalable deployments on any Kubernetes cluster."
          />
        </div>
      </main>

      <Footer />
    </div>
  );
};

createRoot(document.getElementById("root")!).render(<App />);
