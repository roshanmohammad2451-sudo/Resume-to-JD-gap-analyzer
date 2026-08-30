import { useState, useEffect } from 'react';
import { 
  FileText, 
  Briefcase, 
  Sparkles, 
  CheckCircle2, 
  ShieldCheck, 
  Target, 
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Loader2,
  FileCheck,
  XCircle,
  Check,
  Star,
  Building2
} from 'lucide-react';
import { 
  PDFExtractionResponse, 
  ResumeProfile, 
  JobDescriptionResponse, 
  GapAnalysisResponse 
} from './types/gap';
import { GapDashboard } from './components/GapDashboard';
import { PDFDropzone } from './components/PDFDropzone';
import { getApiUrl } from './config/api';

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

  // Resume Profile state
  const [resumeProfile, setResumeProfile] = useState<ResumeProfile | null>(null);

  // JD Analysis & Input Mode state
  const [jdInputMode, setJdInputMode] = useState<'paste' | 'upload'>('paste');
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [isExtractingJD, setIsExtractingJD] = useState<boolean>(false);
  const [jdExtractionResult, setJdExtractionResult] = useState<PDFExtractionResponse | null>(null);
  const [jdExtractionError, setJdExtractionError] = useState<string | null>(null);
  const [isJdPreviewOpen, setIsJdPreviewOpen] = useState<boolean>(false);
  const [isAnalyzingJD, setIsAnalyzingJD] = useState<boolean>(false);
  const [jdResult, setJdResult] = useState<JobDescriptionResponse | null>(null);
  const [jdError, setJdError] = useState<string | null>(null);

  // Gap Analysis state
  const [isAnalyzingGap, setIsAnalyzingGap] = useState<boolean>(false);
  const [gapResult, setGapResult] = useState<GapAnalysisResponse | null>(null);
  const [gapError, setGapError] = useState<string | null>(null);

  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const response = await fetch(getApiUrl('/api/health'));
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
    // Validate file format
    if (!selectedFile.name.toLowerCase().endsWith('.pdf') && selectedFile.type !== 'application/pdf') {
      setExtractionError('Unsupported file format. Only PDF files (.pdf) are accepted.');
      return;
    }

    // Validate size limit (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setExtractionError('File size exceeds maximum limit of 10MB.');
      return;
    }

    setResumeFile(selectedFile);
    setExtractionError(null);
    setExtractionResult(null);
    setResumeProfile(null);
    setGapResult(null);
    setGapError(null);
    setIsExtracting(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(getApiUrl('/api/resume/extract'), {
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

  const handleJdFileSelect = async (selectedFile: File) => {
    // Validate file format
    if (!selectedFile.name.toLowerCase().endsWith('.pdf') && selectedFile.type !== 'application/pdf') {
      setJdExtractionError('Unsupported file format. Only PDF files (.pdf) are accepted.');
      return;
    }

    // Validate size limit (10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setJdExtractionError('File size exceeds maximum limit of 10MB.');
      return;
    }

    setJdFile(selectedFile);
    setJdExtractionError(null);
    setJdExtractionResult(null);
    setJdResult(null);
    setGapResult(null);
    setGapError(null);
    setIsExtractingJD(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(getApiUrl('/api/jd/extract'), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Failed to extract text from JD PDF.' }));
        throw new Error(errData.detail || 'JD PDF extraction failed.');
      }

      const data: PDFExtractionResponse = await response.json();
      setJdExtractionResult(data);
      const combinedText = data.pages.map((p) => p.text).join('\n\n').trim();
      setJobDescription(combinedText);
      setIsJdPreviewOpen(true);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An error occurred while extracting JD PDF.';
      setJdExtractionError(message);
    } finally {
      setIsExtractingJD(false);
    }
  };

  const handleClearJdFile = () => {
    setJdFile(null);
    setJdExtractionResult(null);
    setJdExtractionError(null);
    setJobDescription('');
    setJdResult(null);
    setGapResult(null);
    setGapError(null);
  };

  const handleAnalyzeJD = async () => {
    if (!jobDescription.trim()) return;
    setJdError(null);
    setGapResult(null);
    setGapError(null);
    setIsAnalyzingJD(true);

    try {
      const response = await fetch(getApiUrl('/api/jd/analyze'), {
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

  const handleAnalyzeGap = async () => {
    if (!extractionResult || extractionResult.pages.length === 0) {
      setGapError('Please select and extract a candidate PDF resume first.');
      return;
    }
    if (!jobDescription.trim()) {
      setGapError('Please enter a target Job Description.');
      return;
    }

    setGapError(null);
    setIsAnalyzingGap(true);

    try {
      // 1. Ensure structured ResumeProfile exists
      let currentResumeProfile = resumeProfile;
      if (!currentResumeProfile) {
        const fullResumeText = extractionResult.pages.map(p => p.text).join('\n');
        const resumeRes = await fetch(getApiUrl('/api/resume/analyze'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: fullResumeText }),
        });

        if (!resumeRes.ok) {
          const errData = await resumeRes.json().catch(() => ({ detail: 'Failed to analyze candidate resume text.' }));
          throw new Error(errData.detail || 'Resume analysis failed.');
        }

        currentResumeProfile = await resumeRes.json();
        setResumeProfile(currentResumeProfile);
      }

      // 2. Ensure structured JobDescription exists
      let currentJdResult = jdResult;
      if (!currentJdResult) {
        const jdRes = await fetch(getApiUrl('/api/jd/analyze'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: jobDescription }),
        });

        if (!jdRes.ok) {
          const errData = await jdRes.json().catch(() => ({ detail: 'Failed to analyze Job Description requirements.' }));
          throw new Error(errData.detail || 'JD requirement analysis failed.');
        }

        currentJdResult = await jdRes.json();
        setJdResult(currentJdResult);
      }

      // 3. Perform Deterministic Gap Analysis
      const gapRes = await fetch(getApiUrl('/api/gap/analyze'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_profile: currentResumeProfile,
          job_description: currentJdResult,
        }),
      });

      if (!gapRes.ok) {
        const errData = await gapRes.json().catch(() => ({ detail: 'Failed to complete gap analysis.' }));
        throw new Error(errData.detail || 'Gap analysis failed.');
      }

      const gapData: GapAnalysisResponse = await gapRes.json();
      setGapResult(gapData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'An unexpected error occurred during gap analysis.';
      setGapError(message);
    } finally {
      setIsAnalyzingGap(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070709] text-zinc-100 flex flex-col relative selection:bg-rose-500/20 selection:text-white">
      {/* Raycast Ambient Background Radial Glow */}
      <div className="raycast-glow-top" />

      {/* Top Navbar */}
      <header className="border-b border-white/[0.08] bg-[#08080a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-[#ff6363] to-[#ff3b30] flex items-center justify-center shadow-lg shadow-rose-500/20 border border-white/20">
              <Target className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-tight text-white">
                  Resume-to-JD Gap Analyzer
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.06] text-zinc-300 border border-white/[0.08] font-mono font-medium">
                  Phase 7 • RAG Engine
                </span>
              </div>
            </div>
          </div>

          {/* Backend Connection Indicator */}
          <div className="flex items-center space-x-2 text-xs font-medium">
            <span className="text-zinc-500 hidden sm:inline">Backend Status:</span>
            {healthStatus === 'checking' && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20 gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping"></span>
                Connecting...
              </span>
            )}
            {healthStatus === 'ok' && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                API Online (/api/health)
              </span>
            )}
            {healthStatus === 'error' && (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20 gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                API Offline
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col justify-center relative z-10">
        {/* Hero Banner */}
        <div className="text-center max-w-3xl mx-auto mb-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-zinc-300 text-xs font-medium mb-4 shadow-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Deterministic & Explainable Gap Analysis Engine</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-white mb-4">
            Resume-to-JD Gap Analysis & <br />
            <span className="bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
              Explainable Match Evaluation
            </span>
          </h1>
          <p className="text-zinc-400 text-base sm:text-lg leading-relaxed">
            Rule-based skill normalization, weighted requirement scoring, and grounded gap verification without non-deterministic AI variance.
          </p>
        </div>

        {/* Input Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Card 1: Resume Upload & Extraction Status */}
          <div className="raycast-card rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-zinc-300 shadow-inner">
                    <FileText className="w-5 h-5 text-sky-400" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-white tracking-tight">1. Candidate Resume</h2>
                    <p className="text-xs text-zinc-400">Upload PDF resume for page-by-page text extraction</p>
                  </div>
                </div>
                {extractionResult && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 gap-1">
                    <FileCheck className="w-3.5 h-3.5" />
                    Extracted
                  </span>
                )}
              </div>

              {/* Upload Drop Zone */}
              <PDFDropzone
                id="resume-dropzone"
                label="Click to select or drag & drop candidate PDF resume here"
                sublabel="Supports PDF format only (Max 10MB)"
                currentFile={resumeFile}
                isLoading={isExtracting}
                loadingText="Extracting PDF text page by page..."
                onFileSelected={handleFileSelect}
                onError={(err) => setExtractionError(err)}
                onClear={() => {
                  setResumeFile(null);
                  setExtractionResult(null);
                  setExtractionError(null);
                  setResumeProfile(null);
                  setGapResult(null);
                  setGapError(null);
                }}
                accentColor="cyan"
              />

              {/* Error Alert Display */}
              {extractionError && (
                <div className="mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start space-x-2">
                  <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold block mb-0.5">Extraction Error</span>
                    <span>{extractionError}</span>
                  </div>
                </div>
              )}

              {/* Extraction Metadata Banner */}
              {extractionResult && (
                <div className="mt-4 p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-1 w-full sm:w-auto">
                    <div className="flex items-center space-x-2">
                      <span className="text-zinc-500">Filename:</span>
                      <span className="font-medium text-zinc-200 truncate max-w-[150px]" title={extractionResult.file_name}>{extractionResult.file_name}</span>
                    </div>
                    {resumeFile && (
                      <div className="flex items-center space-x-2">
                        <span className="text-zinc-500">Size:</span>
                        <span className="font-mono text-zinc-300">{formatFileSize(resumeFile.size)}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-2">
                      <span className="text-zinc-500">Pages:</span>
                      <span className="font-mono text-sky-400">{extractionResult.total_pages} page(s)</span>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium inline-flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      Extracted Successfully
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Card 2: Job Description Input & Analysis */}
          <div className="raycast-card rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-zinc-300 shadow-inner">
                    <Briefcase className="w-5 h-5 text-indigo-400" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-white tracking-tight">2. Job Description (JD)</h2>
                    <p className="text-xs text-zinc-400">Paste target job role and requirement details</p>
                  </div>
                </div>
                {jdResult && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Analyzed
                  </span>
                )}
              </div>

              {/* JD Input Mode Selector */}
              <div className="flex items-center space-x-1 mb-3 bg-black/40 p-1 rounded-xl border border-white/[0.08] w-fit">
                <button
                  type="button"
                  onClick={() => setJdInputMode('paste')}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                    jdInputMode === 'paste'
                      ? 'bg-white/[0.14] text-white shadow-sm border border-white/[0.12]'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  Paste Text
                </button>
                <button
                  type="button"
                  onClick={() => setJdInputMode('upload')}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                    jdInputMode === 'upload'
                      ? 'bg-white/[0.14] text-white shadow-sm border border-white/[0.12]'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  Upload PDF
                </button>
              </div>

              {jdInputMode === 'paste' ? (
                /* JD Textarea */
                <textarea
                  value={jobDescription}
                  onChange={(e) => {
                    setJobDescription(e.target.value);
                    setJdResult(null);
                    setGapResult(null);
                    setGapError(null);
                  }}
                  placeholder="Paste Job Description here (e.g. Required skills, experience level, responsibilities, technical stack requirements)..."
                  className="w-full h-[180px] p-4 rounded-xl bg-black/40 border border-white/[0.08] text-zinc-200 text-xs placeholder:text-zinc-600 focus:outline-none focus:border-white/[0.25] focus:ring-1 focus:ring-white/[0.25] transition-all resize-none font-mono mb-4"
                />
              ) : (
                /* JD PDF Dropzone & Extracted Info */
                <div className="mb-4 space-y-3">
                  <PDFDropzone
                    id="jd-dropzone"
                    label="Click to select or drag & drop Job Description PDF here"
                    sublabel="Supports PDF format only (Max 10MB)"
                    currentFile={jdFile}
                    isLoading={isExtractingJD}
                    loadingText="Extracting Job Description PDF text page by page..."
                    onFileSelected={handleJdFileSelect}
                    onError={(err) => setJdExtractionError(err)}
                    onClear={handleClearJdFile}
                    accentColor="blue"
                  />

                  {/* JD Extraction Error Alert */}
                  {jdExtractionError && (
                    <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start space-x-2">
                      <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold block mb-0.5">JD Extraction Error</span>
                        <span>{jdExtractionError}</span>
                      </div>
                    </div>
                  )}

                  {/* JD Extraction Metadata Banner */}
                  {jdExtractionResult && (
                    <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 text-xs">
                      <div className="flex flex-wrap items-center gap-3">
                        <div>
                          <span className="text-zinc-500">Filename: </span>
                          <span className="font-medium text-zinc-200 truncate max-w-[140px]" title={jdExtractionResult.file_name}>
                            {jdExtractionResult.file_name}
                          </span>
                        </div>
                        <div>
                          <span className="text-zinc-500">Pages: </span>
                          <span className="font-mono text-sky-400">{jdExtractionResult.total_pages} page(s)</span>
                        </div>
                        {jdFile && (
                          <div>
                            <span className="text-zinc-500">Size: </span>
                            <span className="font-mono text-zinc-300">{formatFileSize(jdFile.size)}</span>
                          </div>
                        )}
                      </div>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-medium inline-flex items-center shrink-0 gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Extracted Successfully
                      </span>
                    </div>
                  )}

                  {/* Optional View / Edit Extracted Text */}
                  {jobDescription && (
                    <div className="rounded-xl bg-white/[0.02] border border-white/[0.06] overflow-hidden">
                      <button
                        type="button"
                        onClick={() => setIsJdPreviewOpen(!isJdPreviewOpen)}
                        className="w-full px-3.5 py-2 flex items-center justify-between text-xs text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04] transition-colors cursor-pointer"
                      >
                        <span className="font-medium">
                          {isJdPreviewOpen ? 'Hide Extracted JD Text' : 'View / Edit Extracted JD Text'} ({jobDescription.length} characters)
                        </span>
                        {isJdPreviewOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>
                      {isJdPreviewOpen && (
                        <div className="p-3 border-t border-white/[0.06]">
                          <textarea
                            value={jobDescription}
                            onChange={(e) => {
                              setJobDescription(e.target.value);
                              setJdResult(null);
                              setGapResult(null);
                              setGapError(null);
                            }}
                            placeholder="Extracted Job Description text..."
                            className="w-full h-[130px] p-3 rounded-lg bg-black/50 border border-white/[0.08] text-zinc-200 text-xs font-mono resize-none focus:outline-none focus:border-white/20"
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Analyze JD Trigger Button */}
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleAnalyzeJD}
                  disabled={isAnalyzingJD || !jobDescription.trim()}
                  className={`inline-flex items-center px-4 py-2 rounded-xl text-xs font-semibold shadow-sm transition-all cursor-pointer ${
                    !isAnalyzingJD && jobDescription.trim()
                      ? 'bg-white text-black hover:bg-zinc-200 shadow-md hover:scale-[1.02]'
                      : 'bg-white/[0.04] text-zinc-600 cursor-not-allowed border border-white/[0.06]'
                  }`}
                >
                  {isAnalyzingJD ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin text-zinc-600" />
                      <span>Analyzing Job Requirements...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-1.5 text-rose-500" />
                      <span>Analyze JD Requirements</span>
                    </>
                  )}
                </button>
              </div>

              {/* Error Alert Display */}
              {jdError && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start space-x-2">
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
          <div className="mb-8 rounded-2xl bg-[#0c0d12]/95 border border-white/[0.08] p-6 shadow-raycast-card space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/[0.08] gap-3">
              <div>
                <span className="text-[11px] font-mono font-medium text-sky-400 uppercase tracking-wider block mb-1">
                  Structured Job Requirement Profile
                </span>
                <h3 className="text-xl font-bold text-white flex items-center tracking-tight">
                  <Briefcase className="w-5 h-5 mr-2 text-zinc-400" />
                  {jdResult.role || 'Unspecified Role'}
                </h3>
              </div>
              {jdResult.company && (
                <div className="inline-flex items-center px-3 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-xs text-zinc-300 font-medium">
                  <Building2 className="w-4 h-4 mr-1.5 text-zinc-400" />
                  <span>{jdResult.company}</span>
                </div>
              )}
            </div>

            {jdResult.summary && (
              <p className="text-xs text-zinc-300 leading-relaxed italic bg-white/[0.02] p-3.5 rounded-xl border border-white/[0.06]">
                "{jdResult.summary}"
              </p>
            )}

            {/* Required vs Preferred Skills Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Required Skills */}
              <div className="rounded-xl bg-black/40 p-4 border border-rose-500/20">
                <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-white/[0.06]">
                  <Check className="w-4 h-4 text-rose-400" />
                  <h4 className="text-xs font-semibold text-rose-300 uppercase tracking-wider">
                    Required Skills ({jdResult.required_skills.length})
                  </h4>
                </div>
                {jdResult.required_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {jdResult.required_skills.map((skill, idx) => (
                      <span 
                        key={idx}
                        title={`Evidence: ${skill.evidence}`}
                        className="px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-300 border border-rose-500/20 text-xs font-medium inline-flex items-center"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">No explicit required skills identified.</p>
                )}
              </div>

              {/* Preferred Skills */}
              <div className="rounded-xl bg-black/40 p-4 border border-purple-500/20">
                <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-white/[0.06]">
                  <Star className="w-4 h-4 text-purple-400" />
                  <h4 className="text-xs font-semibold text-purple-300 uppercase tracking-wider">
                    Preferred Skills ({jdResult.preferred_skills.length})
                  </h4>
                </div>
                {jdResult.preferred_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {jdResult.preferred_skills.map((skill, idx) => (
                      <span 
                        key={idx}
                        title={`Evidence: ${skill.evidence}`}
                        className="px-2.5 py-1 rounded-lg bg-purple-500/10 text-purple-300 border border-purple-500/20 text-xs font-medium inline-flex items-center"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">No explicit preferred skills identified.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Action Button & Main Trigger Section */}
        <div className="flex flex-col items-center justify-center space-y-4 mb-8">
          {gapError && (
            <div className="w-full max-w-2xl p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-start space-x-3">
              <XCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-sm block mb-1">Gap Analysis Error</span>
                <span>{gapError}</span>
              </div>
            </div>
          )}

          <button
            onClick={handleAnalyzeGap}
            disabled={isAnalyzingGap || !extractionResult || !jobDescription.trim()}
            className={`group relative inline-flex items-center justify-center px-8 py-4 text-base font-bold rounded-2xl shadow-xl transition-all ${
              !isAnalyzingGap && extractionResult && jobDescription.trim()
                ? 'bg-gradient-to-r from-[#ff6363] via-[#ff4b4b] to-[#ff3b30] text-white shadow-raycast-btn hover:shadow-[0_0_35px_rgba(255,99,99,0.5)] cursor-pointer hover:scale-[1.01]'
                : 'bg-white/[0.04] text-zinc-600 border border-white/[0.08] cursor-not-allowed'
            }`}
          >
            {isAnalyzingGap ? (
              <>
                <Loader2 className="w-5 h-5 mr-3 animate-spin text-white" />
                <span>Running Deterministic Gap Engine...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2 text-white" />
                <span>Analyze Resume-to-JD Gap</span>
                <ArrowRight className="w-5 h-5 ml-2 transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>
          <p className="text-xs text-zinc-500 flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Deterministic matching engine active: zero LLM variance in gap decisions & scoring.</span>
          </p>
        </div>

        {/* Phase 6 Polished Gap Analysis Results Dashboard */}
        {gapResult && (
          <div className="mb-12">
            <GapDashboard
              gapResult={gapResult}
              onRetry={handleAnalyzeGap}
              isReanalyzing={isAnalyzingGap}
            />
          </div>
        )}

        {/* Collapsible Text Preview Component */}
        {extractionResult && (
          <div className="mb-8 rounded-2xl bg-[#0c0d12]/95 border border-white/[0.08] overflow-hidden shadow-raycast-card transition-all">
            <button
              onClick={() => setIsPreviewOpen(!isPreviewOpen)}
              className="w-full p-4 bg-white/[0.02] hover:bg-white/[0.04] flex items-center justify-between transition-colors border-b border-white/[0.08] cursor-pointer"
            >
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-sky-400" />
                <span className="font-semibold text-sm text-zinc-200">
                  Extracted Resume Text Preview ({extractionResult.total_pages} page{extractionResult.total_pages > 1 ? 's' : ''})
                </span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-zinc-400">
                <span>{isPreviewOpen ? 'Collapse Preview' : 'Expand Preview'}</span>
                {isPreviewOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </button>

            {isPreviewOpen && (
              <div className="p-6 space-y-6 max-h-[500px] overflow-y-auto">
                {extractionResult.pages.map((page) => (
                  <div key={page.page_number} className="rounded-xl bg-black/40 border border-white/[0.06] p-4">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-white/[0.06]">
                      <span className="text-xs font-mono font-medium text-sky-400 uppercase tracking-wider">
                        Page {page.page_number}
                      </span>
                      <span className="text-xs font-mono text-zinc-500">
                        {page.text.length} characters
                      </span>
                    </div>
                    <pre className="whitespace-pre-wrap font-mono text-xs text-zinc-300 leading-relaxed overflow-x-auto">
                      {page.text || <span className="italic text-zinc-600">No text content found on this page.</span>}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.08] py-6 text-center text-xs text-zinc-500 bg-[#08080a]">
        Resume-to-JD Gap Analyzer &copy; {new Date().getFullYear()} — Built with FastAPI, PyMuPDF, React & TypeScript
      </footer>
    </div>
  );
}

