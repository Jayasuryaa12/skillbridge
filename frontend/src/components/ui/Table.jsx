import React from 'react';

export const Table = ({ children, className = '' }) => (
  <div className="w-full overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
    <table className={`w-full text-left text-sm text-slate-600 dark:text-slate-300 ${className}`}>
      {children}
    </table>
  </div>
);

export const TableHeader = ({ children, className = '' }) => (
  <thead className={`bg-slate-50/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider ${className}`}>
    {children}
  </thead>
);

export const TableBody = ({ children, className = '' }) => (
  <tbody className={`divide-y divide-slate-100 dark:divide-slate-800/80 bg-white dark:bg-slate-900 ${className}`}>
    {children}
  </tbody>
);

export const TableRow = ({ children, className = '', hover = true, onClick }) => (
  <tr
    onClick={onClick}
    className={`${hover ? 'hover:bg-slate-50/70 dark:hover:bg-slate-800/50 transition-colors' : ''} ${onClick ? 'cursor-pointer' : ''} ${className}`}
  >
    {children}
  </tr>
);

export const TableHead = ({ children, className = '' }) => (
  <th scope="col" className={`py-3.5 px-4 sm:px-6 ${className}`}>
    {children}
  </th>
);

export const TableCell = ({ children, className = '' }) => (
  <td className={`py-3.5 px-4 sm:px-6 whitespace-nowrap text-sm ${className}`}>
    {children}
  </td>
);

export default Table;
