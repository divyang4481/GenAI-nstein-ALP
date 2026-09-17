import React, { useState } from "react";
import { 
  ShieldCheck, 
  Check, 
  X, 
  FileCheck2, 
  Truck, 
  MessageSquare, 
  History,
  Lock,
  UserCheck
} from "lucide-react";

export default function ActionConsole({ 
  activeIncident, 
  auditLedger, 
  onSubmitDecision, 
  isSubmitting 
}) {
  const [reviewerNotes, setReviewerNotes] = useState("Verified route congestion and seller late history. Approved for carrier escalation.");
  const [reviewerName, setReviewerName] = useState("Ops Specialist (Divyang)");

  const isPending = activeIncident?.status === "PENDING_REVIEW";
  const payload = activeIncident?.proposed_payload || {};

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[780px] overflow-hidden border border-[#27354a] bg-[#141c28]">
      
      {/* Header */}
      <div className="p-4 border-b border-[#27354a] bg-[#0f1622] flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-[#0088cc]/15 border border-[#0088cc]/30">
            <UserCheck className="h-4 w-4 text-[#38bdf8]" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">Operations Approval Console</h2>
            <p className="text-[11px] text-[#94a3b8]">Human-in-the-Loop Fulfillment Recovery Decision</p>
          </div>
        </div>

        {activeIncident && (
          <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
            activeIncident.status === "APPROVED" 
              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
              : activeIncident.status === "REJECTED"
              ? "bg-rose-500/20 text-rose-300 border-rose-500/40"
              : "bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse"
          }`}>
            {activeIncident.status.replace(/_/g, " ")}
          </span>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        
        {!activeIncident ? (
          <div className="h-48 flex flex-col items-center justify-center text-center p-6 text-[#64748b]">
            <FileCheck2 className="h-8 w-8 mb-2 opacity-40" />
            <p className="text-xs">No active incident selected. Select a high-risk order to review drafted recovery actions.</p>
          </div>
        ) : (
          <>
            {/* Action Brief Banner */}
            <div className="bg-[#0c121c] rounded-xl p-3.5 border border-[#0088cc]/40 text-xs space-y-2 shadow-inner">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#38bdf8] flex items-center gap-1.5">
                  <Lock className="h-3 w-3 text-[#0088cc]" /> Formal Action Brief
                </span>
                <span className="font-mono text-[10px] text-[#94a3b8]">{activeIncident.incident_id}</span>
              </div>
              <p className="text-[#f1f5f9] font-medium leading-relaxed">
                {activeIncident.recommended_action}
              </p>
            </div>

            {/* Proposed Recovery Steps */}
            <div className="space-y-2">
              <span className="text-[11px] font-bold uppercase text-[#94a3b8] tracking-wider">
                Action Items Requiring Operations Sign-Off:
              </span>

              {/* Step 1: Carrier Escalation */}
              <div className="bg-[#16202e] rounded-xl p-3 border border-[#27354a] text-xs flex items-start gap-3">
                <div className="p-2 rounded-lg bg-[#0088cc]/15 border border-[#0088cc]/30 mt-0.5">
                  <Truck className="h-4 w-4 text-[#38bdf8]" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-white flex items-center justify-between">
                    <span>1. Proactive Carrier Escalation</span>
                    <span className="text-[10px] font-mono text-[#00b4d8] bg-[#00b4d8]/10 px-1.5 py-0.5 rounded border border-[#00b4d8]/30">Priority 1 Expedited</span>
                  </div>
                  <p className="text-[11px] text-[#94a3b8] mt-1">
                    Dispatches priority ticket to Correios SEDEX hub liaison to bypass standard cross-dock queuing.
                  </p>
                </div>
              </div>

              {/* Step 2: Customer Message Draft */}
              <div className="bg-[#16202e] rounded-xl p-3 border border-[#27354a] text-xs flex items-start gap-3">
                <div className="p-2 rounded-lg bg-purple-500/15 border border-purple-500/30 mt-0.5">
                  <MessageSquare className="h-4 w-4 text-purple-400" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-white flex items-center justify-between">
                    <span>2. Customer Goodwill Notification Draft</span>
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-500/30">+ R$ 20.00 Voucher</span>
                  </div>
                  <p className="text-[11px] text-[#cbd5e1] mt-1 italic bg-[#0c121c] p-2 rounded border border-[#27354a]">
                    "{payload.draft_message || "Olá! Your order is being proactively expedited by our logistics team..."}"
                  </p>
                </div>
              </div>
            </div>

            {/* Decision Controls */}
            {isPending ? (
              <div className="bg-[#16202e] rounded-xl p-3.5 border border-[#27354a] space-y-3 shadow-md">
                <div>
                  <label className="text-[11px] font-medium text-[#cbd5e1] block mb-1">
                    Operations Supervisor Signature & Notes:
                  </label>
                  <input
                    type="text"
                    value={reviewerNotes}
                    onChange={(e) => setReviewerNotes(e.target.value)}
                    className="w-full text-xs px-3 py-2 rounded-lg bg-[#0c121c] border border-[#27354a] text-white focus:outline-none focus:border-[#0088cc]"
                    placeholder="Enter approval rationale or notes..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-2.5 pt-1">
                  <button
                    onClick={() => onSubmitDecision(activeIncident.incident_id, "APPROVED", reviewerNotes, reviewerName)}
                    disabled={isSubmitting}
                    className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#0088cc] to-[#0ea5e9] hover:brightness-110 text-white font-bold text-xs transition shadow-lg shadow-[#0088cc]/30 disabled:opacity-50"
                  >
                    <Check className="h-4 w-4" />
                    Approve & Execute
                  </button>

                  <button
                    onClick={() => onSubmitDecision(activeIncident.incident_id, "REJECTED", reviewerNotes, reviewerName)}
                    disabled={isSubmitting}
                    className="flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-[#0c121c] hover:bg-rose-950/40 text-rose-300 hover:text-rose-200 border border-rose-500/40 font-semibold text-xs transition disabled:opacity-50"
                  >
                    <X className="h-4 w-4" />
                    Reject Action
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-[#0c121c] rounded-xl p-3 border border-[#27354a] text-xs flex items-center justify-between text-[#94a3b8]">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  <span>Decided by: <strong className="text-white">{activeIncident.reviewer_notes || "Ops Supervisor"}</strong></span>
                </div>
                <span className="font-mono text-[10px] text-[#38bdf8] font-bold">{activeIncident.resolution_decision}</span>
              </div>
            )}
          </>
        )}

        {/* Immutable Audit Ledger */}
        <div className="space-y-2 pt-2 border-t border-[#27354a]">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase text-[#94a3b8] tracking-wider flex items-center gap-1.5">
              <History className="h-3.5 w-3.5 text-[#0088cc]" /> Action Execution Audit Ledger
            </span>
            <span className="text-[10px] font-mono text-[#64748b]">{auditLedger.length} Records</span>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {auditLedger.length === 0 ? (
              <p className="text-[11px] text-[#64748b] italic">No approved recovery actions recorded yet.</p>
            ) : (
              auditLedger.map((act) => (
                <div 
                  key={act.action_id}
                  className="bg-[#0c121c] rounded-lg p-2.5 border border-[#27354a] text-xs flex items-center justify-between shadow-xs"
                >
                  <div>
                    <div className="font-mono text-[10px] text-[#00b4d8] font-bold">{act.action_id}</div>
                    <div className="text-white text-[11px]">{act.action_type.replace(/_/g, " ")}</div>
                    <div className="text-[10px] text-[#64748b]">Sign-off: {act.approved_by}</div>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    act.status === "EXECUTED" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                  }`}>
                    {act.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
