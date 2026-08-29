import React from 'react';
import { Briefcase, FileText, AlertCircle, Quote } from 'lucide-react';

interface EvidenceCardProps {
  jdEvidence?: string | null;
  resumeEvidence?: string | null;
  jdWording?: string | null;
  resumeWording?: string | null;
  explanation?: string | null;
  compact?: boolean;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  jdEvidence,
  resumeEvidence,
  jdWording,
  resumeWording,
  explanation,
  compact = false,
}) => {
  const hasJdEvidence = Boolean(jdEvidence && jdEvidence.trim());
  const hasResumeEvidence = Boolean(resumeEvidence && resumeEvidence.trim());

  return (
    <div className="rounded-xl bg-slate-950/70 border border-slate-800/80 p-3.5 sm:p-4 space-y-3 text-xs">
      {/* Optional Top Explanation / Rationale */}
      {explanation && (
        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800/80 text-slate-300 flex items-start space-x-2">
          <Quote className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
          <p className="text-[11px] leading-relaxed italic text-slate-300">
            {explanation}
          </p>
        </div>
      )}

      {/* Side-by-side Grounded Evidence Columns */}
      <div className={`grid grid-cols-1 ${compact ? 'gap-2.5' : 'md:grid-cols-2 gap-3.5'}`}>
        {/* Job Description Evidence Column */}
        <div className="rounded-lg bg-slate-900/90 border border-slate-800 p-3 flex flex-col justify-between space-y-2">
          <div className="flex items-center space-x-1.5 pb-1.5 border-b border-slate-800 text-[11px] font-semibold text-blue-400">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Job Description Evidence</span>
          </div>

          {jdWording && (
            <div className="text-[11px]">
              <span className="text-slate-500 font-medium mr-1">Specified Wording:</span>
              <span className="font-mono text-slate-200 bg-slate-800/80 px-1.5 py-0.5 rounded">
                "{jdWording}"
              </span>
            </div>
          )}

          <div className="min-h-[2rem]">
            {hasJdEvidence ? (
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans italic border-l-2 border-blue-500/40 pl-2">
                "{jdEvidence}"
              </p>
            ) : (
              <div className="flex items-center text-[11px] text-slate-500 italic space-x-1">
                <AlertCircle className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                <span>No specific JD excerpt found</span>
              </div>
            )}
          </div>
        </div>

        {/* Candidate Resume Evidence Column */}
        <div className="rounded-lg bg-slate-900/90 border border-slate-800 p-3 flex flex-col justify-between space-y-2">
          <div className="flex items-center space-x-1.5 pb-1.5 border-b border-slate-800 text-[11px] font-semibold text-cyan-400">
            <FileText className="w-3.5 h-3.5" />
            <span>Candidate Resume Evidence</span>
          </div>

          {resumeWording && (
            <div className="text-[11px]">
              <span className="text-slate-500 font-medium mr-1">Resume Phrase:</span>
              <span className="font-mono text-slate-200 bg-slate-800/80 px-1.5 py-0.5 rounded">
                "{resumeWording}"
              </span>
            </div>
          )}

          <div className="min-h-[2rem]">
            {hasResumeEvidence ? (
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans italic border-l-2 border-cyan-500/40 pl-2">
                "{resumeEvidence}"
              </p>
            ) : (
              <div className="flex items-center text-[11px] text-rose-400/80 italic space-x-1.5 bg-rose-950/30 p-1.5 rounded border border-rose-900/30">
                <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                <span>No supporting evidence found in candidate resume</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
