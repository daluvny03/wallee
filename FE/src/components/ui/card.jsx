import React from 'react';

export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-2xl shadow-sm rounded-xl shadow-sm overflow-hidden ${className}`}>
      {children}
    </div>
  );
}