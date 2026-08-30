import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  Star, 
  ChevronDown, 
  ChevronUp, 
  Tag, 
  AlertOctagon
} from 'lucide-react';
import { SkillGapItem } from '../types/gap';
import { EvidenceCard } from './EvidenceCard';

interface SkillGapCardProps {
  item: SkillGapItem;
  defaultExpanded?: boolean;
}

export const SkillGapCard: React.FC<SkillGapCardProps> = ({ item, defaultExpanded = false }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(defaultExpanded);

  const isMatched = item.match_status === 'matched';
  const isPartial = item.match_status === 'partial';
  const isRequired = item.requirement_importance === 'required';

  // Card theme styling based on match status and importance
  const getTheme = () => {
    if (isMatched) {
      return {
        cardBg: 'bg-[#0d0e13]/60 hover:bg-[#12141c]/80',
        border: 'border-emerald-500/20 hover:border-emerald-500/35',
        icon: <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />,
        badgeText: 'Matched',
        badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25',
        dotClass: 'bg-emerald-400',
        titleColor: 'text-zinc-100',
        priorityNotice: null,
      };
    }
    if (isPartial) {
      return {
        cardBg: 'bg-[#0d0e13]/60 hover:bg-[#12141c]/80',
        border: 'border-amber-500/20 hover:border-amber-500/35',
        icon: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />,
        badgeText: 'Partial Match',
        badgeClass: 'bg-amber-500/10 text-amber-300 border-amber-500/25',
        dotClass: 'bg-amber-400',
        titleColor: 'text-zinc-100',
        priorityNotice: 'Partial match identified based on terminology overlap or related technology.',
      };
    }
    if (isRequired) {
      return {
        cardBg: 'bg-[#0d0e13]/70 hover:bg-[#151216]/90',
        border: 'border-rose-500/25 hover:border-rose-500/40',
        icon: <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />,
        badgeText: 'Missing Required',
        badgeClass: 'bg-rose-500/15 text-rose-300 border-rose-500/30 font-semibold',
        dotClass: 'bg-rose-400 animate-pulse',
        titleColor: 'text-zinc-100',
        priorityNotice: 'CRITICAL GAP: This skill is explicitly required for the role.',
      };
    }
    return {
      cardBg: 'bg-[#0d0e13]/60 hover:bg-[#12141c]/80',
      border: 'border-purple-500/20 hover:border-purple-500/35',
      icon: <Star className="w-4 h-4 text-purple-400 shrink-0" />,
      badgeText: 'Missing Preferred',
      badgeClass: 'bg-purple-500/10 text-purple-300 border-purple-500/25',
      dotClass: 'bg-purple-400',
      titleColor: 'text-zinc-100',
      priorityNotice: 'Preferred / nice-to-have requirement gap.',
    };
  };

  const theme = getTheme();

  return (
    <div className={`rounded-xl border ${theme.border} ${theme.cardBg} transition-all duration-200 shadow-sm overflow-hidden`}>
      {/* Card Header Row */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-3.5 sm:p-4 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 select-none"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.08] shadow-inner">
            {theme.icon}
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-sm font-semibold capitalize tracking-tight ${theme.titleColor}`}>
                {item.normalized_skill_name}
              </span>

              {/* Requirement Importance Badge */}
              <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full border ${
                isRequired 
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' 
                  : 'bg-purple-500/10 text-purple-400 border-purple-500/20'
              }`}>
                {item.requirement_importance}
              </span>

              {/* Source Category Tag */}
              {item.category && (
                <span className="text-[10px] text-zinc-400 bg-white/[0.04] px-2 py-0.5 rounded-full border border-white/[0.08] inline-flex items-center">
                  <Tag className="w-2.5 h-2.5 mr-1 text-zinc-500" />
                  {item.category}
                </span>
              )}
            </div>

            {/* Quick Context / Wording line when collapsed */}
            <div className="text-[11px] text-zinc-400 mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
              {item.original_jd_wording && item.original_jd_wording.toLowerCase() !== item.normalized_skill_name.toLowerCase() && (
                <span>JD Term: <strong className="text-zinc-300 font-normal">"{item.original_jd_wording}"</strong></span>
              )}
              {item.original_resume_wording && item.original_resume_wording.toLowerCase() !== item.normalized_skill_name.toLowerCase() && (
                <span>Resume: <strong className="text-zinc-300 font-normal">"{item.original_resume_wording}"</strong></span>
              )}
            </div>
          </div>
        </div>

        {/* Right Status Badge & Expand Toggle */}
        <div className="flex items-center justify-between sm:justify-end space-x-3 shrink-0">
          <span className={`text-xs px-2.5 py-1 rounded-full border inline-flex items-center gap-1.5 ${theme.badgeClass}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${theme.dotClass}`} />
            {theme.badgeText}
          </span>
          <button
            type="button"
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08] transition-colors cursor-pointer"
            aria-label={isExpanded ? 'Collapse evidence' : 'Expand evidence'}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Expandable Grounded Evidence Body */}
      {isExpanded && (
        <div className="px-3.5 sm:px-4 pb-4 pt-1 border-t border-white/[0.06] space-y-3 bg-black/20 animate-in fade-in duration-150">
          {theme.priorityNotice && (
            <div className={`text-[11px] px-3 py-1.5 rounded-xl border flex items-center space-x-2 ${
              isRequired 
                ? 'bg-rose-500/10 border-rose-500/20 text-rose-300 font-medium' 
                : 'bg-white/[0.03] border-white/[0.08] text-zinc-400'
            }`}>
              <AlertOctagon className="w-3.5 h-3.5 text-rose-400 shrink-0" />
              <span>{theme.priorityNotice}</span>
            </div>
          )}

          <EvidenceCard
            jdEvidence={item.jd_evidence}
            resumeEvidence={item.resume_evidence}
            jdWording={item.original_jd_wording}
            resumeWording={item.original_resume_wording}
            explanation={item.evidence}
          />
        </div>
      )}
    </div>
  );
};

