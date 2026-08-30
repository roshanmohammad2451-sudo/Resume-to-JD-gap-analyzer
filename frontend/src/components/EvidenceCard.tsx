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
    <div className="rounded-xl bg-[#090a0e]/90 border border-white/[0.08] p-3.5 sm:p-4 space-y-3 text-xs">
      {/* Optional Top Explanation / Rationale */}
      {explanation && (
        <div className="p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] text-zinc-300 flex items-start space-x-2.5">
          <Quote className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />
          <p className="text-[11px] leading-relaxed italic text-zinc-300">
            {explanation}
          </p>
        </div>
      )}

      {/* Side-by-side Grounded Evidence Columns */}
      <div className={`grid grid-cols-1 ${compact ? 'gap-2.5' : 'md:grid-cols-2 gap-3'}`}>
        {/* Job Description Evidence Column */}
        <div className="rounded-xl bg-white/[0.02] border border-white/[0.06] p-3 flex flex-col justify-between space-y-2">
          <div className="flex items-center space-x-1.5 pb-1.5 border-b border-white/[0.06] text-[11px] font-medium text-sky-400">
            <Briefcase className="w-3.5 h-3.5" />
            <span className="tracking-tight">Job Description Requirement</span>
          </div>

          {jdWording && (
            <div className="text-[11px] flex items-center gap-1.5 flex-wrap">
              <span className="text-zinc-500 font-medium">Specified:</span>
              <span className="font-mono text-zinc-200 bg-white/[0.06] px-1.5 py-0.5 rounded text-[10px] border border-white/[0.08]">
                "{jdWording}"
              </span>
            </div>
          )}

          <div className="min-h-[2rem]">
            {hasJdEvidence ? (
              <p className="text-[11px] text-zinc-300 leading-relaxed font-sans italic border-l-2 border-sky-500/40 pl-2">
                "{jdEvidence}"
              </p>
            ) : (
              <div className="flex items-center text-[11px] text-zinc-500 italic space-x-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                <span>No specific JD excerpt identified</span>
              </div>
            )}
          </div>
        </div>

        {/* Candidate Resume Evidence Column */}
        <div className="rounded-xl bg-white/[0.02] border border-white/[0.06] p-3 flex flex-col justify-between space-y-2">
          <div className="flex items-center space-x-1.5 pb-1.5 border-b border-white/[0.06] text-[11px] font-medium text-emerald-400">
            <FileText className="w-3.5 h-3.5" />
            <span className="tracking-tight">Candidate Resume Match</span>
          </div>

          {resumeWording && (
            <div className="text-[11px] flex items-center gap-1.5 flex-wrap">
              <span className="text-zinc-500 font-medium">Resume:</span>
              <span className="font-mono text-zinc-200 bg-white/[0.06] px-1.5 py-0.5 rounded text-[10px] border border-white/[0.08]">
                "{resumeWording}"
              </span>
            </div>
          )}

          <div className="min-h-[2rem]">
            {hasResumeEvidence ? (
              <p className="text-[11px] text-zinc-300 leading-relaxed font-sans italic border-l-2 border-emerald-500/40 pl-2">
                "{resumeEvidence}"
              </p>
            ) : (
              <div className="flex items-center text-[11px] text-rose-400/90 italic space-x-1.5 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
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

