import React from 'react';
import { cn } from '../../styles/component_classes';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'error' | 'success';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  helperText?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerClassName?: string;
}

export const Input: React.FC<InputProps> = ({
  variant = 'default',
  size = 'md',
  label,
  helperText,
  error,
  leftIcon,
  rightIcon,
  className,
  containerClassName,
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const baseClasses = 'w-full border rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 placeholder-secondary-400';
  
  const variantClasses = {
    default: 'border-secondary-300 focus:ring-primary-500 focus:border-transparent',
    error: 'border-accent-error focus:ring-red-500',
    success: 'border-accent-success focus:ring-green-500',
  };
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-3 py-2 text-base',
    lg: 'px-4 py-3 text-lg',
  };

  const hasIcons = leftIcon || rightIcon;
  const iconPadding = hasIcons ? (leftIcon ? 'pl-10' : '') + (rightIcon ? 'pr-10' : '') : '';

  const inputClasses = cn(
    baseClasses,
    variantClasses[error ? 'error' : variant],
    sizeClasses[size],
    iconPadding,
    className
  );

  return (
    <div className={cn('space-y-1', containerClassName)}>
      {label && (
        <label 
          htmlFor={inputId}
          className="block text-sm font-medium text-secondary-700"
        >
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className="text-secondary-400">
              {leftIcon}
            </span>
          </div>
        )}
        
        <input
          id={inputId}
          className={inputClasses}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <span className="text-secondary-400">
              {rightIcon}
            </span>
          </div>
        )}
      </div>
      
      {(error || helperText) && (
        <p className={cn(
          'text-sm',
          error ? 'text-accent-error' : 'text-secondary-500'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
};

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'default' | 'error' | 'success';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  helperText?: string;
  error?: string;
  containerClassName?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  variant = 'default',
  size = 'md',
  label,
  helperText,
  error,
  className,
  containerClassName,
  id,
  ...props
}) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  
  const baseClasses = 'w-full border rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 placeholder-secondary-400 resize-vertical';
  
  const variantClasses = {
    default: 'border-secondary-300 focus:ring-primary-500 focus:border-transparent',
    error: 'border-accent-error focus:ring-red-500',
    success: 'border-accent-success focus:ring-green-500',
  };
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-sm min-h-[80px]',
    md: 'px-3 py-2 text-base min-h-[100px]',
    lg: 'px-4 py-3 text-lg min-h-[120px]',
  };

  return (
    <div className={cn('space-y-1', containerClassName)}>
      {label && (
        <label 
          htmlFor={textareaId}
          className="block text-sm font-medium text-secondary-700"
        >
          {label}
        </label>
      )}
      
      <textarea
        id={textareaId}
        className={cn(
          baseClasses,
          variantClasses[error ? 'error' : variant],
          sizeClasses[size],
          className
        )}
        {...props}
      />
      
      {(error || helperText) && (
        <p className={cn(
          'text-sm',
          error ? 'text-accent-error' : 'text-secondary-500'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
};
