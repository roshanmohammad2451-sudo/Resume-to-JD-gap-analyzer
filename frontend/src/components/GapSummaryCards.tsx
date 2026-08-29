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
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
      bgClass: 'bg-emerald-950/40 hover:bg-emerald-950/60',
      borderClass: activeFilter === 'matched' ? 'border-emerald-500 ring-2 ring-emerald-500/30' : 'border-emerald-800/50',
      textClass: 'text-emerald-400',
      badgeClass: 'bg-emerald-900/60 text-emerald-300',
      priorityLabel: 'Full Alignment',
    },
    {
      id: 'partial' as SkillFilterType,
      label: 'Partial Matches',
      count: partialCount,
      subtitle: 'Related or overlapping skills',
      icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
      bgClass: 'bg-amber-950/40 hover:bg-amber-950/60',
      borderClass: activeFilter === 'partial' ? 'border-amber-500 ring-2 ring-amber-500/30' : 'border-amber-800/50',
      textClass: 'text-amber-400',
      badgeClass: 'bg-amber-900/60 text-amber-300',
      priorityLabel: 'Requires Context',
    },
    {
      id: 'missing_required' as SkillFilterType,
      label: 'Missing Required',
      count: missingRequiredCount,
      subtitle: 'Mandatory role prerequisites',
      icon: <XCircle className="w-5 h-5 text-rose-400" />,
      bgClass: 'bg-rose-950/40 hover:bg-rose-950/60',
      borderClass: activeFilter === 'missing_required' ? 'border-rose-500 ring-2 ring-rose-500/30' : 'border-rose-800/60',
      textClass: 'text-rose-400',
      badgeClass: 'bg-rose-900/70 text-rose-300 font-bold',
      priorityLabel: 'High Priority Gap',
      isHighPriority: true,
    },
    {
      id: 'missing_preferred' as SkillFilterType,
      label: 'Missing Preferred',
      count: missingPreferredCount,
      subtitle: 'Nice-to-have / bonus skills',
      icon: <Star className="w-5 h-5 text-purple-400" />,
      bgClass: 'bg-purple-950/40 hover:bg-purple-950/60',
      borderClass: activeFilter === 'missing_preferred' ? 'border-purple-500 ring-2 ring-purple-500/30' : 'border-purple-800/50',
      textClass: 'text-purple-400',
      badgeClass: 'bg-purple-900/60 text-purple-300',
      priorityLabel: 'Secondary Gap',
    },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Skill Requirement Summary ({totalSkills} Total Tracked)
          </h3>
        </div>
        {onSelectFilter && activeFilter !== 'all' && (
          <button
            type="button"
            onClick={() => onSelectFilter('all')}
            className="text-xs text-cyan-400 hover:text-cyan-300 underline font-medium"
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
              className={`group relative rounded-xl p-5 border transition-all duration-200 cursor-pointer ${card.bgClass} ${card.borderClass} shadow-lg flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
                    {card.icon}
                  </div>
                  <span className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full ${card.badgeClass}`}>
                    {card.priorityLabel}
                  </span>
                </div>
                <div className="space-y-1">
                  <span className="text-xs font-semibold text-slate-300 block">
                    {card.label}
                  </span>
                  <div className="flex items-baseline space-x-2">
                    <span className={`text-3xl font-extrabold tracking-tight ${card.textClass}`}>
                      {card.count}
                    </span>
                    {totalSkills > 0 && (
                      <span className="text-xs text-slate-400 font-medium">
                        ({Math.round((card.count / totalSkills) * 100)}%)
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 group-hover:text-slate-200 transition-colors">
                <span>{card.subtitle}</span>
                <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>
        ))}
      </div>
    </div>
  );
};
