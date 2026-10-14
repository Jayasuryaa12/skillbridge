import React from 'react';

const COLORS = [
  'bg-brand-500 text-white',
  'bg-emerald-500 text-white',
  'bg-sky-500 text-white',
  'bg-amber-500 text-white',
  'bg-rose-500 text-white',
  'bg-purple-500 text-white',
  'bg-teal-500 text-white',
];

export const Avatar = ({
  name = '',
  src,
  size = 'md',
  status,
  className = '',
}) => {
  const getInitials = (str) => {
    if (!str) return '?';
    const parts = str.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return str.substring(0, 2).toUpperCase();
  };

  const getColor = (str) => {
    if (!str) return COLORS[0];
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const idx = Math.abs(hash) % COLORS.length;
    return COLORS[idx];
  };

  const sizes = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-9 h-9 text-xs',
    lg: 'w-12 h-12 text-sm',
    xl: 'w-16 h-16 text-lg font-semibold',
  };

  const statusSizes = {
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
    xl: 'w-4 h-4',
  };

  const statusColors = {
    online: 'bg-emerald-500',
    busy: 'bg-amber-500',
    offline: 'bg-slate-400',
  };

  return (
    <div className={`relative inline-flex shrink-0 ${className}`}>
      {src ? (
        <img
          src={src}
          alt={name}
          className={`${sizes[size] || sizes.md} rounded-full object-cover ring-2 ring-white dark:ring-slate-900`}
        />
      ) : (
        <div
          className={`${sizes[size] || sizes.md} rounded-full flex items-center justify-center font-medium select-none shadow-sm ring-2 ring-white dark:ring-slate-900 ${getColor(name)}`}
        >
          {getInitials(name)}
        </div>
      )}
      {status && (
        <span
          className={`absolute bottom-0 right-0 rounded-full ring-2 ring-white dark:ring-slate-900 ${statusSizes[size] || statusSizes.md} ${statusColors[status] || statusColors.online}`}
        />
      )}
    </div>
  );
};

export default Avatar;
