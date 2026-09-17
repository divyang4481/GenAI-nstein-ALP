import React from "react";
import { X, Sparkles, Brain, Cpu, Database, ShieldAlert, CheckCircle, Terminal, Layers, Activity } from "lucide-react";

export default function NeuroAiAlignmentModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const mappings = [
    {
      concept: "Multi-Agent Systems",
      application: "5 Specialized Agents",
      desc: "Delivery-Risk Agent, Evidence Agent, Policy Retrieval Agent, Recovery Agent, and Enterprise Guardrail Agent exchange versioned HTTP task envelopes.",
      icon: Cpu,
      color: "text-blue-400"
    },
    {
      concept: "Neuro AI Multi-Agent Accelerator",
      application: "Orchestration Pattern",
      desc: "Inspired by / aligned to Cognizant Neuro AI Multi-Agent Accelerator orchestration patterns, decoupling ingestion, multi-tool reasoning, and governance.",
      icon: Brain,
      color: "text-purple-400"
    },
    {
      concept: "Neuro AI",
      application: "Evidence-Grounded GenAI",
      desc: "Generative AI models synthesize concise recovery recommendations grounded in historical Olist replay evidence and retrieved policy sources.",
      icon: Sparkles,
      color: "text-cyan-400"
    },
    {
      concept: "Neuro SAN",
      application: "Enterprise Knowledge & Policies",
      desc: "Serves as the governed enterprise knowledge/data layer for operational retail playbooks, SLA rules, and compensation caps.",
      icon: Database,
      color: "text-amber-400"
    },
    {
      concept: "Neuro IT Operations",
      application: "Operational Model",
      desc: "Applies the operational paradigm: replay alerts, latency observability, incident/recovery lifecycle, and an append-only demo audit trail.",
      icon: Activity,
      color: "text-emerald-400"
    },
    {
      concept: "Model Context Protocol (MCP)",
      application: "Standardized Tool Layer",
      desc: "Standard MCP tool interfaces: getOrder, getSellerHistory, getPolicy, findSimilarCases, createCase, escalateCarrier, and draftCustomerMessage.",
      icon: Terminal,
      color: "text-rose-400"
    },
    {
      concept: "Guardrails & Responsible AI",
      application: "Strict Policy Bounds",
      desc: "Zero autonomous refunds, no unsolicited customer messaging without human review, and voucher caps strictly <= R$ 25.00.",
      icon: ShieldAlert,
      color: "text-emerald-400"
    },
    {
      concept: "LLM Evaluation & Benchmarking",
      application: "Ground-Truth Auditing",
      desc: "Automated precision/recall evaluation tested against historical Olist delivery delays, measuring structured-output validity and policy compliance.",
      icon: Layers,
      color: "text-indigo-400"
    }
  ];

  const demoSteps = [
    "1. Olist historical order data is replayed as a live stream.",
    "2. A delivery-risk event arrives at transit hub.",
    "3. The Risk Agent identifies high SLA delay likelihood (> 0.65).",
    "4. MCP tools retrieve order, seller exception history, and policy evidence.",
    "5. Recovery Agent drafts proactive carrier escalation and customer update notice.",
    "6. Guardrail blocks automatic execution (enforces Responsible AI bounds).",
    "7. Operations analyst approves the brief; the audit ledger updates immediately."
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="glass-panel-elevated rounded-2xl max-w-4xl w-full max-h-[92vh] flex flex-col border border-slate-700 shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 text-white shadow-lg shadow-purple-500/20">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Cognizant Neuro AI Alignment & Positioning</h2>
              <p className="text-xs text-slate-400">Enterprise AI Accelerators, MCP Tool Protocol & Operational Model</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          
          {/* Executive Positioning Quote */}
          <div className="bg-gradient-to-r from-purple-950/40 via-slate-900 to-indigo-950/40 border border-purple-500/30 rounded-xl p-4 text-xs text-purple-200 shadow-sm leading-relaxed">
            <span className="text-[10px] font-mono uppercase tracking-wider text-purple-400 font-bold block mb-1">
              ✨ Core Positioning Statement:
            </span>
            <blockquote className="italic font-semibold text-white text-sm">
              “RetailFlow applies multi-agent orchestration and MCP-based tool access to convert real-time fulfilment risk events into policy-governed, human-approved recovery recommendations.”
            </blockquote>
          </div>

          {/* Alignment Grid */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Application of Learning & Cognizant Neuro AI Accelerators
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {mappings.map((m, idx) => {
                const Icon = m.icon;
                return (
                  <div key={idx} className="bg-slate-900/80 rounded-xl p-3.5 border border-slate-800 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-200 flex items-center gap-1.5">
                        <Icon className={`h-3.5 w-3.5 ${m.color}`} />
                        {m.concept}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-cyan-400 border border-slate-800">
                        {m.application}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                      {m.desc}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Live Demo Sequence */}
          <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 text-xs space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <CheckCircle className="h-4 w-4 text-emerald-400" /> Live Demonstration Narrative Flow
            </h3>
            <div className="grid grid-cols-1 gap-1.5 pt-1">
              {demoSteps.map((step, i) => (
                <div key={i} className="text-[11px] text-slate-300 font-mono bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800/80">
                  {step}
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition"
          >
            Close Alignment View
          </button>
        </div>

      </div>
    </div>
  );
}
