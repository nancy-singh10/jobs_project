import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Layers,
  FolderKanban,
  Cpu,
  Settings,
  BookOpen,
  Database,
  ExternalLink,
  PlusCircle,
} from 'lucide-react';

export const Sidebar = ({ onOpenSubmitModal }) => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/jobs', label: 'Jobs', icon: Layers },
    { to: '/workers', label: 'Workers', icon: Cpu },
    { to: '/projects', label: 'Projects', icon: FolderKanban },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0d0f15] border-r border-[#1e2230] flex flex-col h-screen sticky top-0 shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#1e2230] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-indigo-500/20">
            F
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-white">FlowOps</span>
              <span className="text-[10px] uppercase font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 px-1.5 py-0.2 rounded">
                Phase 1
              </span>
            </div>
            <p className="text-xs text-zinc-400">Job Orchestration</p>
          </div>
        </div>
      </div>

      {/* Quick Action Button */}
      <div className="p-4">
        <button
          onClick={onOpenSubmitModal}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium px-4 py-2.5 rounded-lg text-sm transition-all duration-150 shadow-sm shadow-indigo-600/30 cursor-pointer"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Submit Job</span>
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[#1a1f2e] text-indigo-400 border-l-2 border-indigo-500 font-semibold'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-[#141722]'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* External Resources */}
      <div className="p-3 border-t border-[#1e2230] space-y-1">
        <a
          href="http://127.0.0.1:8000/api/docs/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-between px-3.5 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-indigo-400 hover:bg-[#141722] transition-colors"
        >
          <div className="flex items-center gap-2.5">
            <BookOpen className="w-4 h-4 text-zinc-400" />
            <span>Swagger API Docs</span>
          </div>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {/* Engine Status Footer */}
      <div className="p-4 border-t border-[#1e2230] bg-[#0a0c12]">
        <div className="flex items-center gap-2 text-xs text-zinc-400 mb-1.5">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-medium text-zinc-300">PostgreSQL 17</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-auto" />
        </div>
        <p className="text-[11px] text-zinc-500">
          Database: <span className="font-mono text-zinc-400">flowops_db</span>
        </p>
      </div>
    </aside>
  );
};
