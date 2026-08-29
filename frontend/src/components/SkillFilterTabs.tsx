import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Star, 
  Layers,
  Search
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
      activeColor: 'bg-cyan-600 text-white shadow-cyan-500/20',
    },
    {
      id: 'matched',
      label: 'Matched',
      count: counts.matched,
      icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />,
      activeColor: 'bg-emerald-600 text-white shadow-emerald-500/20',
    },
    {
      id: 'partial',
      label: 'Partial',
      count: counts.partial,
      icon: <AlertTriangle className="w-3.5 h-3.5 mr-1.5 text-amber-400" />,
      activeColor: 'bg-amber-600 text-white shadow-amber-500/20',
    },
    {
      id: 'missing_required',
      label: 'Missing Required',
      count: counts.missing_required,
      icon: <XCircle className="w-3.5 h-3.5 mr-1.5 text-rose-400" />,
      activeColor: 'bg-rose-600 text-white shadow-rose-500/20',
    },
    {
      id: 'missing_preferred',
      label: 'Missing Preferred',
      count: counts.missing_preferred,
      icon: <Star className="w-3.5 h-3.5 mr-1.5 text-purple-400" />,
      activeColor: 'bg-purple-600 text-white shadow-purple-500/20',
    },
  ];

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
      {/* Tab Buttons */}
      <div className="flex flex-wrap items-center gap-1.5 p-1 bg-slate-900/90 rounded-xl border border-slate-800">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold transition-all select-none ${
                isActive
                  ? `${tab.activeColor} shadow-md`
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
              <span className={`ml-2 px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                isActive ? 'bg-black/30 text-white' : 'bg-slate-800 text-slate-400'
              }`}>
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Quick Search Input */}
      <div className="relative w-full sm:w-60">
        <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter skill by name..."
          className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 hover:text-slate-200"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
};
