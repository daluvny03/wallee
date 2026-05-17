import React from 'react';
import { ChevronDown } from 'lucide-react';

export default function SelectFields({ value, onChange, children, className = '', ...props }) {
  return (
    <div className={`relative w-full ${className}`}>
      <select
        value={value}
        onChange={onChange}
        className="w-full h-12 pl-4 pr-10 bg-white border border-gray-200 rounded-xl text-sm outline-none focus:ring-1 focus:ring-blue-500 transition-all appearance-none cursor-pointer text-gray-500"
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground" />
    </div>
  );
}