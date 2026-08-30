import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Star, 
  Layers,
  Search,
  X
} from 'lucide-react';
import { SkillFilterType } from '../types/gap';

interface SkillFilterTabsProps {
  activeTab: SkillFilterType;
  onTabChange: (tab: SkillFilterType) => void;
  counts: {
    all: number;
    matched: number;
    partial: number;
    missing_required: number;
    missing_preferred: number;
  };
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export const SkillFilterTabs: React.FC<SkillFilterTabsProps> = ({
  activeTab,
  onTabChange,
  counts,
  searchQuery,
  onSearchChange,
}) => {
  const tabs: { id: SkillFilterType; label: string; count: number; icon: React.ReactNode; activeColor: string }[] = [
    {
      id: 'all',
      label: 'All Skills',
      count: counts.all,
      icon: <Layers className="w-3.5 h-3.5 mr-1.5" />,
      activeColor: 'bg-white/[0.12] text-white shadow-sm border border-white/[0.15]',
    },
    {
      id: 'matched',
      label: 'Matched',
      count: counts.matched,
      icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />,
      activeColor: 'bg-emerald-500/15 text-emerald-300 shadow-sm border border-emerald-500/30',
    },
    {
      id: 'partial',
      label: 'Partial',
      count: counts.partial,
      icon: <AlertTriangle className="w-3.5 h-3.5 mr-1.5 text-amber-400" />,
      activeColor: 'bg-amber-500/15 text-amber-300 shadow-sm border border-amber-500/30',
    },
    {
      id: 'missing_required',
      label: 'Missing Required',
      count: counts.missing_required,
      icon: <XCircle className="w-3.5 h-3.5 mr-1.5 text-rose-400" />,
      activeColor: 'bg-rose-500/15 text-rose-300 shadow-sm border border-rose-500/30',
    },
    {
      id: 'missing_preferred',
      label: 'Missing Preferred',
      count: counts.missing_preferred,
      icon: <Star className="w-3.5 h-3.5 mr-1.5 text-purple-400" />,
      activeColor: 'bg-purple-500/15 text-purple-300 shadow-sm border border-purple-500/30',
    },
  ];

  return (
    <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 pb-3 border-b border-white/[0.08]">
      {/* Raycast Segmented Control Bar */}
      <div className="flex flex-wrap items-center gap-1 p-1 bg-black/40 backdrop-blur-md rounded-xl border border-white/[0.08]">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium transition-all select-none cursor-pointer ${
                isActive
                  ? tab.activeColor
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]'
              }`}
            >
              {tab.icon}
              <span className="tracking-tight">{tab.label}</span>
              <span className={`ml-2 px-1.5 py-0.2 rounded-full text-[10px] font-mono font-medium ${
                isActive ? 'bg-white/[0.15] text-white' : 'bg-white/[0.06] text-zinc-400'
              }`}>
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Quick Search Input styled like Raycast Command Palette Search */}
      <div className="relative w-full md:w-64">
        <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter skill by name..."
          className="w-full pl-8.5 pr-8 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-zinc-200 text-xs placeholder:text-zinc-500 focus:outline-none focus:border-white/[0.24] focus:bg-white/[0.05] transition-all"
        />
        {searchQuery ? (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.1] transition-colors cursor-pointer"
            aria-label="Clear filter query"
          >
            <X className="w-3 h-3" />
          </button>
        ) : (
          <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono text-zinc-500 pointer-events-none">
            Filter
          </span>
        )}
      </div>
    </div>
  );
};

