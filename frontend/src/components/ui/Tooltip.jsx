import React, { useState } from 'react';

export const Tooltip = ({
  children,
  content,
  position = 'top',
  delay = 150,
}) => {
  const [visible, setVisible] = useState(false);
  let timeoutId = null;

  const show = () => {
    timeoutId = setTimeout(() => setVisible(true), delay);
  };

  const hide = () => {
    if (timeoutId) clearTimeout(timeoutId);
    setVisible(false);
  };

  const positionStyles = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div className="relative inline-flex" onMouseEnter={show} onMouseLeave={hide} onFocus={show} onBlur={hide}>
      {children}
      {visible && content && (
        <div
          role="tooltip"
          className={`absolute z-50 px-2.5 py-1 text-xs font-medium text-white bg-slate-900 dark:bg-slate-800 rounded-lg shadow-dropdown pointer-events-none whitespace-nowrap animate-fade-in border border-slate-800 dark:border-slate-700 ${positionStyles[position] || positionStyles.top}`}
        >
          {content}
        </div>
      )}
    </div>
  );
};

export default Tooltip;
