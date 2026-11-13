import React, { useState, useEffect } from 'react';
import {
  Cpu,
  RefreshCw,
  Server,
  Zap,
  Activity,
  Layers,
  Terminal,
  CheckCircle2,
  AlertCircle,
  Clock,
} from 'lucide-react';
import { api } from '../api/client';

export const WorkersPage = () => {
  const [workersData, setWorkersData] = useState({ workers: [], count: 0 });
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWorkers = async () => {
    setLoading(true);
    setError(null);
    try {
      const [workersRes, healthRes] = await Promise.all([
        api.getWorkers(),
        api.getHealth(),
      ]);
      setWorkersData(workersRes || { workers: [], count: 0 });
      setHealthData(healthRes || null);
    } catch (err) {
      setError(err.message || 'Failed to fetch worker telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkers();
    const interval = setInterval(fetchWorkers, 10000); // 10s polling
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#1e2230]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Celery Background Workers</h1>
            <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
              Phase 2 Telemetry
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Independent background execution processes consuming from the Redis message queue
          </p>
        </div>
        <button
          onClick={fetchWorkers}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141824] hover:bg-[#1a2030] text-zinc-300 text-xs font-medium border border-[#232838] transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Workers</span>
        </button>
      </div>

      {/* Broker & Engine Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* API Health */}
        <div className="p-4 rounded-xl bg-[#11141e] border border-[#1e2230] flex items-center justify-between">
          <div>
            <div className="text-[11px] text-zinc-400 font-medium">Django API Gateway</div>
            <div className="text-sm font-bold text-white mt-0.5">Online & Healthy</div>
          </div>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>

        {/* PostgreSQL Health */}
        <div className="p-4 rounded-xl bg-[#11141e] border border-[#1e2230] flex items-center justify-between">
          <div>
            <div className="text-[11px] text-zinc-400 font-medium">PostgreSQL Source of Truth</div>
            <div className="text-sm font-bold text-white mt-0.5">
              {healthData?.database?.status === 'healthy' ? 'Connected (PostgreSQL 17)' : 'Checking...'}
            </div>
          </div>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>

        {/* Redis Health */}
        <div className="p-4 rounded-xl bg-[#11141e] border border-[#1e2230] flex items-center justify-between">
          <div>
            <div className="text-[11px] text-zinc-400 font-medium">Redis Message Broker</div>
            <div className="text-sm font-bold text-white mt-0.5">
              {healthData?.redis?.status === 'healthy' ? 'Online (redis://localhost:6379)' : 'Standby / Broker URL Configured'}
            </div>
          </div>
          <div className={`p-2 rounded-lg border ${
            healthData?.redis?.status === 'healthy'
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
          }`}>
            <Zap className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Discovered Workers List */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[#1e2230] bg-[#141724] flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white">Connected Worker Nodes</h2>
            <p className="text-xs text-zinc-400">Live telemetry reported via Celery broker inspect</p>
          </div>
          <span className="font-mono text-xs px-2.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
            {workersData.count} node(s) active
          </span>
        </div>

        <div className="p-5">
          {workersData.count === 0 ? (
            <div className="py-8 text-center space-y-3">
              <Cpu className="w-10 h-10 text-zinc-400 mx-auto" />
              <div>
                <p className="text-sm font-semibold text-zinc-300">No external Celery worker processes detected</p>
                <p className="text-xs text-zinc-400 mt-1 max-w-lg mx-auto">
                  Start one or more independent worker processes using the commands below to process jobs from the Redis queue.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {workersData.workers.map((w, idx) => (
                <div
                  key={w.name || idx}
                  className="p-4 rounded-lg bg-[#0e1017] border border-[#1e2230] flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-sm font-semibold text-white">{w.name}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        {w.status || 'Online'}
                      </span>
                    </div>
                    <div className="text-xs text-zinc-400 flex items-center gap-4">
                      <span>Concurrency: <strong className="text-zinc-200">{w.concurrency}</strong></span>
                      <span>Active Tasks: <strong className="text-indigo-300">{w.active_tasks_count}</strong></span>
                    </div>
                  </div>
                  <div className="text-[11px] font-mono text-zinc-400 bg-[#161a25] px-3 py-1.5 rounded border border-[#222838]">
                    Registered Handlers: {w.registered_tasks?.length || 1}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* How to Run Multiple Workers Card */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
        <div className="flex items-center gap-2 text-indigo-400">
          <Terminal className="w-4 h-4" />
          <h2 className="text-sm font-semibold text-white">How to Launch Independent Workers</h2>
        </div>
        <p className="text-xs text-zinc-300">
          In Phase 2, you can scale throughput by launching multiple Celery worker processes with distinct identities.
        </p>

        <div className="space-y-3 font-mono text-xs">
          <div>
            <div className="text-zinc-400 text-[11px] mb-1 font-sans">Worker 1 (Terminal A):</div>
            <div className="bg-[#0b0d13] p-3 rounded-lg border border-[#1e2230] text-indigo-300 select-all">
              celery -A config worker --loglevel=info --concurrency=2 -n worker1@%h -P solo
            </div>
          </div>

          <div>
            <div className="text-zinc-400 text-[11px] mb-1 font-sans">Worker 2 (Terminal B):</div>
            <div className="bg-[#0b0d13] p-3 rounded-lg border border-[#1e2230] text-indigo-300 select-all">
              celery -A config worker --loglevel=info --concurrency=2 -n worker2@%h -P solo
            </div>
          </div>

          <div>
            <div className="text-zinc-400 text-[11px] mb-1 font-sans">Local Redis Service (if Redis is not installed as a Windows service):</div>
            <div className="bg-[#0b0d13] p-3 rounded-lg border border-[#1e2230] text-emerald-300 select-all">
              python backend/manage.py run_redis
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

