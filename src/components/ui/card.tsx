import React from 'react';
import { cn } from '../../styles/component_classes';

interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined' | 'flat';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  size = 'md',
  children,
  className,
  onClick,
  hover = false,
}) => {
  const baseClasses = 'rounded-xl border transition-all duration-200';
  
  const variantClasses = {
    default: 'bg-white border-secondary-200 shadow-soft hover:shadow-medium',
    elevated: 'bg-white shadow-medium hover:shadow-large',
    outlined: 'bg-white border-2 border-secondary-200 hover:border-primary-300',
    flat: 'bg-secondary-50 border-secondary-100',
  };
  
  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const hoverClasses = hover ? 'hover:scale-105 hover:shadow-lg cursor-pointer' : '';

  const Component = onClick ? 'button' : 'div';

  return (
    <Component
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        hoverClasses,
        className
      )}
      onClick={onClick}
    >
      {children}
    </Component>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => (
  <div className={cn('mb-4', className)}>
    {children}
  </div>
);

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export const CardTitle: React.FC<CardTitleProps> = ({ children, className }) => (
  <h3 className={cn('text-lg font-semibold text-secondary-900', className)}>
    {children}
  </h3>
);

interface CardDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export const CardDescription: React.FC<CardDescriptionProps> = ({ children, className }) => (
  <p className={cn('text-sm text-secondary-600 mt-1', className)}>
    {children}
  </p>
);

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className }) => (
  <div className={cn('', className)}>
    {children}
  </div>
);

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className }) => (
  <div className={cn('mt-4 pt-4 border-t border-secondary-200', className)}>
    {children}
  </div>
);
