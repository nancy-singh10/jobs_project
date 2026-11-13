import React from 'react';

const statusConfig = {
  PENDING: {
    label: 'Pending',
    bgColor: 'bg-amber-500/10',
    textColor: 'text-amber-400',
    borderColor: 'border-amber-500/30',
    dotColor: 'bg-amber-400',
  },
  QUEUED: {
    label: 'Queued',
    bgColor: 'bg-sky-500/10',
    textColor: 'text-sky-400',
    borderColor: 'border-sky-500/30',
    dotColor: 'bg-sky-400',
  },
  RUNNING: {
    label: 'Running',
    bgColor: 'bg-purple-500/10',
    textColor: 'text-purple-400',
    borderColor: 'border-purple-500/30',
    dotColor: 'bg-purple-400 animate-pulse',
  },
  COMPLETED: {
    label: 'Completed',
    bgColor: 'bg-emerald-500/10',
    textColor: 'text-emerald-400',
    borderColor: 'border-emerald-500/30',
    dotColor: 'bg-emerald-400',
  },
  FAILED: {
    label: 'Failed',
    bgColor: 'bg-rose-500/10',
    textColor: 'text-rose-400',
    borderColor: 'border-rose-500/30',
    dotColor: 'bg-rose-400',
  },
  CANCELLED: {
    label: 'Cancelled',
    bgColor: 'bg-zinc-500/10',
    textColor: 'text-zinc-400',
    borderColor: 'border-zinc-500/30',
    dotColor: 'bg-zinc-400',
  },
};

export const StatusBadge = ({ status }) => {
  const config = statusConfig[status] || {
    label: status || 'Unknown',
    bgColor: 'bg-zinc-800',
    textColor: 'text-zinc-400',
    borderColor: 'border-zinc-700',
    dotColor: 'bg-zinc-500',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.bgColor} ${config.textColor} ${config.borderColor}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dotColor}`} />
      {config.label}
    </span>
  );
};
