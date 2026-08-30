import React, { useState } from 'react';
import { 
  GraduationCap, 
  ChevronDown, 
  ChevronUp, 
  Award,
  AlertCircle
} from 'lucide-react';
import { QualificationGapItem } from '../types/gap';

interface QualificationAlignmentProps {
  items: QualificationGapItem[];
}

export const QualificationAlignment: React.FC<QualificationAlignmentProps> = ({ items }) => {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  const matchedCount = items.filter(i => i.status === 'matched').length;
  const partialCount = items.filter(i => i.status === 'partial').length;
  const missingCount = items.filter(i => i.status === 'missing').length;

  const getStatusBadge = (status: 'matched' | 'partial' | 'missing') => {
    switch (status) {
      case 'matched':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Verified
          </span>
        );
      case 'partial':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium uppercase bg-amber-500/10 text-amber-300 border border-amber-500/20 inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            Partial
          </span>
        );
      case 'missing':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium uppercase bg-rose-500/15 text-rose-300 border border-rose-500/30 inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
            Unverified
          </span>
        );
    }
  };

  return (
    <div className="rounded-2xl bg-[#0c0d12]/90 border border-white/[0.08] shadow-raycast-card overflow-hidden">
      {/* Header */}
      <div 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer bg-white/[0.02] hover:bg-white/[0.04] transition-colors border-b border-white/[0.08] select-none"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-white/[0.04] text-emerald-400 border border-white/[0.08] shadow-inner">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-semibold text-white tracking-tight">
                Qualifications & Education Alignment
              </h3>
              <span className="text-xs px-2 py-0.2 rounded-full bg-white/[0.06] text-zinc-400 font-mono">
                {items.length}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Verified education, degrees, and certifications matching role qualifications
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Status counts */}
          <div className="flex items-center space-x-1.5 text-[11px]">
            {matchedCount > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                {matchedCount} Verified
              </span>
            )}
            {partialCount > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
                {partialCount} Partial
              </span>
            )}
            {missingCount > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-300 border border-rose-500/20 font-medium">
                {missingCount} Unverified
              </span>
            )}
          </div>

          <button
            type="button"
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08] transition-colors"
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="p-5 space-y-4">
          {items.length === 0 ? (
            <div className="p-8 text-center rounded-xl bg-white/[0.02] border border-dashed border-white/[0.08]">
              <p className="text-xs text-zinc-400 italic">
                No specific educational or certification requirements were listed in the Job Description.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((item, idx) => (
                <div 
                  key={idx}
                  className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.14] transition-all space-y-3"
                >
                  {/* Top line: Qualification requirement + status */}
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2.5">
                    <div className="flex items-start space-x-2.5">
                      <Award className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="text-xs font-semibold text-zinc-200 block leading-snug">
                          {item.requirement}
                        </span>
                        {item.details && (
                          <p className="text-[11px] text-zinc-400 italic mt-0.5">
                            {item.details}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="shrink-0 self-start">
                      {getStatusBadge(item.status)}
                    </div>
                  </div>

                  {/* Grounded Evidence Box */}
                  <div className="p-3 rounded-lg bg-[#08090d]/80 border border-white/[0.06] flex items-start space-x-2.5">
                    <GraduationCap className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />
                    <div className="text-xs w-full">
                      <span className="text-[10px] uppercase font-mono font-medium text-zinc-500 block mb-0.5">
                        Candidate Education & Certification Evidence
                      </span>
                      {item.resume_evidence ? (
                        <p className="text-[11px] text-zinc-300 leading-relaxed italic">
                          "{item.resume_evidence}"
                        </p>
                      ) : (
                        <div className="flex items-center text-[11px] text-rose-400/90 italic space-x-1.5">
                          <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                          <span>No explicit candidate degree or certification found matching this requirement</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

