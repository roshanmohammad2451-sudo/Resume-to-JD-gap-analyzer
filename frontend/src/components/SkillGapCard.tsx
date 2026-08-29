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
        cardBg: 'bg-slate-900/60 hover:bg-slate-900/80',
        border: 'border-emerald-900/40 hover:border-emerald-700/60',
        icon: <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />,
        badgeText: 'Matched',
        badgeClass: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/70',
        titleColor: 'text-emerald-300',
        priorityNotice: null,
      };
    }
    if (isPartial) {
      return {
        cardBg: 'bg-slate-900/60 hover:bg-slate-900/80',
        border: 'border-amber-900/40 hover:border-amber-700/60',
        icon: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />,
        badgeText: 'Partial Match',
        badgeClass: 'bg-amber-950/80 text-amber-400 border-amber-800/70',
        titleColor: 'text-amber-300',
        priorityNotice: 'Partial match identified based on terminology overlap or related technology.',
      };
    }
    if (isRequired) {
      return {
        cardBg: 'bg-slate-900/70 hover:bg-slate-900/90',
        border: 'border-rose-900/50 hover:border-rose-700/80',
        icon: <AlertOctagon className="w-4 h-4 text-rose-400 shrink-0" />,
        badgeText: 'Missing Required',
        badgeClass: 'bg-rose-950 text-rose-300 border-rose-800 font-bold',
        titleColor: 'text-rose-300',
        priorityNotice: 'CRITICAL GAP: This skill is explicitly required for the role.',
      };
    }
    return {
      cardBg: 'bg-slate-900/60 hover:bg-slate-900/80',
      border: 'border-purple-900/40 hover:border-purple-700/60',
      icon: <Star className="w-4 h-4 text-purple-400 shrink-0" />,
      badgeText: 'Missing Preferred',
      badgeClass: 'bg-purple-950/80 text-purple-400 border-purple-800/70',
      titleColor: 'text-purple-300',
      priorityNotice: 'Preferred / nice-to-have requirement gap.',
    };
  };

  const theme = getTheme();

  return (
    <div className={`rounded-xl border ${theme.border} ${theme.cardBg} transition-all duration-200 shadow-md overflow-hidden`}>
      {/* Card Header Row */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-3.5 sm:p-4 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 select-none"
      >
        <div className="flex items-center space-x-3">
          <div className="p-1.5 rounded-lg bg-slate-950 border border-slate-800">
            {theme.icon}
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-sm font-bold capitalize ${theme.titleColor}`}>
                {item.normalized_skill_name}
              </span>

              {/* Requirement Importance Badge */}
              <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full border ${
                isRequired 
                  ? 'bg-rose-950/60 text-rose-300 border-rose-800/60' 
                  : 'bg-purple-950/60 text-purple-300 border-purple-800/60'
              }`}>
                {item.requirement_importance}
              </span>

              {/* Source Category Tag */}
              {item.category && (
                <span className="text-[10px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60 inline-flex items-center">
                  <Tag className="w-2.5 h-2.5 mr-1 text-slate-500" />
                  {item.category}
                </span>
              )}
            </div>

            {/* Quick Context / Wording line when collapsed */}
            <div className="text-[11px] text-slate-400 mt-1 flex flex-wrap items-center gap-x-3 gap-y-0.5">
              {item.original_jd_wording && item.original_jd_wording.toLowerCase() !== item.normalized_skill_name.toLowerCase() && (
                <span>JD Term: <strong className="text-slate-300 font-normal">"{item.original_jd_wording}"</strong></span>
              )}
              {item.original_resume_wording && item.original_resume_wording.toLowerCase() !== item.normalized_skill_name.toLowerCase() && (
                <span>Resume: <strong className="text-slate-300 font-normal">"{item.original_resume_wording}"</strong></span>
              )}
            </div>
          </div>
        </div>

        {/* Right Status Badge & Expand Toggle */}
        <div className="flex items-center justify-between sm:justify-end space-x-3 shrink-0">
          <span className={`text-xs px-2.5 py-1 rounded-lg border font-semibold inline-flex items-center ${theme.badgeClass}`}>
            {theme.badgeText}
          </span>
          <button
            type="button"
            className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            aria-label={isExpanded ? 'Collapse evidence' : 'Expand evidence'}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Expandable Grounded Evidence Body */}
      {isExpanded && (
        <div className="px-3.5 sm:px-4 pb-4 pt-1 border-t border-slate-800/60 space-y-3 bg-slate-950/40 animate-in fade-in duration-200">
          {theme.priorityNotice && (
            <div className={`text-[11px] px-3 py-1.5 rounded-lg border flex items-center space-x-1.5 ${
              isRequired 
                ? 'bg-rose-950/60 border-rose-800/60 text-rose-300 font-medium' 
                : 'bg-slate-900 border-slate-800 text-slate-400'
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
