import React, { useState } from 'react';
import { 
  GraduationCap, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
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
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-950 text-emerald-400 border border-emerald-800 inline-flex items-center">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Verified
          </span>
        );
      case 'partial':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-amber-950 text-amber-400 border border-amber-800 inline-flex items-center">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Partial
          </span>
        );
      case 'missing':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-rose-950 text-rose-400 border border-rose-800 inline-flex items-center">
            <XCircle className="w-3 h-3 mr-1" />
            Unverified
          </span>
        );
    }
  };

  return (
    <div className="rounded-2xl bg-slate-950/80 border border-slate-800 shadow-xl overflow-hidden">
      {/* Header */}
      <div 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 cursor-pointer bg-slate-900/60 hover:bg-slate-900/80 transition-colors border-b border-slate-800 select-none"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-white tracking-tight">
                Qualifications & Education Alignment
              </h3>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold">
                {items.length}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Verified education, degrees, and certifications matching role qualifications
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Status counts */}
          <div className="flex items-center space-x-1.5 text-[11px]">
            {matchedCount > 0 && (
              <span className="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 font-medium">
                {matchedCount} Verified
              </span>
            )}
            {partialCount > 0 && (
              <span className="px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800/80 font-medium">
                {partialCount} Partial
              </span>
            )}
            {missingCount > 0 && (
              <span className="px-2 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-800/80 font-medium">
                {missingCount} Unverified
              </span>
            )}
          </div>

          <button
            type="button"
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="p-5 space-y-4">
          {items.length === 0 ? (
            <div className="p-8 text-center rounded-xl bg-slate-900/40 border border-dashed border-slate-800">
              <p className="text-xs text-slate-400 italic">
                No specific educational or certification requirements were listed in the Job Description.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {items.map((item, idx) => (
                <div 
                  key={idx}
                  className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/90 hover:border-slate-700 transition-all space-y-3"
                >
                  {/* Top line: Qualification requirement + status */}
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2.5">
                    <div className="flex items-start space-x-2">
                      <Award className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="text-xs font-semibold text-slate-200 block leading-snug">
                          {item.requirement}
                        </span>
                        {item.details && (
                          <p className="text-[11px] text-slate-400 italic mt-0.5">
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
                  <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 flex items-start space-x-2.5">
                    <GraduationCap className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                    <div className="text-xs w-full">
                      <span className="text-[10px] uppercase font-semibold text-slate-500 block mb-0.5">
                        Candidate Education & Certification Evidence
                      </span>
                      {item.resume_evidence ? (
                        <p className="text-[11px] text-slate-300 leading-relaxed italic">
                          "{item.resume_evidence}"
                        </p>
                      ) : (
                        <div className="flex items-center text-[11px] text-rose-400/80 italic space-x-1">
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
