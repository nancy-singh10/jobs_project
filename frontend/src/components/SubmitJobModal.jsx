import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, CheckCircle, AlertTriangle, Send, Loader2, Sparkles, ExternalLink } from 'lucide-react';
import { api } from '../api/client';

const PRESET_TEMPLATES = [
  {
    type: 'invoice.generate',
    label: 'Invoice Gen',
    payload: { invoice_id: 10428, customer_email: 'customer@example.com', total_usd: 199.99 },
    priority: 7,
  },
  {
    type: 'email.send',
    label: 'Send Email',
    payload: { recipient: 'user@example.com', template: 'welcome_notification', retry_count: 0 },
    priority: 5,
  },
  {
    type: 'report.create',
    label: 'Create Report',
    payload: { report_period: '2026-Q4', format: 'pdf', notify_email: 'ops@company.org' },
    priority: 8,
  },
  {
    type: 'document.process',
    label: 'Process Doc',
    payload: { file_url: 's3://bucket/contracts/oct2026.pdf', ocr_enabled: true },
    priority: 4,
  },
];

export const SubmitJobModal = ({ isOpen, onClose, onJobSubmitted }) => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [projectId, setProjectId] = useState('');
  const [taskType, setTaskType] = useState('invoice.generate');
  const [payloadText, setPayloadText] = useState(
    JSON.stringify({ invoice_id: 123, customer_email: 'customer@example.com' }, null, 2)
  );
  const [priority, setPriority] = useState(5);
  const [statusVal, setStatusVal] = useState('PENDING');

  const [loading, setLoading] = useState(false);
  const [jsonError, setJsonError] = useState(null);
  const [apiError, setApiError] = useState(null);
  const [submittedJob, setSubmittedJob] = useState(null);

  // Load projects when modal opens
  useEffect(() => {
    if (isOpen) {
      setSubmittedJob(null);
      setApiError(null);
      api
        .getProjects()
        .then((data) => {
          setProjects(data || []);
          if (data && data.length > 0 && !projectId) {
            setProjectId(data[0].id);
          }
        })
        .catch((err) => {
          setApiError(err.message || 'Failed to load projects');
        });
    }
  }, [isOpen]);

  // Validate JSON on payload changes
  const handlePayloadChange = (e) => {
    const text = e.target.value;
    setPayloadText(text);
    try {
      const parsed = JSON.parse(text);
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
        setJsonError('Payload must be a JSON object (e.g. { "key": "value" }).');
      } else {
        setJsonError(null);
      }
    } catch (err) {
      setJsonError('Invalid JSON syntax: ' + err.message);
    }
  };

  const applyPreset = (preset) => {
    setTaskType(preset.type);
    setPayloadText(JSON.stringify(preset.payload, null, 2));
    setPriority(preset.priority);
    setJsonError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError(null);

    // Validate JSON object
    let parsedPayload;
    try {
      parsedPayload = JSON.parse(payloadText);
      if (typeof parsedPayload !== 'object' || parsedPayload === null || Array.isArray(parsedPayload)) {
        setJsonError('Payload must be a JSON object.');
        return;
      }
    } catch (err) {
      setJsonError('Invalid JSON format: ' + err.message);
      return;
    }

    if (!projectId) {
      setApiError('Please select a project.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.submitJob({
        project_id: projectId,
        task_type: taskType.trim(),
        payload: parsedPayload,
        priority: Number(priority),
        status: statusVal,
      });

      setSubmittedJob(res.data);
      if (onJobSubmitted) onJobSubmitted(res.data);
    } catch (err) {
      const details = err.details
        ? Object.entries(err.details)
            .map(([k, v]) => `${k}: ${v}`)
            .join(' | ')
        : '';
      setApiError(`${err.message || 'Job submission failed'} ${details}`);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs">
      <div className="bg-[#12151f] border border-[#232838] rounded-xl max-w-xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#232838] flex items-center justify-between bg-[#151824]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Send className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Submit Background Job</h2>
              <p className="text-xs text-zinc-400">Phase 1: Ingestion & PostgreSQL Persistence</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded-md hover:bg-[#1f2433] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-4">
          {submittedJob ? (
            /* Success Feedback Card */
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-5 space-y-3">
              <div className="flex items-center gap-2.5 text-emerald-400">
                <CheckCircle className="w-5 h-5 shrink-0" />
                <h3 className="text-sm font-semibold">Job Stored Successfully in PostgreSQL</h3>
              </div>
              <p className="text-xs text-zinc-300">
                Your job was assigned a unique UUID and safely persisted. In Phase 1, distributed worker execution is scheduled for Phase 2.
              </p>
              <div className="bg-[#0b0d13] p-3 rounded-lg border border-[#1e2230] font-mono text-xs space-y-1">
                <div>
                  <span className="text-zinc-400">Job ID: </span>
                  <span className="text-indigo-300 select-all font-semibold">{submittedJob.id}</span>
                </div>
                <div>
                  <span className="text-zinc-400">Task Type: </span>
                  <span className="text-zinc-200">{submittedJob.task_type}</span>
                </div>
                <div>
                  <span className="text-zinc-400">Status: </span>
                  <span className="text-amber-400 font-semibold">{submittedJob.status}</span>
                </div>
                <div>
                  <span className="text-zinc-400">Priority: </span>
                  <span className="text-zinc-200">{submittedJob.priority}</span>
                </div>
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    navigate(`/jobs/${submittedJob.id}`);
                  }}
                  className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer"
                >
                  <span>View Job Details</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  onClick={() => setSubmittedJob(null)}
                  className="bg-[#1f2433] hover:bg-[#282f42] text-zinc-300 text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer"
                >
                  Submit Another Job
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Architecture Notice */}
              <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 flex items-start gap-2.5 text-xs text-amber-300">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">Phase 1 Foundation:</span> Acceptance stores the job in PostgreSQL with status PENDING/QUEUED. Worker processing will be implemented in Phase 2.
                </div>
              </div>

              {/* Template Presets */}
              <div>
                <label className="text-xs font-medium text-zinc-400 mb-1.5 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-indigo-400" />
                  <span>Preset Task Templates</span>
                </label>
                <div className="flex flex-wrap gap-2">
                  {PRESET_TEMPLATES.map((tmpl) => (
                    <button
                      key={tmpl.type}
                      type="button"
                      onClick={() => applyPreset(tmpl)}
                      className="px-2.5 py-1 rounded bg-[#1a1f2e] hover:bg-indigo-950/60 border border-[#2b3245] hover:border-indigo-500/50 text-[11px] font-medium text-zinc-300 hover:text-indigo-300 transition-colors cursor-pointer"
                    >
                      {tmpl.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Project Dropdown */}
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Project <span className="text-rose-400">*</span>
                </label>
                <select
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  required
                  className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-indigo-500"
                >
                  {projects.length === 0 && <option value="">No projects available</option>}
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Task Type */}
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Task Type <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value)}
                  placeholder="e.g. invoice.generate"
                  required
                  className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-2 text-sm text-zinc-200 font-mono focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Priority & Status */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between text-xs font-medium text-zinc-300 mb-1">
                    <span>Priority (1 to 10)</span>
                    <span className="font-mono text-indigo-400 font-bold">{priority}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full accent-indigo-500 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-zinc-400 mt-0.5">
                    <span>1 (Low)</span>
                    <span>5 (Default)</span>
                    <span>10 (High)</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-300 mb-1">
                    Initial Status
                  </label>
                  <select
                    value={statusVal}
                    onChange={(e) => setStatusVal(e.target.value)}
                    className="w-full bg-[#0d0f15] border border-[#272d3f] rounded-lg px-3 py-2 text-sm text-zinc-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="PENDING">PENDING (Default)</option>
                    <option value="QUEUED">QUEUED</option>
                  </select>
                </div>
              </div>

              {/* Payload JSON Editor */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-medium text-zinc-300">
                    Task Payload (JSON Object) <span className="text-rose-400">*</span>
                  </label>
                  {jsonError ? (
                    <span className="text-[11px] text-rose-400 font-medium">{jsonError}</span>
                  ) : (
                    <span className="text-[11px] text-emerald-400">Valid JSON Object</span>
                  )}
                </div>
                <textarea
                  rows={6}
                  value={payloadText}
                  onChange={handlePayloadChange}
                  className={`w-full bg-[#0d0f15] border rounded-lg p-3 text-xs font-mono text-zinc-200 focus:outline-none ${
                    jsonError ? 'border-rose-500/60' : 'border-[#272d3f] focus:border-indigo-500'
                  }`}
                  placeholder='{\n  "key": "value"\n}'
                />
              </div>

              {/* API Error Callout */}
              {apiError && (
                <div className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 text-xs text-rose-300">
                  {apiError}
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-xs font-medium text-zinc-400 hover:text-white rounded-lg hover:bg-[#1a1f2e] transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || Boolean(jsonError)}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium px-5 py-2 rounded-lg transition-colors cursor-pointer"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Storing Job...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Submit Job</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
