import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Star,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { SkillFilterType } from '../types/gap';

interface GapSummaryCardsProps {
  matchedCount: number;
  partialCount: number;
  missingRequiredCount: number;
  missingPreferredCount: number;
  activeFilter?: SkillFilterType;
  onSelectFilter?: (filter: SkillFilterType) => void;
}

export const GapSummaryCards: React.FC<GapSummaryCardsProps> = ({
  matchedCount,
  partialCount,
  missingRequiredCount,
  missingPreferredCount,
  activeFilter = 'all',
  onSelectFilter,
}) => {
  const totalSkills = matchedCount + partialCount + missingRequiredCount + missingPreferredCount;

  const cards = [
    {
      id: 'matched' as SkillFilterType,
      label: 'Fully Matched',
      count: matchedCount,
      subtitle: 'Verified in candidate resume',
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
      bgClass: 'bg-[#0d0f14]/70 hover:bg-[#121620]/90',
      borderClass: activeFilter === 'matched' ? 'border-emerald-500/60 ring-2 ring-emerald-500/20' : 'border-white/[0.08] hover:border-white/[0.16]',
      textClass: 'text-emerald-400',
      badgeClass: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
      dotClass: 'bg-emerald-400',
      priorityLabel: 'Full Alignment',
    },
    {
      id: 'partial' as SkillFilterType,
      label: 'Partial Matches',
      count: partialCount,
      subtitle: 'Related or overlapping skills',
      icon: <AlertTriangle className="w-4 h-4 text-amber-400" />,
      bgClass: 'bg-[#0d0f14]/70 hover:bg-[#121620]/90',
      borderClass: activeFilter === 'partial' ? 'border-amber-500/60 ring-2 ring-amber-500/20' : 'border-white/[0.08] hover:border-white/[0.16]',
      textClass: 'text-amber-400',
      badgeClass: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
      dotClass: 'bg-amber-400',
      priorityLabel: 'Requires Context',
    },
    {
      id: 'missing_required' as SkillFilterType,
      label: 'Missing Required',
      count: missingRequiredCount,
      subtitle: 'Mandatory role prerequisites',
      icon: <XCircle className="w-4 h-4 text-rose-400" />,
      bgClass: 'bg-[#0d0f14]/70 hover:bg-[#151114]/90',
      borderClass: activeFilter === 'missing_required' ? 'border-rose-500/60 ring-2 ring-rose-500/20' : 'border-white/[0.08] hover:border-white/[0.16]',
      textClass: 'text-rose-400',
      badgeClass: 'bg-rose-500/15 text-rose-300 border-rose-500/30 font-semibold',
      dotClass: 'bg-rose-400 animate-pulse',
      priorityLabel: 'High Priority Gap',
      isHighPriority: true,
    },
    {
      id: 'missing_preferred' as SkillFilterType,
      label: 'Missing Preferred',
      count: missingPreferredCount,
      subtitle: 'Nice-to-have / bonus skills',
      icon: <Star className="w-4 h-4 text-purple-400" />,
      bgClass: 'bg-[#0d0f14]/70 hover:bg-[#121620]/90',
      borderClass: activeFilter === 'missing_preferred' ? 'border-purple-500/60 ring-2 ring-purple-500/20' : 'border-white/[0.08] hover:border-white/[0.16]',
      textClass: 'text-purple-400',
      badgeClass: 'bg-purple-500/10 text-purple-300 border-purple-500/20',
      dotClass: 'bg-purple-400',
      priorityLabel: 'Secondary Gap',
    },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-zinc-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Skill Requirement Summary ({totalSkills} Total Tracked)
          </h3>
        </div>
        {onSelectFilter && activeFilter !== 'all' && (
          <button
            type="button"
            onClick={() => onSelectFilter('all')}
            className="text-xs text-zinc-400 hover:text-white underline font-medium cursor-pointer"
          >
            Show All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div
            key={card.id}
            onClick={() => onSelectFilter && onSelectFilter(card.id)}
            className={`group relative rounded-2xl p-5 border transition-all duration-200 cursor-pointer ${card.bgClass} ${card.borderClass} shadow-raycast-card flex flex-col justify-between`}
          >
            <div>
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.08] shadow-inner">
                  {card.icon}
                </div>
                <span className={`text-[10px] uppercase font-medium px-2 py-0.5 rounded-full border inline-flex items-center gap-1 ${card.badgeClass}`}>
                  <span className={`w-1 h-1 rounded-full ${card.dotClass}`} />
                  {card.priorityLabel}
                </span>
              </div>
              <div className="space-y-1">
                <span className="text-xs font-medium text-zinc-300 block">
                  {card.label}
                </span>
                <div className="flex items-baseline space-x-2">
                  <span className={`text-3xl font-extrabold tracking-tight ${card.textClass}`}>
                    {card.count}
                  </span>
                  {totalSkills > 0 && (
                    <span className="text-xs text-zinc-500 font-mono">
                      ({Math.round((card.count / totalSkills) * 100)}%)
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-zinc-500 group-hover:text-zinc-300 transition-colors">
              <span>{card.subtitle}</span>
              <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-zinc-400" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

