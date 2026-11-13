import React from 'react';

export const PriorityBadge = ({ priority }) => {
  const p = Number(priority) || 5;

  let colorClasses = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
  let label = 'Medium';

  if (p <= 3) {
    colorClasses = 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    label = 'Low';
  } else if (p >= 9) {
    colorClasses = 'bg-rose-500/10 text-rose-400 border-rose-500/30 font-semibold';
    label = 'Critical';
  } else if (p >= 7) {
    colorClasses = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    label = 'High';
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs border font-mono ${colorClasses}`}
      title={`Priority level ${p}/10 (${label})`}
    >
      <span className="font-semibold">P{p}</span>
      <span className="opacity-75 text-[10px] uppercase font-sans">({label})</span>
    </span>
  );
};
