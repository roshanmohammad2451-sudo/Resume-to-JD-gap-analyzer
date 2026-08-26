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
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Loader2,
  FileCheck,
  XCircle,
  Check,
  Star,
  ListChecks,
  GraduationCap,
  Building2
} from 'lucide-react';

interface PageExtraction {
  page_number: number;
  text: string;
}

interface PDFExtractionResponse {
  pages: PageExtraction[];
  total_pages: number;
  file_name: string;
}

interface JobSkill {
  name: string;
  evidence: string;
  importance: 'required' | 'preferred';
  source_text: string;
}

interface JobDescriptionResponse {
  role?: string;
  company?: string;
  summary?: string;
  required_skills: JobSkill[];
  preferred_skills: JobSkill[];
  responsibilities: string[];
  qualifications: string[];
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export default function App() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'ok' | 'error'>('checking');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<string>('');

  // PDF Extraction state
  const [isExtracting, setIsExtracting] = useState<boolean>(false);
  const [extractionResult, setExtractionResult] = useState<PDFExtractionResponse | null>(null);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState<boolean>(true);

  // JD Analysis state
  const [isAnalyzingJD, setIsAnalyzingJD] = useState<boolean>(false);
  const [jdResult, setJdResult] = useState<JobDescriptionResponse | null>(null);
  const [jdError, setJdError] = useState<string | null>(null);

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

