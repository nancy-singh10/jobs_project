import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Copy,
  Check,
  Clock,
  Layers,
  AlertTriangle,
  FolderKanban,
  CheckCircle2,
  Calendar,
  Terminal,
} from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const JobDetailPage = () => {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .getJobById(jobId)
      .then(setJob)
      .catch((err) => setError(err.message || 'Failed to load job details'))
      .finally(() => setLoading(false));
  }, [jobId]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="py-20 text-center text-zinc-400 text-sm">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading job parameters from PostgreSQL...
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="space-y-4">
        <Link
          to="/jobs"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Jobs</span>
        </Link>
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-6 text-center text-rose-300 text-sm">
          {error || 'Job not found'}
        </div>
      </div>
    );
  }

  // Lifecycle steps for visual timeline
  const lifecycleSteps = [
    { state: 'PENDING', label: '1. Ingested & Stored (Pending)' },
    { state: 'QUEUED', label: '2. Queued' },
    { state: 'RUNNING', label: '3. Worker Execution (Phase 2)' },
    { state: 'COMPLETED', label: '4. Completed' },
  ];

  const getStepStatus = (stepState) => {
    if (job.status === stepState) return 'current';
    if (job.status === 'COMPLETED') return 'completed';
    if (job.status === 'RUNNING' && (stepState === 'PENDING' || stepState === 'QUEUED')) return 'completed';
    if (job.status === 'QUEUED' && stepState === 'PENDING') return 'completed';
    return 'upcoming';
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Navigation & Header */}
      <div>
        <Link
          to="/jobs"
          className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-indigo-400 transition-colors mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Jobs List</span>
        </Link>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold font-mono text-white tracking-tight">{job.id}</h1>
            <button
              onClick={() => copyToClipboard(job.id)}
              className="p-1 rounded bg-[#161a25] hover:bg-[#202636] border border-[#252b3d] text-zinc-400 hover:text-white cursor-pointer"
              title="Copy Job UUID"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={job.status} />
            <PriorityBadge priority={job.priority} />
          </div>
        </div>
      </div>

      {/* Phase 2 Execution Notice Banner */}
      <div className="bg-indigo-950/30 border border-indigo-500/30 rounded-xl p-4 flex items-start gap-3">
        <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0">
          <Terminal className="w-4 h-4" />
        </div>
        <div className="text-xs space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-white">Execution Status:</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/40">
              {job.status === 'COMPLETED'
                ? 'EXECUTION COMPLETED'
                : job.status === 'RUNNING'
                ? 'WORKER EXECUTING NOW'
                : job.status === 'FAILED'
                ? 'EXECUTION FAILED'
                : 'DISPATCHED TO QUEUE (PENDING WORKER)'}
            </span>
          </div>
          <p className="text-zinc-300">
            {job.phase_1_status_note ||
              'Background workers consume from the Redis queue and record full execution attempts in PostgreSQL.'}
          </p>
        </div>
      </div>

      {/* Lifecycle Timeline */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-3">
        <h2 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
          Job Lifecycle State Machine
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-2">
          {lifecycleSteps.map((step, idx) => {
            const stepStatus = getStepStatus(step.state);
            return (
              <div
                key={step.state}
                className={`p-3 rounded-lg border text-xs transition-colors ${
                  stepStatus === 'current'
                    ? 'bg-amber-500/10 border-amber-500/40 text-amber-300 font-medium'
                    : stepStatus === 'completed'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-[#0e1017] border-[#1e2230] text-zinc-400'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider">Step {idx + 1}</span>
                  {stepStatus === 'completed' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  {stepStatus === 'current' && <Clock className="w-3.5 h-3.5 text-amber-400 animate-pulse" />}
                </div>
                <div className="font-semibold">{step.label}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Metadata Card */}
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
          <h2 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
            Metadata & Configuration
          </h2>
          <dl className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Task Type</dt>
              <dd className="font-mono text-zinc-200 font-medium">{job.task_type}</dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Project</dt>
              <dd className="text-indigo-400 font-medium">
                <Link to={`/jobs?project_id=${job.project_id}`} className="hover:underline">
                  {job.project_name}
                </Link>
              </dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Project UUID</dt>
              <dd className="font-mono text-[11px] text-zinc-400">{job.project_id}</dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Priority Level</dt>
              <dd className="font-mono text-zinc-200">{job.priority} / 10</dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Persistence Target</dt>
              <dd className="font-mono text-emerald-400">PostgreSQL 17 (flowops_jobs)</dd>
            </div>
          </dl>
        </div>

        {/* Timestamps Card */}
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
          <h2 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
            Lifecycle Timestamps
          </h2>
          <dl className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Created At (Ingested)</dt>
              <dd className="font-mono text-zinc-300">
                {new Date(job.created_at).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Last Updated</dt>
              <dd className="font-mono text-zinc-300">
                {new Date(job.updated_at).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Started At</dt>
              <dd className="font-mono text-zinc-400">
                {job.started_at ? new Date(job.started_at).toLocaleString() : 'Not started (Phase 2)'}
              </dd>
            </div>
            <div className="flex justify-between py-1.5 border-b border-[#1b1e2b]">
              <dt className="text-zinc-400">Completed At</dt>
              <dd className="font-mono text-zinc-400">
                {job.completed_at ? new Date(job.completed_at).toLocaleString() : 'Not completed (Phase 2)'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Execution History Table */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-[#1e2230] bg-[#141724] flex items-center justify-between">
          <span className="text-xs font-semibold text-white">Worker Execution History ({job.executions?.length || 0} attempts)</span>
          <span className="text-[11px] font-mono text-zinc-400">PostgreSQL Durable Records</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0e1017] text-zinc-400 font-medium border-b border-[#1e2230]">
              <tr>
                <th className="py-2.5 px-4">Attempt</th>
                <th className="py-2.5 px-4">Worker Identity</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Duration</th>
                <th className="py-2.5 px-4">Started At</th>
                <th className="py-2.5 px-4">Ended At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2230] text-zinc-300">
              {!job.executions || job.executions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-zinc-400">
                    No worker execution recorded yet. Task is waiting in queue.
                  </td>
                </tr>
              ) : (
                job.executions.map((exec) => (
                  <tr key={exec.id} className="hover:bg-[#151926]">
                    <td className="py-2.5 px-4 font-mono font-semibold text-indigo-300">#{exec.attempt_number}</td>
                    <td className="py-2.5 px-4 font-mono text-zinc-200">{exec.worker_name}</td>
                    <td className="py-2.5 px-4"><StatusBadge status={exec.status} /></td>
                    <td className="py-2.5 px-4 font-mono">{exec.duration_ms ? `${exec.duration_ms} ms` : 'Running...'}</td>
                    <td className="py-2.5 px-4 font-mono text-[11px] text-zinc-400">
                      {new Date(exec.started_at).toLocaleString()}
                    </td>
                    <td className="py-2.5 px-4 font-mono text-[11px] text-zinc-400">
                      {exec.ended_at ? new Date(exec.ended_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Payload Viewer Card */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-[#1e2230] bg-[#141724] flex items-center justify-between">
          <span className="text-xs font-semibold text-white">Task Payload (Immutable JSON)</span>
          <button
            onClick={() => copyToClipboard(JSON.stringify(job.payload, null, 2))}
            className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white px-2 py-1 rounded bg-[#1e2333] transition-colors cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>Copy JSON</span>
          </button>
        </div>
        <div className="p-4 bg-[#0a0c12]">
          <pre className="text-xs font-mono text-indigo-300 overflow-x-auto p-2">
            {JSON.stringify(job.payload, null, 2)}
          </pre>
        </div>
      </div>

      {/* Result / Error Section */}
      {(job.result || job.error_message) && (
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-2">
          <h2 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
            Execution Output / Diagnostic
          </h2>
          {job.result && (
            <pre className="p-3 bg-[#0a0c12] rounded-lg text-xs font-mono text-emerald-400 overflow-x-auto">
              {JSON.stringify(job.result, null, 2)}
            </pre>
          )}
          {job.error_message && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs font-mono text-rose-300">
              {job.error_message}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
