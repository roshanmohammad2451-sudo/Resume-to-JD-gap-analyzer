import React, { useState, useMemo } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Star, 
  ShieldCheck, 
  HelpCircle, 
  RotateCcw,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { GapAnalysisResponse, SkillFilterType, SkillGapItem } from '../types/gap';
import { MatchScoreCard } from './MatchScoreCard';
import { GapSummaryCards } from './GapSummaryCards';
import { SkillFilterTabs } from './SkillFilterTabs';
import { SkillGapCard } from './SkillGapCard';
import { ExperienceAlignment } from './ExperienceAlignment';
import { QualificationAlignment } from './QualificationAlignment';
import { GroundedRecommendations } from './GroundedRecommendations';

interface GapDashboardProps {
  gapResult: GapAnalysisResponse;
  onRetry?: () => void;
  isReanalyzing?: boolean;
}

export const GapDashboard: React.FC<GapDashboardProps> = ({
  gapResult,
  onRetry,
  isReanalyzing = false,
}) => {
  const [activeTab, setActiveTab] = useState<SkillFilterType>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showFormulaFooter, setShowFormulaFooter] = useState<boolean>(false);

  // Helper to filter skills by search query
  const filterByQuery = (items: SkillGapItem[]) => {
    if (!searchQuery.trim()) return items;
    const q = searchQuery.toLowerCase().trim();
    return items.filter(
      item => 
        item.normalized_skill_name.toLowerCase().includes(q) ||
        (item.original_jd_wording && item.original_jd_wording.toLowerCase().includes(q)) ||
        (item.original_resume_wording && item.original_resume_wording.toLowerCase().includes(q)) ||
        (item.category && item.category.toLowerCase().includes(q))
    );
  };

  const matchedFiltered = useMemo(() => filterByQuery(gapResult.matched_skills), [gapResult.matched_skills, searchQuery]);
  const partialFiltered = useMemo(() => filterByQuery(gapResult.partial_matches), [gapResult.partial_matches, searchQuery]);
  const missingReqFiltered = useMemo(() => filterByQuery(gapResult.missing_required_skills), [gapResult.missing_required_skills, searchQuery]);
  const missingPrefFiltered = useMemo(() => filterByQuery(gapResult.missing_preferred_skills), [gapResult.missing_preferred_skills, searchQuery]);

  const counts = useMemo(() => ({
    all: gapResult.matched_skills.length + gapResult.partial_matches.length + gapResult.missing_required_skills.length + gapResult.missing_preferred_skills.length,
    matched: gapResult.matched_skills.length,
    partial: gapResult.partial_matches.length,
    missing_required: gapResult.missing_required_skills.length,
    missing_preferred: gapResult.missing_preferred_skills.length,
  }), [gapResult]);

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. Overall Match Score Prominent Card */}
      <MatchScoreCard 
        score={gapResult.overall_match_score} 
        summary={gapResult.summary} 
      />

      {/* 2. Compact Skill Summary Metric Cards */}
      <GapSummaryCards 
        matchedCount={gapResult.matched_skills.length}
        partialCount={gapResult.partial_matches.length}
        missingRequiredCount={gapResult.missing_required_skills.length}
        missingPreferredCount={gapResult.missing_preferred_skills.length}
        activeFilter={activeTab}
        onSelectFilter={(tab) => setActiveTab(tab)}
      />

      {/* Main Results Container */}
      <div className="rounded-2xl bg-[#0c0d12]/95 border border-white/[0.08] p-6 sm:p-8 shadow-raycast-card space-y-8">
        {/* Section Header with Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/[0.08] gap-3">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 rounded-xl bg-white/[0.04] border border-white/[0.08] shadow-inner text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Skill Gap & Evidence Breakdown
              </h3>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Grounded, deterministic evaluation of requirements without non-deterministic AI variance
            </p>
          </div>

          {onRetry && (
            <button
              onClick={onRetry}
              disabled={isReanalyzing}
              className="inline-flex items-center px-3.5 py-1.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-zinc-200 hover:text-white border border-white/[0.1] text-xs font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed self-start sm:self-auto cursor-pointer"
            >
              <RotateCcw className={`w-3.5 h-3.5 mr-1.5 text-zinc-400 ${isReanalyzing ? 'animate-spin' : ''}`} />
              <span>Re-run Gap Engine</span>
            </button>
          )}
        </div>

        {/* Filter & View Controls */}
        <SkillFilterTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          counts={counts}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />

        {/* Categorized Skills Section Rendering */}
        <div className="space-y-8">
          {/* Section: MISSING REQUIRED SKILLS (Highest Priority) */}
          {(activeTab === 'all' || activeTab === 'missing_required') && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-rose-500/20">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    <XCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-rose-300 uppercase tracking-wider">
                      Missing Required Skills ({gapResult.missing_required_skills.length})
                    </h4>
                    <span className="text-[11px] text-rose-400/80 font-normal">
                      High Priority • Essential role requirements absent from candidate resume
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30 font-semibold">
                  Critical Gaps
                </span>
              </div>

              {missingReqFiltered.length > 0 ? (
                <div className="grid grid-cols-1 gap-3">
                  {missingReqFiltered.map((item, idx) => (
                    <SkillGapCard key={`req-${idx}`} item={item} defaultExpanded={true} />
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 text-center space-y-1">
                  <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
                  <p className="text-xs font-medium text-emerald-300">
                    {searchQuery ? 'No matching missing required skills for this search.' : 'Outstanding! Zero missing required skills identified.'}
                  </p>
                  {!searchQuery && (
                    <p className="text-[11px] text-zinc-400">
                      The candidate resume covers all mandatory skills specified in the Job Description.
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Section: PARTIAL MATCHES */}
          {(activeTab === 'all' || activeTab === 'partial') && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-amber-500/20">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-amber-300 uppercase tracking-wider">
                      Partially Matched Skills ({gapResult.partial_matches.length})
                    </h4>
                    <span className="text-[11px] text-amber-400/80 font-normal">
                      Related technologies or partial keyword overlap detected
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
                  Needs Review
                </span>
              </div>

              {partialFiltered.length > 0 ? (
                <div className="grid grid-cols-1 gap-3">
                  {partialFiltered.map((item, idx) => (
                    <SkillGapCard key={`part-${idx}`} item={item} defaultExpanded={true} />
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-dashed border-white/[0.08] text-center">
                  <p className="text-xs text-zinc-400 italic">
                    {searchQuery ? 'No partial matches found for this search.' : 'No partial skill matches detected.'}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Section: FULLY MATCHED SKILLS */}
          {(activeTab === 'all' || activeTab === 'matched') && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-emerald-500/20">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider">
                      Fully Matched Skills ({gapResult.matched_skills.length})
                    </h4>
                    <span className="text-[11px] text-emerald-400/80 font-normal">
                      Exact or canonical equivalence confirmed with supporting evidence
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium">
                  Verified Skills
                </span>
              </div>

              {matchedFiltered.length > 0 ? (
                <div className="grid grid-cols-1 gap-3">
                  {matchedFiltered.map((item, idx) => (
                    <SkillGapCard key={`match-${idx}`} item={item} defaultExpanded={false} />
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-dashed border-white/[0.08] text-center">
                  <p className="text-xs text-zinc-400 italic">
                    {searchQuery ? 'No matched skills found for this search.' : 'No fully matched skills detected in resume.'}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Section: MISSING PREFERRED SKILLS (Lower Priority) */}
          {(activeTab === 'all' || activeTab === 'missing_preferred') && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-purple-500/20">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
                    <Star className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-purple-300 uppercase tracking-wider">
                      Missing Preferred Skills ({gapResult.missing_preferred_skills.length})
                    </h4>
                    <span className="text-[11px] text-purple-400/80 font-normal">
                      Secondary • Nice-to-have / bonus qualifications absent from resume
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium">
                  Optional Gaps
                </span>
              </div>

              {missingPrefFiltered.length > 0 ? (
                <div className="grid grid-cols-1 gap-3">
                  {missingPrefFiltered.map((item, idx) => (
                    <SkillGapCard key={`pref-${idx}`} item={item} defaultExpanded={false} />
                  ))}
                </div>
              ) : (
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-dashed border-white/[0.08] text-center">
                  <p className="text-xs text-zinc-400 italic">
                    {searchQuery ? 'No missing preferred skills found for this search.' : 'Zero missing preferred skills.'}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 7. Experience / Duty Alignment */}
        <ExperienceAlignment items={gapResult.experience_gaps} />

        {/* 8. Qualification Gaps */}
        <QualificationAlignment items={gapResult.qualification_gaps} />

        {/* Phase 7: RAG-Grounded Recommendations */}
        <GroundedRecommendations gapResult={gapResult} />

        {/* Deterministic Scoring Basis & Verification Footer */}
        <div className="pt-4 border-t border-white/[0.08] space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-zinc-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Phase 5 Deterministic Gap Engine • Grounded Evidence Only</span>
            </div>
            <button
              type="button"
              onClick={() => setShowFormulaFooter(!showFormulaFooter)}
              className="text-xs text-zinc-400 hover:text-white inline-flex items-center font-medium transition-colors cursor-pointer"
            >
              <HelpCircle className="w-3.5 h-3.5 mr-1 text-zinc-500" />
              <span>{showFormulaFooter ? 'Hide Formula' : 'Formula Documentation'}</span>
              {showFormulaFooter ? <ChevronUp className="w-3.5 h-3.5 ml-1" /> : <ChevronDown className="w-3.5 h-3.5 ml-1" />}
            </button>
          </div>

          {showFormulaFooter && (
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.08] text-xs text-zinc-300 space-y-2 animate-in fade-in duration-150">
              <p className="font-semibold text-white">Transparent Weighted Match Scoring Formula:</p>
              <p className="text-zinc-400 leading-relaxed">
                {gapResult.summary?.formula || '70% Required Skills Weight + 30% Preferred Skills Weight (100% Required if no Preferred skills present).'}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-[11px]">
                <div className="p-2.5 rounded-lg bg-black/40 border border-white/[0.06]">
                  <span className="text-zinc-500 block">Required Skills Weight:</span>
                  <span className="font-mono font-bold text-zinc-200">70% (0.70)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-white/[0.06]">
                  <span className="text-zinc-500 block">Preferred Skills Weight:</span>
                  <span className="font-mono font-bold text-zinc-200">30% (0.30)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-white/[0.06]">
                  <span className="text-zinc-500 block">Match Status Values:</span>
                  <span className="font-mono text-emerald-400">Full: 1.0</span> • <span className="font-mono text-amber-400">Part: 0.5</span> • <span className="font-mono text-rose-400">Miss: 0.0</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

