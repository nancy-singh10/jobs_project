import React from 'react';
import {
  Database,
  Layers,
  BookOpen,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
  Server,
  Zap,
} from 'lucide-react';

export const SettingsPage = () => {
  const checklist = [
    { label: 'Django & PostgreSQL configured with production settings', done: true },
    { label: 'Project model and CRUD APIs created with job counts', done: true },
    { label: 'Job model, indexes, and migrations applied to PostgreSQL', done: true },
    { label: 'Job submission API with atomic transaction and immediate UUID', done: true },
    { label: 'Multi-field job listing, filtering, search, and pagination', done: true },
    { label: 'Job detail inspection and lifecycle timeline display', done: true },
    { label: 'Real-time metrics API powering dashboard overview', done: true },
    { label: 'OpenAPI 3.0 schema and interactive Swagger UI documentation', done: true },
    { label: 'Comprehensive automated Pytest backend suite passing (33/33)', done: true },
    { label: 'React, Vite, and Tailwind CSS developer dashboard connected to real APIs', done: true },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="pb-2 border-b border-[#1e2230]">
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings & Architecture</h1>
        <p className="text-xs text-zinc-400 mt-1">
          Operational boundaries, database configuration, and Phase 2 roadmap
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Storage Engine Status */}
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2.5 text-emerald-400">
            <Database className="w-5 h-5" />
            <h2 className="text-sm font-semibold text-white">Database & Persistence Engine</h2>
          </div>
          <div className="bg-[#0b0d13] p-4 rounded-lg border border-[#1e2230] font-mono text-xs space-y-2 text-zinc-300">
            <div className="flex justify-between">
              <span className="text-zinc-400">Database Engine:</span>
              <span className="text-emerald-400">PostgreSQL 17 (psycopg2)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-400">Database Name:</span>
              <span className="text-zinc-200">flowops_db</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-400">Host & Port:</span>
              <span className="text-zinc-200">localhost:5432</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-400">Primary Tables:</span>
              <span className="text-zinc-200">flowops_projects, flowops_jobs</span>
            </div>
            <div className="flex justify-between">
              <span className="text-zinc-400">Isolation Level:</span>
              <span className="text-zinc-200">Atomic Database Transactions</span>
            </div>
          </div>
          <p className="text-xs text-zinc-400">
            All submitted background jobs are safely validated and written to PostgreSQL. No ephemeral memory queues are used in Phase 1.
          </p>
        </div>

        {/* API & Documentation */}
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2.5 text-indigo-400">
            <Server className="w-5 h-5" />
            <h2 className="text-sm font-semibold text-white">REST API & OpenAPI Schema</h2>
          </div>
          <div className="bg-[#0b0d13] p-4 rounded-lg border border-[#1e2230] text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Base Endpoint:</span>
              <span className="font-mono text-indigo-300">/api/v1/</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Swagger UI:</span>
              <a
                href="http://127.0.0.1:8000/api/docs/"
                target="_blank"
                rel="noreferrer"
                className="font-mono text-indigo-400 hover:underline flex items-center gap-1"
              >
                <span>/api/docs/</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">OpenAPI 3.0 Schema:</span>
              <a
                href="http://127.0.0.1:8000/api/schema/"
                target="_blank"
                rel="noreferrer"
                className="font-mono text-indigo-400 hover:underline flex items-center gap-1"
              >
                <span>/api/schema/</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
          <p className="text-xs text-zinc-400">
            Full request/response examples, field-level validation schemas, and envelope definitions are generated automatically with drf-spectacular.
          </p>
        </div>
      </div>

      {/* Phase 1 Completion Checklist */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">
            Phase 1 Implementation Tracker (10/10 Complete)
          </h2>
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            100% Operational
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {checklist.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-2 p-2.5 rounded-lg bg-[#0e1017] border border-[#1c202d] text-xs text-zinc-300"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Phase 2 Roadmap & Deliberate Postponement */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-5 space-y-4">
        <div className="flex items-center gap-2.5 text-amber-400">
          <Zap className="w-5 h-5" />
          <h2 className="text-sm font-semibold text-white">
            Architecture Roadmap — Deliberately Postponed to Phase 2
          </h2>
        </div>
        <p className="text-xs text-zinc-300">
          To maintain architectural rigor and prevent superficial pseudo-implementations, distributed execution is deliberately scheduled for Phase 2:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-[#0e1017] border border-[#1e2230] rounded-lg">
            <h3 className="font-semibold text-zinc-200 mb-1">Redis Queue Engine</h3>
            <p className="text-zinc-400 text-[11px]">
              Priority queue brokers, Redis streams, and in-memory queue management.
            </p>
          </div>
          <div className="p-3 bg-[#0e1017] border border-[#1e2230] rounded-lg">
            <h3 className="font-semibold text-zinc-200 mb-1">Distributed Workers</h3>
            <p className="text-zinc-400 text-[11px]">
              Dedicated worker processes consuming tasks, executing Python handlers, and capturing outputs.
            </p>
          </div>
          <div className="p-3 bg-[#0e1017] border border-[#1e2230] rounded-lg">
            <h3 className="font-semibold text-zinc-200 mb-1">Retries & Dead Letters</h3>
            <p className="text-zinc-400 text-[11px]">
              Exponential backoff policies, dead letter queues (DLQ), and failure notification webhooks.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
