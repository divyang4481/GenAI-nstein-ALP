import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, FastForward, Search, ChevronDown, Boxes, BarChart3, Cloud, Brain, ShieldCheck, Cpu } from "lucide-react";
import { fetchLlmStatus } from "../services/api";

export default function Header({ isReplaying, onStartReplay, onPauseReplay, onResetReplay, onTriggerNext, onSetSpeed, currentSpeed, onOpenAwsModal, onOpenEvalModal, onOpenPolicyModal, onOpenNeuroModal, wsConnected }) {
  const [showReplay, setShowReplay] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  const [activeModel, setActiveModel] = useState("us.amazon.nova-lite-v1:0");
  const [llmReady, setLlmReady] = useState(false);
  const [fallbackActive, setFallbackActive] = useState(true);

  useEffect(() => {
    const refreshStatus = () => fetchLlmStatus()
      .then((data) => {
        if (data.active_model) setActiveModel(data.active_model);
        setLlmReady(Boolean(data.ready));
        setFallbackActive(Boolean(data.fallback_active));
      })
      .catch(() => {});
    refreshStatus();
    const timer = setInterval(refreshStatus, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-16 bg-[#0F172A] border-b border-slate-700/70 text-white sticky top-0 z-40">
      <div className="h-full max-w-[1600px] mx-auto px-6 flex items-center gap-4 lg:gap-6">
        <div className="flex items-center gap-3 min-w-fit">
          <div className="h-9 w-9 rounded-lg bg-[#0F6CBD] flex items-center justify-center"><Boxes className="h-5 w-5 text-white" /></div>
          <div><h1 className="text-base font-semibold leading-tight tracking-tight">RetailFlow</h1><p className="text-[11px] text-slate-400">Fulfilment Control Tower</p></div>
        </div>
        
        <span className="hidden md:inline-flex text-xs px-2.5 py-1 rounded-md border border-slate-700 bg-slate-800/60 text-slate-300 font-medium">
          Olist Brazilian Dataset
        </span>

        {/* AWS Bedrock readiness and deployment-approved models */}
        <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border border-sky-500/40 bg-sky-950/40 text-sky-200" title={activeModel}>
            <Cpu className="h-3.5 w-3.5 text-sky-400 animate-pulse" />
            <span className="font-semibold text-slate-100">Deployment-approved model: Amazon Nova Lite</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded border bg-amber-500/20 text-amber-300 border-amber-500/30">
              {llmReady ? "AWS Bedrock • Ready" : fallbackActive ? "Demo fallback active" : "Bedrock checking"}
            </span>
        </div>

        <div className="hidden lg:flex flex-1 max-w-xs relative ml-auto">
          <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-500" />
          <input aria-label="Global search" placeholder="Search orders, customers or routes" className="w-full bg-slate-800/80 border border-slate-700 rounded-lg py-1.5 pl-9 pr-3 text-xs outline-none focus:border-[#0F6CBD] text-slate-200 placeholder-slate-500" />
        </div>

        {/* Replay Controls Dropdown */}
        <div className="relative">
          <button onClick={() => setShowReplay(!showReplay)} className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 transition">
            <span className={`h-2 w-2 rounded-full ${wsConnected ? "bg-emerald-400 shadow-sm shadow-emerald-400" : "bg-amber-400"}`} /> {isReplaying ? "Replay live" : "Replay paused"}<ChevronDown className="h-3.5 w-3.5 text-slate-400" />
          </button>
          {showReplay && <div className="absolute right-0 top-11 w-72 bg-white text-slate-700 rounded-xl border border-slate-200 shadow-xl p-3 space-y-3 z-50">
            <div className="flex gap-2">
              <button onClick={isReplaying ? onPauseReplay : onStartReplay} className="flex-1 flex justify-center items-center gap-1.5 bg-[#0F6CBD] text-white rounded-lg py-2 text-xs font-medium hover:bg-[#0b5494] transition">{isReplaying ? <Pause className="h-3.5 w-3.5"/> : <Play className="h-3.5 w-3.5"/>}{isReplaying ? "Pause" : "Resume"}</button>
              <button onClick={onTriggerNext} className="p-2 border rounded-lg hover:bg-slate-50" title="Next event"><FastForward className="h-4 w-4 text-slate-600"/></button>
              <button onClick={onResetReplay} className="p-2 border rounded-lg hover:bg-slate-50" title="Reset"><RotateCcw className="h-4 w-4 text-slate-600"/></button>
            </div>
            <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-100"><span className="text-slate-500 font-medium">Replay speed</span><div className="flex gap-1">{[0.8,1.5,3.0].map(s=><button key={s} onClick={()=>onSetSpeed(s)} className={`px-2 py-1 rounded text-xs transition ${currentSpeed===s?"bg-blue-50 text-[#0F6CBD] font-bold border border-blue-200":"bg-slate-50 text-slate-600 hover:bg-slate-100"}`}>{s}s</button>)}</div></div>
          </div>}
        </div>

        <button onClick={onOpenEvalModal} className="hidden md:flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 transition font-medium"><BarChart3 className="h-4 w-4 text-sky-400"/> Evaluation</button>
        
        <div className="relative">
          <button onClick={()=>setShowInsights(!showInsights)} className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 transition font-medium">Solution insights <ChevronDown className="h-3.5 w-3.5 text-slate-400"/></button>
          {showInsights && <div className="absolute right-0 top-11 w-56 bg-white text-slate-700 rounded-xl border border-slate-200 shadow-xl p-1.5 z-50">
            {[{label:"AWS Architecture",icon:Cloud,fn:onOpenAwsModal},{label:"Neuro AI Alignment",icon:Brain,fn:onOpenNeuroModal},{label:"Policy Playbooks (MCP)",icon:ShieldCheck,fn:onOpenPolicyModal}].map(({label,icon:Icon,fn})=><button key={label} onClick={fn} className="w-full flex items-center gap-2.5 px-3 py-2 text-xs rounded-lg hover:bg-slate-50 text-slate-700 font-medium transition"><Icon className="h-4 w-4 text-sky-600"/>{label}</button>)}
          </div>}
        </div>

        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-sky-600 to-blue-500 text-white flex items-center justify-center text-xs font-bold shadow-sm">DP</div>
      </div>
    </header>
  );
}
