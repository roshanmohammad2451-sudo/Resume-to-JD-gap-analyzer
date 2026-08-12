import { useState, useEffect } from 'react';
import { 
  FileText, 
  Briefcase, 
  Sparkles, 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Cpu, 
  Target, 
  ArrowRight
} from 'lucide-react';

export default function App() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'ok' | 'error'>('checking');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');

  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'ok') {
            setHealthStatus('ok');
          } else {
            setHealthStatus('error');
          }
        } else {
          setHealthStatus('error');
        }
      } catch (err) {
        console.error('Health check failed:', err);
        setHealthStatus('error');
      }
    };

    checkBackendHealth();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-white">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Target className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Resume-to-JD Gap Analyzer
              </span>
              <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-medium">
                v1.0 Baseline
              </span>
            </div>
          </div>

          {/* Backend Connection Indicator */}
          <div className="flex items-center space-x-2 text-sm font-medium">
            <span className="text-slate-400 text-xs hidden sm:inline">Backend Status:</span>
            {healthStatus === 'checking' && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-950/60 text-amber-400 border border-amber-800/50">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping mr-1.5"></span>
                Connecting...
              </span>
            )}
            {healthStatus === 'ok' && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/50">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" />
                API Online (/api/health)
              </span>
            )}
            {healthStatus === 'error' && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-950/60 text-rose-400 border border-rose-800/50">
                <AlertCircle className="w-3.5 h-3.5 mr-1 text-rose-400" />
                API Offline
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col justify-center">
        {/* Hero Banner */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-cyan-400 text-xs font-medium mb-4">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Deterministic Skill Matching & Grounded AI Recommendations</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
            AI-Powered Resume-to-JD <br />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-400 to-blue-500 bg-clip-text text-transparent">
              Gap Analysis Engine
            </span>
          </h1>
          <p className="text-slate-400 text-base sm:text-lg leading-relaxed">
            Upload candidate resumes and job descriptions to receive rigorous, deterministic skill gap breakdowns and verified learning recommendations.
          </p>
        </div>

        {/* Input Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Card 1: Resume Upload Placeholder */}
          <div className="glass-card-interactive rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2.5 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-white">1. Candidate Resume</h2>
                  <p className="text-xs text-slate-400">Upload PDF resume for structured skill extraction</p>
                </div>
              </div>

              {/* Upload Drop Zone Placeholder */}
              <div className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-xl p-8 text-center transition-colors bg-slate-900/40 cursor-pointer flex flex-col items-center justify-center min-h-[200px]">
                <div className="p-3 rounded-full bg-slate-800/80 text-slate-400 mb-3">
                  <UploadCloud className="w-8 h-8 text-cyan-400" />
                </div>
                <p className="text-sm font-medium text-slate-200 mb-1">
                  {resumeFile ? resumeFile.name : 'Click to select or drag PDF resume here'}
                </p>
                <p className="text-xs text-slate-500">
                  Supports PDF format (Max 10MB)
                </p>
                <input 
                  type="file" 
                  accept=".pdf" 
                  className="hidden" 
                  id="resume-input"
                  onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                />
                <label 
                  htmlFor="resume-input" 
                  className="mt-4 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors cursor-pointer"
                >
                  Browse File
                </label>
              </div>
            </div>
          </div>

          {/* Card 2: Job Description Input Placeholder */}
          <div className="glass-card-interactive rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2.5 rounded-xl bg-blue-950/80 text-blue-400 border border-blue-800/50">
                  <Briefcase className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-white">2. Job Description (JD)</h2>
                  <p className="text-xs text-slate-400">Paste target job role and requirement details</p>
                </div>
              </div>

              {/* JD Textarea Placeholder */}
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste Job Description here (e.g. Required skills, experience level, responsibilities, technical stack requirements)..."
                className="w-full h-[200px] p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-200 text-sm placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/60 transition-all resize-none font-mono"
              />
            </div>
          </div>
        </div>

        {/* Action Button Section Placeholder */}
        <div className="flex flex-col items-center justify-center space-y-4">
          <button
            disabled={true}
            className="group relative inline-flex items-center justify-center px-8 py-4 text-base font-bold text-slate-400 bg-slate-900/80 border border-slate-800 rounded-2xl shadow-xl transition-all opacity-80 cursor-not-allowed"
          >
            <Sparkles className="w-5 h-5 mr-2 text-cyan-400" />
            <span>Analyze Resume-to-JD Gap</span>
            <ArrowRight className="w-5 h-5 ml-2 text-slate-500" />
          </button>
          <p className="text-xs text-slate-500 flex items-center space-x-1">
            <Cpu className="w-3.5 h-3.5 text-cyan-500" />
            <span>Analysis engine placeholder ready (PDF parsing & deterministic gap pipeline coming in Phase 2)</span>
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 bg-slate-950">
        Resume-to-JD Gap Analyzer &copy; {new Date().getFullYear()} — Built with FastAPI, React, TypeScript & Tailwind CSS
      </footer>
    </div>
  );
}
