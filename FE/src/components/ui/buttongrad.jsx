import React from 'react';

export default function ButtonGrad({ children, type = 'button', disabled = false, onClick, className = '' }) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`bg-[linear-gradient(135deg,#3975E6,#9E4CC6)] text-white font-semibold text-sm rounded-xl md:rounded-xl flex items-center justify-center gap-2 transition-all hover:opacity-95 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none shadow-lg shadow-primary/15 ${className}`}
    >
      {children}
    </button>
  );
}