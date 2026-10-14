import React from 'react';

export const Card = ({
  children,
  className = '',
  hoverEffect = false,
  glass = false,
  onClick,
  ...props
}) => {
  const base = 'rounded-2xl transition-all duration-200 border';
  const glassStyle = glass
    ? 'glass-panel shadow-sm'
    : 'bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800 shadow-card';
  const hoverStyle = hoverEffect
    ? 'hover:shadow-card-hover hover:border-slate-300 dark:hover:border-slate-700 hover:-translate-y-0.5 cursor-pointer'
    : '';

  return (
    <div
      onClick={onClick}
      className={`${base} ${glassStyle} ${hoverStyle} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '', title, subtitle, action }) => (
  <div className={`p-5 sm:p-6 pb-3 sm:pb-4 flex items-start justify-between gap-4 border-b border-slate-100 dark:border-slate-800/80 ${className}`}>
    <div>
      {title && <h3 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</h3>}
      {subtitle && <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>}
      {children}
    </div>
    {action && <div className="shrink-0">{action}</div>}
  </div>
);

export const CardContent = ({ children, className = '' }) => (
  <div className={`p-5 sm:p-6 ${className}`}>
    {children}
  </div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`p-4 sm:p-5 pt-3 sm:pt-4 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/50 rounded-b-2xl flex items-center justify-between gap-3 ${className}`}>
    {children}
  </div>
);

export default Card;
