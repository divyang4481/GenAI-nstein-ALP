import React, { useState } from "react";
import { Play, Pause, RotateCcw, FastForward, Search, ChevronDown, Boxes, BarChart3, Cloud, Brain, ShieldCheck } from "lucide-react";

export default function Header({ isReplaying, onStartReplay, onPauseReplay, onResetReplay, onTriggerNext, onSetSpeed, currentSpeed, onOpenAwsModal, onOpenEvalModal, onOpenPolicyModal, onOpenNeuroModal, wsConnected }) {
  const [showReplay, setShowReplay] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  return (
    <header className="h-16 bg-[#0F172A] border-b border-slate-700/70 text-white sticky top-0 z-40">
      <div className="h-full max-w-[1600px] mx-auto px-6 flex items-center gap-6">
        <div className="flex items-center gap-3 min-w-fit">
          <div className="h-9 w-9 rounded-lg bg-[#0F6CBD] flex items-center justify-center"><Boxes className="h-5 w-5" /></div>
          <div><h1 className="text-base font-semibold leading-tight">RetailFlow</h1><p className="text-[11px] text-slate-400">Fulfilment Control Tower</p></div>
        </div>
        <span className="hidden md:inline-flex text-xs px-2.5 py-1 rounded-md border border-slate-600 text-slate-300">Olist · Production replay</span>
        <div className="hidden lg:flex flex-1 max-w-md relative ml-auto">
          <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-500" />
          <input aria-label="Global search" placeholder="Search orders, customers or routes" className="w-full bg-slate-800/80 border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-xs outline-none focus:border-[#0F6CBD]" />
        </div>
        <div className="relative">
          <button onClick={() => setShowReplay(!showReplay)} className="flex items-center gap-2 text-xs px-3 py-2 rounded-lg border border-slate-700 hover:bg-slate-800">
            <span className={`h-2 w-2 rounded-full ${wsConnected ? "bg-emerald-400" : "bg-amber-400"}`} /> {isReplaying ? "Replay live" : "Replay paused"}<ChevronDown className="h-3.5 w-3.5" />
          </button>
          {showReplay && <div className="absolute right-0 top-11 w-72 bg-white text-slate-700 rounded-xl border border-slate-200 shadow-xl p-3 space-y-3">
            <div className="flex gap-2">
              <button onClick={isReplaying ? onPauseReplay : onStartReplay} className="flex-1 flex justify-center items-center gap-1.5 bg-[#0F6CBD] text-white rounded-lg py-2 text-xs">{isReplaying ? <Pause className="h-3.5 w-3.5"/> : <Play className="h-3.5 w-3.5"/>}{isReplaying ? "Pause" : "Resume"}</button>
              <button onClick={onTriggerNext} className="p-2 border rounded-lg" title="Next event"><FastForward className="h-4 w-4"/></button><button onClick={onResetReplay} className="p-2 border rounded-lg" title="Reset"><RotateCcw className="h-4 w-4"/></button>
            </div>
            <div className="flex items-center justify-between text-xs"><span className="text-slate-500">Replay speed</span><div className="flex gap-1">{[0.8,1.5,3].map(s=><button key={s} onClick={()=>onSetSpeed(s)} className={`px-2 py-1 rounded ${currentSpeed===s?"bg-blue-50 text-[#0F6CBD] font-semibold":"bg-slate-50"}`}>{s}s</button>)}</div></div>
          </div>}
        </div>
        <button onClick={onOpenEvalModal} className="hidden md:flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg hover:bg-slate-800"><BarChart3 className="h-4 w-4"/> Evaluation</button>
        <div className="relative">
          <button onClick={()=>setShowInsights(!showInsights)} className="flex items-center gap-1 text-xs px-2 py-2 rounded-lg hover:bg-slate-800">Solution insights <ChevronDown className="h-3.5 w-3.5"/></button>
          {showInsights && <div className="absolute right-0 top-11 w-52 bg-white text-slate-700 rounded-xl border border-slate-200 shadow-xl p-1.5">
            {[{label:"Architecture",icon:Cloud,fn:onOpenAwsModal},{label:"AI alignment",icon:Brain,fn:onOpenNeuroModal},{label:"Policy playbooks",icon:ShieldCheck,fn:onOpenPolicyModal}].map(({label,icon:Icon,fn})=><button key={label} onClick={fn} className="w-full flex items-center gap-2 px-3 py-2 text-xs rounded-lg hover:bg-slate-50"><Icon className="h-4 w-4 text-slate-500"/>{label}</button>)}
          </div>}
        </div>
        <div className="h-8 w-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center text-xs font-semibold">DO</div>
      </div>
    </header>
  );
}
