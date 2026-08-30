import React, { useState } from 'react';
import { 
  Award, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Info, 
  ChevronDown, 
  ChevronUp
} from 'lucide-react';
import { GapSummaryData } from '../types/gap';

interface MatchScoreCardProps {
  score: number;
  summary?: GapSummaryData;
}

export const MatchScoreCard: React.FC<MatchScoreCardProps> = ({ score, summary }) => {
  const [showFormulaDetails, setShowFormulaDetails] = useState<boolean>(false);

  // Interpretation strictly following specifications:
  // 80–100 = Strong Match
  // 60–79 = Good Match
  // 40–59 = Moderate Match
  // 0–39 = Low Match
  const getInterpretation = (val: number) => {
    if (val >= 80) {
      return {
        label: 'Strong Match',
        description: 'Candidate demonstrates strong alignment with core job requirements and technical competencies.',
        badgeBg: 'bg-emerald-500/10',
        badgeText: 'text-emerald-400',
        badgeBorder: 'border-emerald-500/20',
        dotColor: 'bg-emerald-400',
        glowColor: 'from-emerald-500/15 via-teal-500/5 to-transparent',
        textColor: 'text-emerald-400',
        icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" />,
        progressColor: 'bg-gradient-to-r from-emerald-500 to-teal-400',
      };
    }
    if (val >= 60) {
      return {
        label: 'Good Match',
        description: 'Candidate satisfies most key requirements with only minor or secondary skill gaps.',
        badgeBg: 'bg-sky-500/10',
        badgeText: 'text-sky-400',
        badgeBorder: 'border-sky-500/20',
        dotColor: 'bg-sky-400',
        glowColor: 'from-sky-500/15 via-blue-500/5 to-transparent',
        textColor: 'text-sky-400',
        icon: <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-sky-400" />,
        progressColor: 'bg-gradient-to-r from-sky-500 to-cyan-400',
      };
    }
    if (val >= 40) {
      return {
        label: 'Moderate Match',
        description: 'Candidate meets some qualifications but has notable gaps in required skills.',
        badgeBg: 'bg-amber-500/10',
        badgeText: 'text-amber-400',
        badgeBorder: 'border-amber-500/20',
        dotColor: 'bg-amber-400',
        glowColor: 'from-amber-500/15 via-orange-500/5 to-transparent',
        textColor: 'text-amber-400',
        icon: <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-400" />,
        progressColor: 'bg-gradient-to-r from-amber-500 to-yellow-400',
      };
    }
    return {
      label: 'Low Match',
      description: 'Significant gaps identified across fundamental required skills and experience.',
      badgeBg: 'bg-rose-500/10',
      badgeText: 'text-rose-400',
      badgeBorder: 'border-rose-500/20',
      dotColor: 'bg-rose-400',
      glowColor: 'from-rose-500/15 via-red-500/5 to-transparent',
      textColor: 'text-rose-400',
      icon: <XCircle className="w-3.5 h-3.5 mr-1 text-rose-400" />,
      progressColor: 'bg-gradient-to-r from-rose-500 to-red-400',
    };
  };

  const tier = getInterpretation(score);

  return (
    <div className={`relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0c0d12]/90 backdrop-blur-xl shadow-raycast-card transition-all`}>
      {/* Ambient radial lighting in background */}
      <div className={`absolute top-0 right-1/4 -translate-y-1/2 w-96 h-96 bg-gradient-to-br ${tier.glowColor} rounded-full blur-3xl pointer-events-none opacity-40`} />

      <div className="relative p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          {/* Main Score Block */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
            {/* Score Ring Gauge Display */}
            <div className="relative flex items-center justify-center w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-white/[0.03] border border-white/[0.08] shadow-inner shrink-0 group">
              <div className="text-center">
                <span className={`text-3xl sm:text-4xl font-extrabold tracking-tight ${tier.textColor}`}>
                  {score.toFixed(1)}%
                </span>
                <span className="block text-[10px] font-mono uppercase tracking-widest text-zinc-500 mt-0.5">
                  Match
                </span>
              </div>
              <div className="absolute inset-0 rounded-2xl ring-1 ring-white/10 group-hover:ring-white/20 transition-all pointer-events-none" />
            </div>

            {/* Title & Tier Badge */}
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center">
                  <Award className="w-4 h-4 mr-1 text-zinc-300" />
                  Deterministic Match Score
                </span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${tier.badgeBg} ${tier.badgeText} ${tier.badgeBorder} shadow-sm gap-1.5`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${tier.dotColor}`} />
                  {tier.label}
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                Resume-to-JD Fit: <span className={tier.textColor}>{tier.label}</span>
              </h2>
              <p className="text-xs sm:text-sm text-zinc-400 max-w-xl leading-relaxed">
                {tier.description}
              </p>
            </div>
          </div>

          {/* Scoring Basis & Formula Quick Box */}
          <div className="w-full lg:w-80 p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs text-zinc-300 space-y-2.5 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5 font-medium text-zinc-200">
                <Info className="w-3.5 h-3.5 text-zinc-400" />
                <span>Scoring Basis</span>
              </div>
              <button
                type="button"
                onClick={() => setShowFormulaDetails(!showFormulaDetails)}
                className="text-[11px] text-zinc-400 hover:text-white font-medium inline-flex items-center transition-colors cursor-pointer"
              >
                {showFormulaDetails ? 'Hide' : 'Details'}
                {showFormulaDetails ? <ChevronUp className="w-3 h-3 ml-0.5" /> : <ChevronDown className="w-3 h-3 ml-0.5" />}
              </button>
            </div>

            <p className="text-[11px] text-zinc-400 leading-relaxed">
              <strong className="text-zinc-300 font-medium">Required skills</strong> are weighted at 70%; <strong className="text-zinc-300 font-medium">preferred skills</strong> at 30%.
            </p>

            {/* Visual Progress Bar for Overall Match */}
            <div className="w-full bg-white/[0.06] rounded-full h-1.5 overflow-hidden">
              <div 
                className={`h-full ${tier.progressColor} transition-all duration-700 ease-out`}
                style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
              />
            </div>

            {/* Collapsible Formula Breakdown */}
            {showFormulaDetails && (
              <div className="pt-2 border-t border-white/[0.08] space-y-2 text-[11px] animate-in fade-in duration-150">
                <div className="flex justify-between items-center text-zinc-400">
                  <span>Required Skills Weight:</span>
                  <span className="font-mono text-zinc-200 font-semibold">70%</span>
                </div>
                {summary?.required_score_avg !== undefined && (
                  <div className="flex justify-between items-center text-zinc-400">
                    <span>Required Match Rate:</span>
                    <span className="font-mono text-zinc-200">
                      {(summary.required_score_avg * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                <div className="flex justify-between items-center text-zinc-400">
                  <span>Preferred Skills Weight:</span>
                  <span className="font-mono text-zinc-200 font-semibold">30%</span>
                </div>
                {summary?.preferred_score_avg !== undefined && summary?.preferred_score_avg !== null && (
                  <div className="flex justify-between items-center text-zinc-400">
                    <span>Preferred Match Rate:</span>
                    <span className="font-mono text-zinc-200">
                      {(summary.preferred_score_avg * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                <div className="pt-1.5 border-t border-white/[0.06] text-[10px] text-zinc-500 font-mono">
                  Matched = 1.0 • Partial = 0.5 • Missing = 0.0
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

