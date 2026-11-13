import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Layers,
  Clock,
  CheckCircle2,
  XCircle,
  FolderKanban,
  ArrowRight,
  RefreshCw,
  PlusCircle,
  Copy,
  Check,
  Cpu,
  Zap,
  Activity,
} from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const DashboardPage = ({ onOpenSubmitModal }) => {
  const [stats, setStats] = useState({
    total_jobs: 0,
    running_jobs: 0,
    completed_jobs: 0,
    failed_jobs: 0,
    pending_jobs: 0,
    queued_jobs: 0,
    total_executions: 0,
    avg_duration_ms: 0,
    recent_executions: [],
  });
  const [recentJobs, setRecentJobs] = useState([]);
  const [projects, setProjects] = useState([]);
  const [workersData, setWorkersData] = useState({ workers: [], count: 0 });
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, jobsData, projectsData, workersRes] = await Promise.all([
        api.getDashboardStats(),
        api.getJobs({ page_size: 6 }),
        api.getProjects(),
        api.getWorkers(),
      ]);

      setStats(statsData || {});
      setRecentJobs(jobsData?.results || []);
      setProjects(projectsData || []);
      setWorkersData(workersRes || { workers: [], count: 0 });
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard data from FlowOps backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(loadDashboardData, 4000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const copyJobId = (id) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const metricCards = [
    {
      title: 'Total Jobs',
      value: stats.total_jobs ?? 0,
      icon: Layers,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/20',
      note: 'Durable in PostgreSQL',
    },
    {
      title: 'Running',
      value: stats.running_jobs ?? 0,
      icon: Activity,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
      note: 'Active on Celery workers',
      pulse: (stats.running_jobs ?? 0) > 0,
    },
    {
      title: 'Completed',
      value: stats.completed_jobs ?? 0,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
      note: `Avg execution: ${stats.avg_duration_ms || 0} ms`,
    },
    {
      title: 'Failed',
      value: stats.failed_jobs ?? 0,
      icon: XCircle,
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10',
      borderColor: 'border-rose-500/20',
      note: 'Diagnostic captured',
    },
    {
      title: 'Pending & Queued',
      value: (stats.pending_jobs || 0) + (stats.queued_jobs || 0),
      icon: Clock,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
      note: `${stats.queued_jobs || 0} ready in Redis queue`,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#1e2230]">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold text-white tracking-tight">FlowOps Dashboard</h1>
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              API Connected
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Phase 2: Redis Queue & Asynchronous Celery Background Worker Execution
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-zinc-400 select-none cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="accent-indigo-500 cursor-pointer"
            />
            <span>Auto-refresh (4s)</span>
          </label>
          <button
            onClick={loadDashboardData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141824] hover:bg-[#1a2030] text-zinc-300 text-xs font-medium border border-[#232838] transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={onOpenSubmitModal}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors shadow-sm shadow-indigo-600/30 cursor-pointer"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Submit Job</span>
          </button>
        </div>
      </div>

      {/* Error Callout */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-xs text-rose-300 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={loadDashboardData}
            className="underline hover:text-white font-medium cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
        {metricCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className={`p-4 rounded-xl bg-[#11141e] border ${card.borderColor} flex flex-col justify-between`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-zinc-400">{card.title}</span>
                <div className={`p-1.5 rounded-md ${card.bgColor} ${card.color}`}>
                  <Icon className={`w-4 h-4 ${card.pulse ? 'animate-pulse' : ''}`} />
                </div>
              </div>
              <div className="my-2">
                <span className="text-2xl font-bold font-mono text-white">
                  {loading ? '—' : card.value}
                </span>
              </div>
              <div className="text-[10px] text-zinc-400 font-medium">{card.note}</div>
            </div>
          );
        })}
      </div>

      {/* Execution Telemetry + Workers Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Job Executions (2 columns on large screen) */}
        <div className="lg:col-span-2 bg-[#11141e] border border-[#1e2230] rounded-xl overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-[#1e2230] flex items-center justify-between bg-[#141724]">
            <div>
              <h2 className="text-sm font-semibold text-white">Recent Job Executions</h2>
              <p className="text-xs text-zinc-400">Worker execution records stored in PostgreSQL</p>
            </div>
            <Link
              to="/jobs"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 transition-colors"
            >
              <span>View all jobs</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto flex-1">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0e1017] text-zinc-400 font-medium border-b border-[#1e2230]">
                <tr>
                  <th className="py-2.5 px-4">Task</th>
                  <th className="py-2.5 px-4">Worker</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Duration</th>
                  <th className="py-2.5 px-4">Started At</th>
                  <th className="py-2.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e2230] text-zinc-300">
                {stats.recent_executions.length === 0 ? (
                  recentJobs.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-zinc-400">
                        No executions recorded yet. Submit a job to trigger Celery workers.
                      </td>
                    </tr>
                  ) : (
                    recentJobs.map((job) => (
                      <tr key={job.id} className="hover:bg-[#151926] transition-colors">
                        <td className="py-3 px-4 font-mono font-medium text-white">{job.task_type}</td>
                        <td className="py-3 px-4 text-zinc-400 font-mono text-[11px]">—</td>
                        <td className="py-3 px-4"><StatusBadge status={job.status} /></td>
                        <td className="py-3 px-4 font-mono text-zinc-400">—</td>
                        <td className="py-3 px-4 font-mono text-[11px] text-zinc-400">
                          {new Date(job.created_at).toLocaleTimeString()}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <Link to={`/jobs/${job.id}`} className="text-xs text-indigo-400 hover:underline">
                            Details
                          </Link>
                        </td>
                      </tr>
                    ))
                  )
                ) : (
                  stats.recent_executions.map((exec) => (
                    <tr key={exec.id} className="hover:bg-[#151926] transition-colors">
                      <td className="py-3 px-4 font-mono font-medium text-white">{exec.task_type}</td>
                      <td className="py-3 px-4 text-zinc-300 font-mono text-[11px] truncate max-w-[140px]">
                        {exec.worker_name}
                      </td>
                      <td className="py-3 px-4">
                        <StatusBadge status={exec.status} />
                      </td>
                      <td className="py-3 px-4 font-mono text-zinc-300">
                        {exec.duration_ms ? `${exec.duration_ms} ms` : 'In progress...'}
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-zinc-400">
                        {new Date(exec.started_at).toLocaleTimeString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={`/jobs/${exec.job_id}`}
                          className="text-xs text-indigo-400 hover:text-indigo-300 font-medium hover:underline"
                        >
                          Inspect
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Connected Workers Widget */}
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl overflow-hidden flex flex-col">
          <div className="px-5 py-4 border-b border-[#1e2230] flex items-center justify-between bg-[#141724]">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-semibold text-white">Active Workers</h2>
            </div>
            <Link
              to="/workers"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1 transition-colors"
            >
              <span>Manage</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-4 space-y-3 flex-1 overflow-y-auto">
            {workersData.workers.length === 0 ? (
              <div className="py-6 text-center text-xs text-zinc-400 space-y-2">
                <Cpu className="w-8 h-8 mx-auto text-zinc-400" />
                <p className="font-semibold text-zinc-300">No worker processes detected</p>
                <p className="text-[11px] text-zinc-400">
                  Launch workers in terminal:
                  <br />
                  <code className="text-indigo-300 font-mono text-[10px]">
                    celery -A config worker -n worker1@%h -P solo
                  </code>
                </p>
              </div>
            ) : (
              workersData.workers.map((w, idx) => (
                <div
                  key={w.name || idx}
                  className="p-3.5 rounded-lg bg-[#0e1017] border border-[#1e2230] hover:border-[#2a3044] transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-xs font-mono text-white truncate max-w-[160px]">
                      {w.name}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {w.status || 'Online'}
                    </span>
                  </div>
                  <div className="mt-2 pt-2 border-t border-[#181b26] flex items-center justify-between text-[11px] text-zinc-400">
                    <span>Concurrency: {w.concurrency}</span>
                    <span className="text-indigo-300 font-medium">{w.active_tasks_count} active</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
