import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { SubmitJobModal } from './components/SubmitJobModal';
import { DashboardPage } from './pages/DashboardPage';
import { JobsPage } from './pages/JobsPage';
import { JobDetailPage } from './pages/JobDetailPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { SettingsPage } from './pages/SettingsPage';

export default function App() {
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-[#090a0f] text-zinc-100 antialiased font-sans">
        {/* Navigation Sidebar */}
        <Sidebar onOpenSubmitModal={() => setIsSubmitModalOpen(true)} />

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {/* Top Bar */}
          <header className="h-14 border-b border-[#1e2230] bg-[#0c0e14]/80 backdrop-blur-xs px-8 flex items-center justify-between sticky top-0 z-30">
            <div className="flex items-center gap-3">
              <span className="text-xs font-medium text-zinc-400">Environment:</span>
              <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium">
                Development (PostgreSQL)
              </span>
            </div>

            <div className="flex items-center gap-4 text-xs text-zinc-400">
              <span className="hidden sm:inline">
                API Base: <code className="text-indigo-400 font-mono text-[11px]">/api/v1/</code>
              </span>
              <a
                href="http://127.0.0.1:8000/api/docs/"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline"
              >
                Swagger Docs
              </a>
            </div>
          </header>

          {/* Page Routing */}
          <div className="p-8 flex-1">
            <Routes>
              <Route
                path="/"
                element={<DashboardPage onOpenSubmitModal={() => setIsSubmitModalOpen(true)} />}
              />
              <Route
                path="/jobs"
                element={<JobsPage onOpenSubmitModal={() => setIsSubmitModalOpen(true)} />}
              />
              <Route path="/jobs/:jobId" element={<JobDetailPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>

        {/* Global Submit Job Modal */}
        <SubmitJobModal
          isOpen={isSubmitModalOpen}
          onClose={() => setIsSubmitModalOpen(false)}
          onJobSubmitted={() => {
            // Trigger refresh or notification if needed
          }}
        />
      </div>
    </BrowserRouter>
  );
}
