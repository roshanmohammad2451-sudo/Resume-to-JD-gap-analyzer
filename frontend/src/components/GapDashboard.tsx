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
    <div className="space-y-8 animate-in fade-in duration-500">
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
      <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-6 sm:p-8 shadow-2xl space-y-8">
        {/* Section Header with Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <h3 className="text-xl font-bold text-white tracking-tight">
                Skill Gap & Evidence Breakdown
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Grounded, deterministic evaluation of requirements without non-deterministic AI variance
            </p>
          </div>

          {onRetry && (
            <button
              onClick={onRetry}
              disabled={isReanalyzing}
              className="inline-flex items-center px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed self-start sm:self-auto"
            >
              <RotateCcw className={`w-3.5 h-3.5 mr-1.5 text-cyan-400 ${isReanalyzing ? 'animate-spin' : ''}`} />
              <span>Re-run Gap Engine</span>
            </button>
          )}
        </div>

        {/* 10. Filter & View Controls */}
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
              <div className="flex items-center justify-between pb-2 border-b border-rose-900/30">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-rose-950 text-rose-400 border border-rose-800/80">
                    <XCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-rose-300 uppercase tracking-wider">
                      Missing Required Skills ({gapResult.missing_required_skills.length})
                    </h4>
                    <span className="text-[11px] text-rose-400/80 font-medium">
                      High Priority • Essential role requirements absent from candidate resume
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-rose-950 text-rose-300 border border-rose-800 font-bold">
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
                <div className="p-6 rounded-xl bg-emerald-950/20 border border-emerald-900/40 text-center space-y-1">
                  <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
                  <p className="text-xs font-semibold text-emerald-300">
                    {searchQuery ? 'No matching missing required skills for this search.' : 'Outstanding! Zero missing required skills identified.'}
                  </p>
                  {!searchQuery && (
                    <p className="text-[11px] text-slate-400">
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
              <div className="flex items-center justify-between pb-2 border-b border-amber-900/30">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-amber-950 text-amber-400 border border-amber-800/80">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-amber-300 uppercase tracking-wider">
                      Partially Matched Skills ({gapResult.partial_matches.length})
                    </h4>
                    <span className="text-[11px] text-amber-400/80 font-medium">
                      Related technologies or partial keyword overlap detected
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800 font-medium">
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
                <div className="p-6 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-center">
                  <p className="text-xs text-slate-400 italic">
                    {searchQuery ? 'No partial matches found for this search.' : 'No partial skill matches detected.'}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Section: FULLY MATCHED SKILLS */}
          {(activeTab === 'all' || activeTab === 'matched') && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-emerald-900/30">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/80">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-emerald-300 uppercase tracking-wider">
                      Fully Matched Skills ({gapResult.matched_skills.length})
                    </h4>
                    <span className="text-[11px] text-emerald-400/80 font-medium">
                      Exact or canonical equivalence confirmed with supporting evidence
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-medium">
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
                <div className="p-6 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-center">
                  <p className="text-xs text-slate-400 italic">
                    {searchQuery ? 'No matched skills found for this search.' : 'No fully matched skills detected in resume.'}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Section: MISSING PREFERRED SKILLS (Lower Priority) */}
          {(activeTab === 'all' || activeTab === 'missing_preferred') && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-purple-900/30">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-purple-950 text-purple-400 border border-purple-800/80">
                    <Star className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-purple-300 uppercase tracking-wider">
                      Missing Preferred Skills ({gapResult.missing_preferred_skills.length})
                    </h4>
                    <span className="text-[11px] text-purple-400/80 font-medium">
                      Secondary • Nice-to-have / bonus qualifications absent from resume
                    </span>
                  </div>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-800 font-medium">
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
                <div className="p-6 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-center">
                  <p className="text-xs text-slate-400 italic">
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
        <div className="pt-4 border-t border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>Phase 5 Deterministic Gap Engine • Grounded Evidence Only</span>
            </div>
            <button
              type="button"
              onClick={() => setShowFormulaFooter(!showFormulaFooter)}
              className="text-xs text-cyan-400 hover:text-cyan-300 inline-flex items-center font-medium"
            >
              <HelpCircle className="w-3.5 h-3.5 mr-1" />
              <span>{showFormulaFooter ? 'Hide Formula' : 'Formula Documentation'}</span>
              {showFormulaFooter ? <ChevronUp className="w-3.5 h-3.5 ml-1" /> : <ChevronDown className="w-3.5 h-3.5 ml-1" />}
            </button>
          </div>

          {showFormulaFooter && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/90 text-xs text-slate-300 space-y-2 animate-in fade-in duration-200">
              <p className="font-semibold text-white">Transparent Weighted Match Scoring Formula:</p>
              <p className="text-slate-400 leading-relaxed">
                {gapResult.summary?.formula || '70% Required Skills Weight + 30% Preferred Skills Weight (100% Required if no Preferred skills present).'}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-[11px]">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block">Required Skills Weight:</span>
                  <span className="font-mono font-bold text-cyan-400">70% (0.70)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block">Preferred Skills Weight:</span>
                  <span className="font-mono font-bold text-purple-400">30% (0.30)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block">Match Status Values:</span>
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
