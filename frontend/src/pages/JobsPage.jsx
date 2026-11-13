import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  Search,
  Filter,
  RefreshCw,
  PlusCircle,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  Layers,
  X,
} from 'lucide-react';
import { api } from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';

export const JobsPage = ({ onOpenSubmitModal }) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [jobs, setJobs] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Filter states
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [selectedStatus, setSelectedStatus] = useState(searchParams.get('status') || '');
  const [selectedProject, setSelectedProject] = useState(searchParams.get('project_id') || '');
  const [taskTypeFilter, setTaskTypeFilter] = useState(searchParams.get('task_type') || '');

  // Load projects for dropdown filter
  useEffect(() => {
    api.getProjects().then(setProjects).catch(console.error);
  }, []);

  const fetchJobsList = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        page_size: pageSize,
      };
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (selectedStatus) params.status = selectedStatus;
      if (selectedProject) params.project_id = selectedProject;
      if (taskTypeFilter.trim()) params.task_type = taskTypeFilter.trim();

      const data = await api.getJobs(params);
      setJobs(data?.results || []);
      setTotalCount(data?.count || 0);
      setTotalPages(data?.total_pages || 1);
      setCurrentPage(data?.page || 1);
    } catch (err) {
      setError(err.message || 'Failed to retrieve jobs list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobsList(1);
  }, [selectedStatus, selectedProject, pageSize]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchJobsList(1);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedStatus('');
    setSelectedProject('');
    setTaskTypeFilter('');
    setSearchParams({});
    // reload next tick
    setTimeout(() => {
      api.getJobs({ page: 1, page_size: pageSize }).then((data) => {
        setJobs(data?.results || []);
        setTotalCount(data?.count || 0);
        setTotalPages(data?.total_pages || 1);
        setCurrentPage(1);
      });
    }, 10);
  };

  const copyJobId = (id) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#1e2230]">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Background Jobs</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Browse, inspect, and filter jobs persisted in PostgreSQL
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchJobsList(currentPage)}
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

      {/* Filters Bar */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-4 space-y-3">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Job ID or Task..."
              className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg pl-9 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-400 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          {/* Status Dropdown */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="QUEUED">Queued</option>
              <option value="RUNNING">Running</option>
              <option value="COMPLETED">Completed</option>
              <option value="FAILED">Failed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          {/* Project Dropdown */}
          <div>
            <select
              value={selectedProject}
              onChange={(e) => setSelectedProject(e.target.value)}
              className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Projects</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          {/* Buttons */}
          <div className="flex gap-2">
            <button
              type="submit"
              className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium py-1.5 px-3 rounded-lg transition-colors cursor-pointer"
            >
              Filter
            </button>
            {(searchQuery || selectedStatus || selectedProject || taskTypeFilter) && (
              <button
                type="button"
                onClick={clearFilters}
                className="bg-[#1b202d] hover:bg-[#252c3f] text-zinc-300 text-xs font-medium py-1.5 px-3 rounded-lg transition-colors flex items-center gap-1 cursor-pointer"
                title="Clear filters"
              >
                <X className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </form>
      </div>

      {/* Error Callout */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-xs text-rose-300 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={() => fetchJobsList(currentPage)}
            className="underline hover:text-white font-medium cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Jobs Table */}
      <div className="bg-[#11141e] border border-[#1e2230] rounded-xl overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0e1017] text-zinc-400 font-medium border-b border-[#1e2230]">
              <tr>
                <th className="py-3 px-4">Job ID</th>
                <th className="py-3 px-4">Task Type</th>
                <th className="py-3 px-4">Project</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Created At</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2230] text-zinc-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-zinc-400">
                    Loading jobs from PostgreSQL...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-zinc-400">
                    <Layers className="w-8 h-8 mx-auto text-zinc-400 mb-2" />
                    <p className="font-medium text-sm text-zinc-400">No jobs match your query.</p>
                    <p className="text-xs text-zinc-400 mt-1">
                      Adjust your filters or submit a new background job.
                    </p>
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-[#151926] transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-zinc-300">
                      <div className="flex items-center gap-1.5">
                        <span title={job.id}>{job.id.slice(0, 8)}...</span>
                        <button
                          onClick={() => copyJobId(job.id)}
                          className="text-zinc-400 hover:text-indigo-400 p-0.5 rounded cursor-pointer"
                          title="Copy Full UUID"
                        >
                          {copiedId === job.id ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-white">{job.task_type}</td>
                    <td className="py-3 px-4 text-zinc-400 max-w-[150px] truncate">
                      {job.project_name}
                    </td>
                    <td className="py-3 px-4">
                      <PriorityBadge priority={job.priority} />
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={job.status} />
                    </td>
                    <td className="py-3 px-4 text-zinc-400 font-mono text-[11px]">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/jobs/${job.id}`}
                        className="inline-block px-2.5 py-1 rounded bg-[#1a1f2e] hover:bg-indigo-600 hover:text-white text-indigo-400 text-xs font-medium border border-[#272d3f] transition-colors"
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

        {/* Pagination Bar */}
        <div className="px-5 py-3 border-t border-[#1e2230] bg-[#0e1017] flex items-center justify-between text-xs text-zinc-400">
          <div>
            Showing <span className="text-zinc-200 font-semibold">{jobs.length}</span> of{' '}
            <span className="text-zinc-200 font-semibold">{totalCount}</span> total jobs
          </div>
          <div className="flex items-center gap-3">
            <span className="text-zinc-400">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex gap-1">
              <button
                onClick={() => fetchJobsList(currentPage - 1)}
                disabled={currentPage <= 1 || loading}
                className="p-1 rounded bg-[#161a25] border border-[#252b3d] hover:bg-[#202636] disabled:opacity-40 disabled:hover:bg-[#161a25] text-zinc-300 cursor-pointer"
                title="Previous Page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => fetchJobsList(currentPage + 1)}
                disabled={currentPage >= totalPages || loading}
                className="p-1 rounded bg-[#161a25] border border-[#252b3d] hover:bg-[#202636] disabled:opacity-40 disabled:hover:bg-[#161a25] text-zinc-300 cursor-pointer"
                title="Next Page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
