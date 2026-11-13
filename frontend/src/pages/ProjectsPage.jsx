import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FolderKanban,
  PlusCircle,
  RefreshCw,
  Edit2,
  Calendar,
  Layers,
  X,
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { api } from '../api/client';

export const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState(null);

  const fetchProjectsList = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProjects();
      setProjects(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjectsList();
  }, []);

  const openCreateModal = () => {
    setEditingProject(null);
    setProjectName('');
    setProjectDescription('');
    setModalError(null);
    setIsModalOpen(true);
  };

  const openEditModal = (proj) => {
    setEditingProject(proj);
    setProjectName(proj.name);
    setProjectDescription(proj.description || '');
    setModalError(null);
    setIsModalOpen(true);
  };

  const handleSaveProject = async (e) => {
    e.preventDefault();
    setModalError(null);
    setModalLoading(true);

    try {
      if (editingProject) {
        await api.updateProject(editingProject.id, {
          name: projectName.trim(),
          description: projectDescription.trim(),
        });
      } else {
        await api.createProject({
          name: projectName.trim(),
          description: projectDescription.trim(),
        });
      }
      setIsModalOpen(false);
      fetchProjectsList();
    } catch (err) {
      const details = err.details
        ? Object.entries(err.details)
            .map(([k, v]) => `${k}: ${v}`)
            .join(' | ')
        : '';
      setModalError(`${err.message || 'Operation failed'} ${details}`);
    } finally {
      setModalLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-[#1e2230]">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Tenant Projects</h1>
          <p className="text-xs text-zinc-400 mt-1">
            Manage external client applications submitting background tasks to FlowOps
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchProjectsList}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#141824] hover:bg-[#1a2030] text-zinc-300 text-xs font-medium border border-[#232838] transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={openCreateModal}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors shadow-sm shadow-indigo-600/30 cursor-pointer"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Project</span>
          </button>
        </div>
      </div>

      {/* Error Callout */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-xs text-rose-300 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={fetchProjectsList}
            className="underline hover:text-white font-medium cursor-pointer"
          >
            Retry
          </button>
        </div>
      )}

      {/* Projects Grid */}
      {loading ? (
        <div className="py-16 text-center text-zinc-400 text-xs">
          Loading projects from database...
        </div>
      ) : projects.length === 0 ? (
        <div className="bg-[#11141e] border border-[#1e2230] rounded-xl p-12 text-center text-zinc-400">
          <FolderKanban className="w-10 h-10 mx-auto text-zinc-400 mb-2" />
          <p className="font-semibold text-sm text-zinc-300">No projects registered yet.</p>
          <p className="text-xs text-zinc-400 mt-1 mb-4">
            Create your first tenant project to begin submitting background jobs.
          </p>
          <button
            onClick={openCreateModal}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg cursor-pointer"
          >
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="bg-[#11141e] border border-[#1e2230] hover:border-[#2b3348] rounded-xl p-5 flex flex-col justify-between transition-colors shadow-xs"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
                      <FolderKanban className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-white">{proj.name}</h3>
                      <span className="font-mono text-[10px] text-zinc-400 select-all">
                        {proj.id.slice(0, 8)}...
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => openEditModal(proj)}
                    className="p-1 rounded hover:bg-[#1f2433] text-zinc-400 hover:text-zinc-200 transition-colors cursor-pointer"
                    title="Edit Project"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <p className="text-xs text-zinc-400 line-clamp-3 mt-2 min-h-[36px]">
                  {proj.description || 'No description provided.'}
                </p>
              </div>

              <div className="pt-4 mt-4 border-t border-[#1b1e2a] flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 text-zinc-400">
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                  <span className="font-medium text-zinc-300 font-mono">
                    {proj.jobs_count || 0}
                  </span>
                  <span>jobs</span>
                </div>
                <Link
                  to={`/jobs?project_id=${proj.id}`}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium hover:underline"
                >
                  View Jobs &rarr;
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Project Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
          <div className="bg-[#12151f] border border-[#232838] rounded-xl max-w-md w-full shadow-2xl overflow-hidden">
            <div className="px-5 py-4 border-b border-[#232838] flex items-center justify-between bg-[#151824]">
              <h2 className="text-sm font-semibold text-white">
                {editingProject ? 'Edit Project' : 'Create New Project'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-zinc-400 hover:text-white p-1 rounded hover:bg-[#1f2433]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveProject} className="p-5 space-y-4">
              {modalError && (
                <div className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 text-xs text-rose-300">
                  {modalError}
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Project Name <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="e.g. E-Commerce Platform"
                  required
                  className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  rows={3}
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Summary of workload, external application domain, etc."
                  className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-1.5 text-xs font-medium text-zinc-400 hover:text-white rounded-lg hover:bg-[#1a1f2e] cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalLoading || !projectName.trim()}
                  className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium px-4 py-1.5 rounded-lg transition-colors cursor-pointer"
                >
                  {modalLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>{editingProject ? 'Save Changes' : 'Create Project'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