  const handleFileSelect = async (selectedFile: File) => {
    setResumeFile(selectedFile);
    setExtractionError(null);
    setExtractionResult(null);
    setIsExtracting(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/resume/extract', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Failed to parse PDF.' }));
        throw new Error(errData.detail || 'Extraction failed.');
      }

      const data: PDFExtractionResponse = await response.json();
      setExtractionResult(data);
      setIsPreviewOpen(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred while extracting PDF.';
      setExtractionError(message);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleAnalyzeJD = async () => {
    if (!jobDescription.trim()) return;
    setJdError(null);
    setIsAnalyzingJD(true);

    try {
      const response = await fetch('/api/jd/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: jobDescription }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Failed to analyze Job Description.' }));
        throw new Error(errData.detail || 'Analysis failed.');
      }

      const data: JobDescriptionResponse = await response.json();
      setJdResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred while analyzing JD.';
      setJdError(message);
    } finally {
      setIsAnalyzingJD(false);
    }
  };

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
                Phase 4: Structured JD Analysis
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
        <div className="text-center max-w-3xl mx-auto mb-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-cyan-400 text-xs font-medium mb-4">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Structured Job Description Analysis & Requirement Extraction</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
            Structured JD Parsing & <br />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-400 to-blue-500 bg-clip-text text-transparent">
              Grounded Requirement Extraction
            </span>
          </h1>
          <p className="text-slate-400 text-base sm:text-lg leading-relaxed">
            Extract target role, required vs. preferred technical skills, and key job duties with zero hallucination.
          </p>
        </div>

        {/* Input Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Card 1: Resume Upload & Extraction Status */}
          <div className="glass-card-interactive rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-xl bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">1. Candidate Resume</h2>
                    <p className="text-xs text-slate-400">Upload PDF resume for page-by-page text extraction</p>
                  </div>
                </div>
                {extractionResult && (
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    <FileCheck className="w-3.5 h-3.5 mr-1" />
                    Extracted
                  </span>
                )}
              </div>

              {/* Upload Drop Zone */}
              <div className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-xl p-6 text-center transition-colors bg-slate-900/40 relative">
                {isExtracting ? (
                  <div className="py-8 flex flex-col items-center justify-center space-y-3">
                    <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
                    <p className="text-sm font-medium text-slate-300">Extracting PDF text page by page...</p>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center min-h-[160px]">
                    <div className="p-3 rounded-full bg-slate-800/80 text-slate-400 mb-3">
                      <UploadCloud className="w-8 h-8 text-cyan-400" />
                    </div>
                    <p className="text-sm font-medium text-slate-200 mb-1">
                      {resumeFile ? resumeFile.name : 'Click to select or drag PDF resume here'}
                    </p>
                    <p className="text-xs text-slate-500">
                      Supports PDF format only (Max 10MB)
                    </p>
                    <input 
                      type="file" 
                      accept=".pdf" 
                      className="hidden" 
                      id="resume-input"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          handleFileSelect(e.target.files[0]);
                        }
                      }}
                    />
                    <label 
                      htmlFor="resume-input" 
                      className="mt-4 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-semibold text-white transition-colors cursor-pointer shadow-lg shadow-cyan-600/20"
                    >
                      {resumeFile ? 'Change File' : 'Select PDF File'}
                    </label>
                  </div>
                )}
              </div>

              {/* Error Alert Display */}
              {extractionError && (
                <div className="mt-4 p-3 rounded-xl bg-rose-950/80 border border-rose-800 text-rose-300 text-xs flex items-start space-x-2">
                  <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold block mb-0.5">Extraction Error</span>
                    <span>{extractionError}</span>
                  </div>
                </div>
              )}

              {/* Extraction Metadata Banner */}
              {extractionResult && (
                <div className="mt-4 p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-1 w-full sm:w-auto">
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-400">Filename:</span>
                      <span className="font-semibold text-slate-200 truncate max-w-[150px]" title={extractionResult.file_name}>{extractionResult.file_name}</span>
                    </div>
                    {resumeFile && (
                      <div className="flex items-center space-x-2">
                        <span className="text-slate-400">File Size:</span>
                        <span className="font-semibold text-slate-300">{formatFileSize(resumeFile.size)}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-2">
                      <span className="text-slate-400">Pages:</span>
                      <span className="font-semibold text-cyan-400">{extractionResult.total_pages} page(s)</span>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="px-2.5 py-1 rounded-md bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 font-medium inline-flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      Status: Extracted Successfully
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Card 2: Job Description Input & Analysis */}
          <div className="glass-card-interactive rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-xl bg-blue-950/80 text-blue-400 border border-blue-800/50">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">2. Job Description (JD)</h2>
                    <p className="text-xs text-slate-400">Paste target job role and requirement details</p>
                  </div>
                </div>
                {jdResult && (
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                    Analyzed
                  </span>
                )}
              </div>

              {/* JD Textarea */}
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste Job Description here (e.g. Required skills, experience level, responsibilities, technical stack requirements)..."
                className="w-full h-[180px] p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-slate-200 text-sm placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/60 transition-all resize-none font-mono mb-4"
              />

              {/* Analyze JD Trigger Button */}
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleAnalyzeJD}
                  disabled={isAnalyzingJD || !jobDescription.trim()}
                  className={`inline-flex items-center px-4 py-2 rounded-xl text-xs font-semibold shadow-lg transition-all ${
                    !isAnalyzingJD && jobDescription.trim()
                      ? 'bg-blue-600 hover:bg-blue-500 text-white cursor-pointer shadow-blue-600/20'
                      : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                  }`}
                >
                  {isAnalyzingJD ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin text-blue-400" />
                      <span>Analyzing Job Requirements...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-1.5 text-cyan-400" />
                      <span>Analyze JD Requirements</span>
                    </>
                  )}
                </button>
              </div>

              {/* Error Alert Display */}
              {jdError && (
                <div className="mb-4 p-3 rounded-xl bg-rose-950/80 border border-rose-800 text-rose-300 text-xs flex items-start space-x-2">
                  <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold block mb-0.5">JD Analysis Error</span>
                    <span>{jdError}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Structured JD Analysis Result Panel */}
        {jdResult && (
          <div className="mb-8 rounded-2xl bg-slate-900/90 border border-slate-800 p-6 shadow-2xl space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
              <div>
                <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider block mb-1">
                  Structured Job Requirement Profile
                </span>
                <h3 className="text-xl font-bold text-white flex items-center">
                  <Briefcase className="w-5 h-5 mr-2 text-cyan-400" />
                  {jdResult.role || 'Unspecified Role'}
                </h3>
              </div>
              {jdResult.company && (
                <div className="inline-flex items-center px-3 py-1.5 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-300">
                  <Building2 className="w-4 h-4 mr-1.5 text-cyan-400" />
                  <span>{jdResult.company}</span>
                </div>
              )}
            </div>

            {jdResult.summary && (
              <p className="text-xs text-slate-300 leading-relaxed italic bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                "{jdResult.summary}"
              </p>
            )}

            {/* Required vs Preferred Skills Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Required Skills */}
              <div className="rounded-xl bg-slate-950 p-4 border border-cyan-900/40">
                <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-slate-800">
                  <Check className="w-4 h-4 text-cyan-400" />
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">
                    Required Skills ({jdResult.required_skills.length})
                  </h4>
                </div>
                {jdResult.required_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {jdResult.required_skills.map((skill, idx) => (
                      <span 
                        key={idx}
                        title={`Evidence: ${skill.evidence}`}
                        className="px-2.5 py-1 rounded-lg bg-cyan-950/80 text-cyan-300 border border-cyan-800 text-xs font-medium inline-flex items-center"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">No explicit required skills identified.</p>
                )}
              </div>

              {/* Preferred Skills */}
              <div className="rounded-xl bg-slate-950 p-4 border border-purple-900/40">
                <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-slate-800">
                  <Star className="w-4 h-4 text-purple-400" />
                  <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider">
                    Preferred Skills ({jdResult.preferred_skills.length})
                  </h4>
                </div>
                {jdResult.preferred_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {jdResult.preferred_skills.map((skill, idx) => (
                      <span 
                        key={idx}
                        title={`Evidence: ${skill.evidence}`}
                        className="px-2.5 py-1 rounded-lg bg-purple-950/80 text-purple-300 border border-purple-800 text-xs font-medium inline-flex items-center"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">No explicit preferred skills identified.</p>
                )}
              </div>
            </div>

            {/* Responsibilities */}
            {jdResult.responsibilities.length > 0 && (
              <div className="rounded-xl bg-slate-950 p-4 border border-slate-800">
                <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-slate-800">
                  <ListChecks className="w-4 h-4 text-blue-400" />
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Key Responsibilities ({jdResult.responsibilities.length})
                  </h4>
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                  {jdResult.responsibilities.map((resp, idx) => (
                    <li key={idx}>{resp}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Qualifications */}
            {jdResult.qualifications.length > 0 && (
              <div className="rounded-xl bg-slate-950 p-4 border border-slate-800">
                <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-slate-800">
                  <GraduationCap className="w-4 h-4 text-emerald-400" />
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Qualifications & Credentials ({jdResult.qualifications.length})
                  </h4>
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                  {jdResult.qualifications.map((qual, idx) => (
                    <li key={idx}>{qual}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Collapsible Text Preview Component */}
        {extractionResult && (
          <div className="mb-8 rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden shadow-2xl transition-all">
            <button
              onClick={() => setIsPreviewOpen(!isPreviewOpen)}
              className="w-full p-4 bg-slate-900 hover:bg-slate-800/80 flex items-center justify-between transition-colors border-b border-slate-800"
            >
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-cyan-400" />
                <span className="font-semibold text-sm text-slate-200">
                  Extracted Resume Text Preview ({extractionResult.total_pages} page{extractionResult.total_pages > 1 ? 's' : ''})
                </span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-400">
                <span>{isPreviewOpen ? 'Collapse Preview' : 'Expand Preview'}</span>
                {isPreviewOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>

            {isPreviewOpen && (
              <div className="p-6 space-y-6 max-h-[500px] overflow-y-auto">
                {extractionResult.pages.map((page) => (
                  <div key={page.page_number} className="rounded-xl bg-slate-950 border border-slate-800/80 p-4">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-800">
                      <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                        Page {page.page_number}
                      </span>
                      <span className="text-xs text-slate-500">
                        {page.text.length} characters
                      </span>
                    </div>
                    <pre className="whitespace-pre-wrap font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto">
                      {page.text || <span className="italic text-slate-600">No text content found on this page.</span>}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Action Button Section Placeholder */}
        <div className="flex flex-col items-center justify-center space-y-4">
          <button
            disabled={!extractionResult || !jobDescription.trim()}
            className={`group relative inline-flex items-center justify-center px-8 py-4 text-base font-bold rounded-2xl shadow-xl transition-all ${
              extractionResult && jobDescription.trim()
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:shadow-cyan-500/25 cursor-pointer'
                : 'bg-slate-900/80 text-slate-500 border border-slate-800 cursor-not-allowed'
            }`}
          >
            <Sparkles className="w-5 h-5 mr-2 text-cyan-400" />
            <span>Analyze Resume-to-JD Gap</span>
            <ArrowRight className="w-5 h-5 ml-2" />
          </button>
          <p className="text-xs text-slate-500 flex items-center space-x-1">
            <Cpu className="w-3.5 h-3.5 text-cyan-500" />
            <span>Phase 4 complete: Structured JD requirement analysis active. Resume-to-JD Gap Engine coming next.</span>
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 bg-slate-950">
        Resume-to-JD Gap Analyzer &copy; {new Date().getFullYear()} — Built with FastAPI, PyMuPDF, React & TypeScript
      </footer>
    </div>
  );
}
