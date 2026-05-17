import React from 'react';

export default function Badge({ children, className = "", variant = "secondary", ...props }) {
  const variants = {
    secondary: "bg-gray-100 text-gray-600",
    success:   "bg-emerald-50 text-emerald-600",
    danger:    "bg-red-50 text-red-600",
  };
  
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium uppercase tracking-wider ${variants[variant] ?? variants.secondary} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}