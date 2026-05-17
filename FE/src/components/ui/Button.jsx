import React from 'react';

export default function Button({ children, className = "", size = "md", ...props }) {
  const sizes = { 
    sm: "px-3 py-1.5 text-xs md:text-sm", 
    md: "px-4 py-2 text-sm" 
  };
  
  return (
    <button
      className={`inline-flex items-center justify-center font-medium rounded-xl transition-all active:scale-95 disabled:opacity-50 border border-transparent ${sizes[size] ?? sizes.md} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}