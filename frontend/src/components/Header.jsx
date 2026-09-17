import React from "react";
import { 
  Play, 
  Pause, 
  RotateCcw, 
  FastForward, 
  Cloud, 
  BarChart3, 
  ShieldCheck, 
  Zap, 
  Brain,
  Cpu
} from "lucide-react";

export default function Header({
  isReplaying,
  onStartReplay,
  onPauseReplay,
  onResetReplay,
  onTriggerNext,
  onSetSpeed,
  currentSpeed,
  onOpenAwsModal,
  onOpenEvalModal,
  onOpenPolicyModal,
  onOpenNeuroModal,
  wsConnected
}) {
  return (
    <header className="glass-panel border-b border-[#27354a] px-6 py-3.5 sticky top-0 z-40 bg-[#141c28]/95 backdrop-blur-md">
      <div className="max-w-[1780px] mx-auto flex flex-wrap items-center justify-between gap-4">
        
        {/* Brand & Live Stream Indicator */}
        <div className="flex items-center space-x-3.5">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-[#0088cc] via-[#00a3ff] to-[#38bdf8] flex items-center justify-center shadow-lg shadow-[#0088cc]/30 border border-[#00b4d8]/40">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                RetailFlow
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#0088cc]/20 text-[#38bdf8] border border-[#0088cc]/40 font-medium tracking-wide">
                  Cognizant Neuro AI
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono font-medium flex items-center gap-1">
                  <Cpu className="h-3 w-3" /> Ollama (Llama 3.1)
                </span>
              </h1>
            </div>
            <p className="text-xs text-[#94a3b8] flex items-center gap-1.5 mt-0.5">
              <span className={`inline-block h-2 w-2 rounded-full ${wsConnected ? 'bg-emerald-400 pulse-dot' : 'bg-rose-400'}`}></span>
              <span>Real-Time Olist Marketplace Stream</span>
              <span className="text-[#475569]">•</span>
              <span className="text-[#38bdf8] font-mono text-[11px]">Real Local LLM Inference Active</span>
            </p>
          </div>
        </div>

        {/* Replay Controller Toolbar */}
        <div className="flex items-center bg-[#0c121c] border border-[#27354a] rounded-xl p-1.5 shadow-inner gap-1">
          <button
            onClick={isReplaying ? onPauseReplay : onStartReplay}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shadow-sm ${
              isReplaying 
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30" 
                : "bg-[#0088cc] text-white border border-[#0099e6] hover:bg-[#0099e6] shadow-md shadow-[#0088cc]/25"
            }`}
            title={isReplaying ? "Pause Stream" : "Start Live Stream"}
          >
            {isReplaying ? (
              <>
                <Pause className="h-3.5 w-3.5 fill-current" /> Pause Replay
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" /> Stream Live
              </>
            )}
          </button>

          <button
            onClick={onTriggerNext}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-[#94a3b8] hover:text-white hover:bg-[#1c2738] transition"
            title="Emit next single order event"
          >
            <FastForward className="h-3.5 w-3.5" /> Next Event
          </button>

          <button
            onClick={onResetReplay}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-[#64748b] hover:text-[#cbd5e1] hover:bg-[#1c2738] transition"
            title="Reset to beginning"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Reset
          </button>

          <div className="h-4 w-px bg-[#27354a] mx-1"></div>

          {/* Speed Selector */}
          <div className="flex items-center space-x-1 text-xs">
            {[
              { label: "0.8s", val: 0.8 },
              { label: "1.5s", val: 1.5 },
              { label: "3.0s", val: 3.0 }
            ].map((s) => (
              <button
                key={s.val}
                onClick={() => onSetSpeed(s.val)}
                className={`px-2 py-1 rounded text-[11px] font-mono transition ${
                  currentSpeed === s.val 
                    ? "bg-[#0088cc] text-white font-bold shadow-xs" 
                    : "text-[#94a3b8] hover:text-white hover:bg-[#1c2738]"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {/* Global Action & Modals Trigger */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onOpenNeuroModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0088cc]/15 hover:bg-[#0088cc]/25 text-[#38bdf8] border border-[#0088cc]/40 text-xs font-semibold transition shadow-sm"
          >
            <Brain className="h-3.5 w-3.5 text-[#38bdf8]" />
            <span>Neuro AI Alignment</span>
          </button>

          <button
            onClick={onOpenAwsModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1c2738] hover:bg-[#233147] text-[#cbd5e1] border border-[#27354a] text-xs font-medium transition"
          >
            <Cloud className="h-3.5 w-3.5 text-[#00a3ff]" />
            <span>AWS Cloud</span>
          </button>

          <button
            onClick={onOpenEvalModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1c2738] hover:bg-[#233147] text-[#cbd5e1] border border-[#27354a] text-xs font-medium transition"
          >
            <BarChart3 className="h-3.5 w-3.5 text-purple-400" />
            <span>Benchmark</span>
          </button>

          <button
            onClick={onOpenPolicyModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#1c2738] hover:bg-[#233147] text-[#cbd5e1] border border-[#27354a] text-xs font-medium transition"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Playbooks</span>
          </button>
        </div>

      </div>
    </header>
  );
}
