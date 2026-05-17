import React from 'react';

export default function InputFields({ type = 'text', placeholder, value, onChange, className = '', ...props }) {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={`w-full h-12 px-4 bg-white border border-gray-300 rounded-xl text-sm outline-none focus:ring-1 focus:ring-blue-500 transition-all text-black placeholder:text-gray-400 ${className}`}
      {...props}
    />
  );
}