import React from 'react';

export default function Button({ 
  children, 
  variant = 'primary', 
  type = 'button', 
  onClick, 
  disabled = false,
  className = ''
}) {
  // Base styles that apply to all buttons (layout, focus states, transitions)
  const baseStyles = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";
  
  // Dynamic styles based on the chosen variant
  const variants = {
    primary: "bg-primary-600 text-white hover:bg-primary-500 shadow-sm",
    secondary: "bg-surface-100 text-surface-900 hover:bg-surface-200",
    outline: "border border-surface-200 bg-transparent hover:bg-surface-50 text-surface-900",
    danger: "bg-rose-600 text-white hover:bg-rose-500 shadow-sm"
  };

  // Standard enterprise sizing
  const sizes = "h-10 py-2 px-4";

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${sizes} ${className}`}
    >
      {children}
    </button>
  );
}