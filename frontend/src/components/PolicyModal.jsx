import React from "react";
import { X, ShieldCheck, BookOpen, AlertCircle, DollarSign, CheckCircle } from "lucide-react";

export default function PolicyModal({ isOpen, onClose, policies }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="glass-panel-elevated rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col border border-slate-700 shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-cyan-500/20 border border-cyan-500/30 text-cyan-400">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Enterprise Fulfilment Policy Sources</h2>
              <p className="text-xs text-slate-400">Governing SLA Protocols, Permitted Actions & Compensation Limits</p>
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
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {policies.map((p) => (
            <div key={p.policy_id} className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 text-xs space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200 text-sm">{p.title}</span>
                <span className="font-mono text-[10px] text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/30">
                  {p.policy_id}
                </span>
              </div>

              <p className="text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                {p.playbook_text}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-emerald-400 font-semibold block mb-1">Permitted Actions:</span>
                  <div className="flex flex-wrap gap-1">
                    {(p.permitted_actions || []).map((act, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-500/30 font-mono text-[10px]">
                        {act}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-rose-400 font-semibold block mb-1">Prohibited Guardrail Actions:</span>
                  <div className="flex flex-wrap gap-1">
                    {(p.prohibited_actions || []).map((pact, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded bg-rose-950/40 text-rose-300 border border-rose-500/30 font-mono text-[10px]">
                        {pact}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                <span>Max Voucher Cap: <strong className="text-cyan-400">R$ {p.max_voucher_brl.toFixed(2)}</strong></span>
                <span className="text-amber-400 font-medium">Requires Human-in-the-Loop Signoff: Yes</span>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition"
          >
            Close Playbooks
          </button>
        </div>

      </div>
    </div>
  );
}
