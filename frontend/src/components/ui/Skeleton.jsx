import React from 'react';

export const Skeleton = ({
  className = '',
  variant = 'rectangular',
  width,
  height,
}) => {
  const variantStyles = {
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    text: 'rounded h-4 w-full my-1',
  };

  const style = {
    width: width || undefined,
    height: height || undefined,
  };

  return (
    <div
      style={style}
      className={`skeleton-shimmer ${variantStyles[variant] || variantStyles.rectangular} ${className}`}
      aria-hidden="true"
    />
  );
};

export const CardSkeleton = () => (
  <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
    <div className="flex items-center justify-between">
      <Skeleton width="45%" height="24px" />
      <Skeleton width="18%" height="20px" variant="rectangular" />
    </div>
    <Skeleton width="80%" height="16px" />
    <div className="pt-2 flex gap-2">
      <Skeleton width="60px" height="24px" />
      <Skeleton width="60px" height="24px" />
      <Skeleton width="80px" height="24px" />
    </div>
  </div>
);

export const TableRowSkeleton = ({ columns = 5 }) => (
  <tr className="border-b border-slate-100 dark:border-slate-800">
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} className="py-4 px-4">
        <Skeleton height="18px" width={i === 0 ? '70%' : '50%'} />
      </td>
    ))}
  </tr>
);

export default Skeleton;
