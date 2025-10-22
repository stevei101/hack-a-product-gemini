import React from 'react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({ icon, title, description }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col items-center text-center h-full">
      <div className="text-blue-600 mb-4 flex-shrink-0">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600 flex-grow">{description}</p>
    </div>
  );
};
