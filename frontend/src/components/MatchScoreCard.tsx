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
        badgeBg: 'bg-emerald-950/80',
        badgeText: 'text-emerald-400',
        badgeBorder: 'border-emerald-800/80',
        glowColor: 'from-emerald-500/20 to-teal-500/10',
        textColor: 'text-emerald-400',
        icon: <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-400" />,
        progressColor: 'bg-gradient-to-r from-emerald-500 to-teal-400',
      };
    }
    if (val >= 60) {
      return {
        label: 'Good Match',
        description: 'Candidate satisfies most key requirements with only minor or secondary skill gaps.',
        badgeBg: 'bg-sky-950/80',
        badgeText: 'text-sky-400',
        badgeBorder: 'border-sky-800/80',
        glowColor: 'from-sky-500/20 to-blue-500/10',
        textColor: 'text-sky-400',
        icon: <CheckCircle2 className="w-4 h-4 mr-1.5 text-sky-400" />,
        progressColor: 'bg-gradient-to-r from-sky-500 to-cyan-400',
      };
    }
    if (val >= 40) {
      return {
        label: 'Moderate Match',
        description: 'Candidate meets some qualifications but has notable gaps in required skills.',
        badgeBg: 'bg-amber-950/80',
        badgeText: 'text-amber-400',
        badgeBorder: 'border-amber-800/80',
        glowColor: 'from-amber-500/20 to-orange-500/10',
        textColor: 'text-amber-400',
        icon: <AlertTriangle className="w-4 h-4 mr-1.5 text-amber-400" />,
        progressColor: 'bg-gradient-to-r from-amber-500 to-yellow-400',
      };
    }
    return {
      label: 'Low Match',
      description: 'Significant gaps identified across fundamental required skills and experience.',
      badgeBg: 'bg-rose-950/80',
      badgeText: 'text-rose-400',
      badgeBorder: 'border-rose-800/80',
      glowColor: 'from-rose-500/20 to-red-500/10',
      textColor: 'text-rose-400',
      icon: <XCircle className="w-4 h-4 mr-1.5 text-rose-400" />,
      progressColor: 'bg-gradient-to-r from-rose-500 to-red-400',
    };
  };

  const tier = getInterpretation(score);

  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${tier.glowColor} p-px shadow-2xl transition-all`}>
      <div className="rounded-[15px] bg-slate-950/90 backdrop-blur-xl p-6 sm:p-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          {/* Main Score Block */}
          <div className="flex items-center space-x-6">
            {/* Score Ring Gauge Display */}
            <div className="relative flex items-center justify-center w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-slate-900 border border-slate-800/90 shadow-inner shrink-0 group">
              <div className="text-center">
                <span className={`text-3xl sm:text-4xl font-black tracking-tight ${tier.textColor}`}>
                  {score.toFixed(1)}%
                </span>
                <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-widest mt-0.5">
                  Match
                </span>
              </div>
              <div className="absolute inset-0 rounded-2xl ring-1 ring-white/10 group-hover:ring-cyan-500/30 transition-all pointer-events-none" />
            </div>

            {/* Title & Tier Badge */}
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center">
                  <Award className="w-4 h-4 mr-1 text-cyan-400" />
                  Deterministic Match Score
                </span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${tier.badgeBg} ${tier.badgeText} ${tier.badgeBorder} shadow-sm`}>
                  {tier.icon}
                  {tier.label}
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Resume-to-JD Fit: <span className={tier.textColor}>{tier.label}</span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 max-w-xl leading-relaxed">
                {tier.description}
              </p>
            </div>
          </div>

          {/* Scoring Basis & Formula Quick Box */}
          <div className="w-full lg:w-80 p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs text-slate-300 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5 font-semibold text-slate-200">
                <Info className="w-3.5 h-3.5 text-cyan-400" />
                <span>Scoring Basis</span>
              </div>
              <button
                type="button"
                onClick={() => setShowFormulaDetails(!showFormulaDetails)}
                className="text-[11px] text-cyan-400 hover:text-cyan-300 font-medium inline-flex items-center transition-colors focus:outline-none"
              >
                {showFormulaDetails ? 'Hide' : 'Details'}
                {showFormulaDetails ? <ChevronUp className="w-3 h-3 ml-0.5" /> : <ChevronDown className="w-3 h-3 ml-0.5" />}
              </button>
            </div>

            <p className="text-[11px] text-slate-400 leading-relaxed">
              <strong className="text-slate-300 font-medium">Required skills</strong> are weighted more heavily (70%) than <strong className="text-slate-300 font-medium">preferred skills</strong> (30%).
            </p>

            {/* Visual Progress Bar for Overall Match */}
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div 
                className={`h-full ${tier.progressColor} transition-all duration-700 ease-out`}
                style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
              />
            </div>

            {/* Collapsible Formula Breakdown */}
            {showFormulaDetails && (
              <div className="pt-2 border-t border-slate-800 space-y-2 text-[11px] animate-in fade-in duration-200">
                <div className="flex justify-between items-center text-slate-400">
                  <span>Required Skills Weight:</span>
                  <span className="font-mono text-cyan-400 font-semibold">70%</span>
                </div>
                {summary?.required_score_avg !== undefined && (
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Required Match Rate:</span>
                    <span className="font-mono text-slate-200">
                      {(summary.required_score_avg * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                <div className="flex justify-between items-center text-slate-400">
                  <span>Preferred Skills Weight:</span>
                  <span className="font-mono text-purple-400 font-semibold">30%</span>
                </div>
                {summary?.preferred_score_avg !== undefined && summary?.preferred_score_avg !== null && (
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Preferred Match Rate:</span>
                    <span className="font-mono text-slate-200">
                      {(summary.preferred_score_avg * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                <div className="pt-1.5 border-t border-slate-800/60 text-[10px] text-slate-500 italic">
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
