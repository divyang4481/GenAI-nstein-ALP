import React, { useState } from "react";
import { ArrowRight, Check, CheckCircle2, CircleAlert, FileText, History, MapPin, MessageSquareText, ShieldCheck, Sparkles, Truck, UserRoundCheck, X, ArrowUpRight } from "lucide-react";
import AgentInspector from "./AgentInspector";
import { askCase } from "../services/api";

export default function CaseWorkspace({ order, incident, traces, isInvestigating, onInvestigate, onDecision, isSubmitting, auditLedger }) {
  const [tab, setTab] = useState("case");
  const [notes, setNotes] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [askError, setAskError] = useState("");
  const [asking, setAsking] = useState(false);
  const ask = async (value=question) => { setAsking(true); setAskError(""); try { setAnswer(await askCase(order.order_id,value)); setQuestion(value); } catch(e) { setAskError(e.message); } finally { setAsking(false); } };
  if (!order) return <section className="bg-white rounded-xl border border-slate-200 flex items-center justify-center min-h-[650px] text-slate-500">Select an order to review its fulfilment case.</section>;
  const score=Math.round((order.risk_score||0)*100);
  const isApproved = incident?.status === "APPROVED_FOR_EXECUTION" || incident?.status === "APPROVED" || incident?.resolution_decision === "APPROVED";
  const isRejected = incident?.status === "REJECTED" || incident?.resolution_decision === "REJECTED";
  const pending = !isApproved && !isRejected && incident?.status === "PENDING_REVIEW";
  const recommendation=incident?.recommended_action || "Run risk analysis to generate an evidence-based recovery recommendation.";
  const voucher=incident?.proposed_payload?.proposed_voucher_brl;
  const slaDate=order.order_estimated_delivery_date ? new Date(order.order_estimated_delivery_date) : null;
  const slaRemaining=slaDate && !Number.isNaN(slaDate.valueOf()) ? `${Math.max(0, Math.round((slaDate-Date.now())/3600000))}h` : "Not available";
  const caseAudit = auditLedger.filter(a => a.order_id === order.order_id);
  return <section className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden h-[calc(100vh-184px)] min-h-[650px] flex flex-col">
    <div className="px-6 pt-5 border-b border-slate-200">
      <div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2"><span className="text-xs font-medium text-[#C4314B] bg-rose-50 px-2 py-1 rounded-md">Critical risk</span><span className="text-xs text-slate-500">Case RF-{order.order_id.slice(0,6).toUpperCase()}</span></div><h2 className="text-2xl font-semibold text-slate-900 mt-2">Order {order.order_id.slice(0,12).toUpperCase()}</h2><div className="flex flex-wrap items-center gap-2 mt-2 text-sm text-slate-600"><MapPin className="h-4 w-4"/>{order.seller_city}, {order.seller_state}<ArrowRight className="h-4 w-4 text-slate-400"/>{order.customer_city}, {order.customer_state}<span className="text-slate-300">|</span><span>{order.carrier_name}</span></div></div>
        <div className="grid grid-cols-3 divide-x divide-slate-200 border border-slate-200 rounded-lg min-w-[360px]"><div className="p-3"><p className="text-[11px] text-slate-500">Risk score</p><strong className="text-lg text-[#C4314B]">{score}%</strong></div><div className="p-3"><p className="text-[11px] text-slate-500">SLA remaining</p><strong className="text-lg text-slate-900">{slaRemaining}</strong></div><div className="p-3"><p className="text-[11px] text-slate-500">Order value</p><strong className="text-lg text-slate-900">R$ {order.price.toFixed(2)}</strong></div></div></div>
      <nav className="flex gap-6 mt-5">{[["case","Case overview"],["evidence","AI evidence & trace"],["ask","Ask this case"],["audit","Audit history"]].map(([v,l])=><button key={v} onClick={()=>setTab(v)} className={`pb-3 text-xs font-medium border-b-2 ${tab===v?"border-[#0F6CBD] text-[#0F6CBD]":"border-transparent text-slate-500"}`}>{l}{v==="evidence"&&traces.length>0?` (${traces.length})`:v==="audit"&&caseAudit.length>0?` (${caseAudit.length})`:""}</button>)}</nav>
    </div>
    <div className="flex-1 overflow-auto bg-[#F8FAFC] p-6">
      {tab==="case" && <div className="grid xl:grid-cols-[1fr_360px] gap-5">
        <div className="space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <CircleAlert className="h-4 w-4 text-[#C4314B]"/>Why this order is at risk
            </h3>
            <div className="grid md:grid-cols-3 gap-3 mt-4">
              {[
                [
                  "Risk root cause",
                  incident?.primary_risk_factor || (incident ? "Interstate transit delay" : "Pending AI investigation"),
                  incident ? "Evidence synthesized by 5-Agent team" : "Click 'Run risk analysis' to evaluate"
                ],
                [
                  "Transit route",
                  `${order.seller_city}, ${order.seller_state}`,
                  `${order.carrier_name} to ${order.customer_city}`
                ],
                [
                  "SLA exposure",
                  slaRemaining,
                  order.order_estimated_delivery_date || "No estimated date"
                ]
              ].map(([a,b,c])=><div key={a} className="border border-slate-200 rounded-lg p-3"><p className="text-[11px] text-slate-500">{a}</p><p className="text-sm font-semibold text-slate-900 mt-1">{b}</p><p className="text-[11px] text-slate-500 mt-1">{c}</p></div>)}
            </div>
            {incident?.evidence_summary && (
              <div className="mt-3 p-3 bg-slate-50/80 rounded-lg border border-slate-200 text-xs text-slate-700">
                <span className="font-semibold text-slate-900">AI Evidence Summary: </span>
                {incident.evidence_summary}
              </div>
            )}
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-[#0F6CBD]"/>Recommended recovery plan
              </h3>
              <span className="text-[11px] text-slate-500">{incident ? "AI generated · human controlled" : "Awaiting agent execution"}</span>
            </div>
            {incident ? (
              <>
                <p className="text-sm text-slate-700 mt-3 font-medium leading-relaxed">{incident.recommended_action}</p>
                <div className="mt-4 divide-y divide-slate-100 border-y border-slate-100">
                  {[
                    [Truck, incident.proposed_action_type?.replaceAll("_", " ") || "Carrier priority escalation", isApproved ? "Executed" : "Ready for review"],
                    [MessageSquareText, incident.proposed_payload?.customer_message?.message_body ? "Proactive customer notification draft" : "Prepare proactive customer update", "Draft only"],
                    [FileText, voucher != null && voucher > 0 ? `Issue R$ ${Number(voucher).toFixed(2)} goodwill voucher` : "No voucher proposed", isApproved ? "Approved in Ledger" : "Requires approval"]
                  ].map(([Icon, a, b]) => (
                    <div key={a} className="flex items-center gap-3 py-3">
                      <div className="h-8 w-8 rounded-lg bg-blue-50 text-[#0F6CBD] flex items-center justify-center">
                        <Icon className="h-4 w-4"/>
                      </div>
                      <span className="text-sm text-slate-800 flex-1 font-medium">{a}</span>
                      <span className={`text-[11px] px-2.5 py-1 rounded font-medium ${b === "Executed" || b === "Approved in Ledger" ? "bg-emerald-50 text-[#1A7F37] border border-emerald-200" : "bg-slate-100 text-slate-600"}`}>{b}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="mt-3 p-6 bg-slate-50/70 border border-dashed border-slate-200 rounded-lg text-center">
                <Sparkles className="h-6 w-6 text-slate-400 mx-auto mb-2"/>
                <p className="text-xs font-semibold text-slate-700">No recovery plan formulated yet</p>
                <p className="text-[11px] text-slate-500 mt-1 max-w-sm mx-auto">
                  Click <strong>"Run risk analysis"</strong> on the right to trigger the 5-agent investigation pipeline (Risk, Evidence, Policy RAG, Recovery, Guardrail).
                </p>
              </div>
            )}
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-5"><h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-[#1A7F37]"/>Safety checks</h3><div className="grid md:grid-cols-2 gap-3 mt-4">{(incident?.safety_checks || []).length ? incident.safety_checks.map(x=><div key={x.rule_name} className="flex items-start gap-2 text-xs text-slate-700">{x.status==="PASSED"?<CheckCircle2 className="h-4 w-4 text-[#1A7F37] shrink-0"/>:<CircleAlert className="h-4 w-4 text-rose-600 shrink-0"/>}<span><strong>{x.rule_name.replaceAll("_"," ")}</strong><br/>{x.description}</span></div>) : <p className="text-xs text-slate-500">Run the investigation to calculate deterministic safety checks.</p>}</div>{incident?.guardrail_status?.startsWith("BLOCKED")&&<p className="text-sm font-semibold text-rose-700 mt-4">Blocked — human review required.</p>}</div>
        </div>
        <aside className="bg-white border border-slate-200 rounded-xl p-5 h-fit sticky top-0">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-900">Decision</h3>
            {isApproved ? (
              <span className="text-[11px] px-2.5 py-1 bg-emerald-50 text-[#1A7F37] border border-emerald-200 font-semibold rounded flex items-center gap-1">
                <Check className="h-3 w-3"/> APPROVED
              </span>
            ) : isRejected ? (
              <span className="text-[11px] px-2.5 py-1 bg-rose-50 text-rose-700 border border-rose-200 font-semibold rounded flex items-center gap-1">
                <X className="h-3 w-3"/> REJECTED
              </span>
            ) : pending ? (
              <span className="text-[11px] px-2 py-1 bg-amber-50 text-[#9A6700] border border-amber-200 font-semibold rounded">
                PENDING REVIEW
              </span>
            ) : (
              <span className="text-[11px] px-2 py-1 bg-slate-100 text-slate-600 rounded">
                {incident?.status?.replaceAll("_"," ") || "UNANALYZED"}
              </span>
            )}
          </div>

          {isApproved ? (
            <div className="mt-3 space-y-3">
              <p className="text-xs text-slate-600">Recovery plan was authorised and recorded in the audit ledger.</p>
              <div className="bg-emerald-50/70 border border-emerald-100 rounded-lg p-3.5 text-xs space-y-2">
                <div className="flex justify-between items-center text-slate-700">
                  <span className="text-slate-500">Authorised by:</span>
                  <strong className="text-slate-900">Ops Specialist</strong>
                </div>
                <div className="flex justify-between items-center text-slate-700">
                  <span className="text-slate-500">Status:</span>
                  <span className="font-bold text-[#1A7F37]">APPROVED FOR EXECUTION</span>
                </div>
                {incident?.reviewer_notes && (
                  <div className="pt-2 border-t border-emerald-100 text-slate-600 italic">
                    "{incident.reviewer_notes}"
                  </div>
                )}
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-[#1A7F37] shrink-0"/>
                <span>Action dispatched to carrier & customer ledger.</span>
              </div>
              <button onClick={()=>onInvestigate(order.order_id)} disabled={isInvestigating} className="w-full mt-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg py-2 text-xs font-medium transition">
                {isInvestigating ? "Analysing case…" : "Re-evaluate case with AI"}
              </button>
            </div>
          ) : isRejected ? (
            <div className="mt-3 space-y-3">
              <p className="text-xs text-slate-600">Recovery plan was rejected by the operator.</p>
              <div className="bg-rose-50/70 border border-rose-100 rounded-lg p-3.5 text-xs space-y-2">
                <div className="flex justify-between items-center text-slate-700">
                  <span className="text-slate-500">Reviewed by:</span>
                  <strong className="text-slate-900">Ops Specialist</strong>
                </div>
                <div className="flex justify-between items-center text-slate-700">
                  <span className="text-slate-500">Status:</span>
                  <span className="font-bold text-rose-700">REJECTED</span>
                </div>
              </div>
              <button onClick={()=>onInvestigate(order.order_id)} disabled={isInvestigating} className="w-full mt-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg py-2 text-xs font-medium transition">
                {isInvestigating ? "Analysing case…" : "Re-run investigation"}
              </button>
            </div>
          ) : pending ? (
            <div className="mt-3">
              <p className="text-xs text-slate-500">Review the evidence and policy boundary before approving.</p>
              <label className="block text-xs font-medium text-slate-700 mt-4 mb-1.5">Decision notes</label>
              <textarea value={notes} onChange={e=>setNotes(e.target.value)} rows="3" placeholder="Add rationale for the audit trail…" className="w-full resize-none border border-slate-200 rounded-lg p-3 text-xs outline-none focus:border-[#0F6CBD]"/>
              <div className="space-y-2 mt-4">
                <button disabled={isSubmitting} onClick={()=>onDecision(incident.incident_id,"APPROVED",notes || "Verified and approved by Operations Supervisor.","Ops Specialist")} className="w-full bg-[#0F6CBD] hover:bg-[#0b5ca3] text-white rounded-lg py-2.5 text-sm font-semibold flex justify-center items-center gap-2 disabled:opacity-50">
                  <Check className="h-4 w-4"/>Approve recovery plan
                </button>
                <div className="grid grid-cols-2 gap-2">
                  <button onClick={()=>onDecision(incident.incident_id,"REJECTED",notes || "Rejected by operations reviewer.","Ops Specialist")} className="border border-slate-300 hover:bg-slate-50 rounded-lg py-2 text-xs font-medium text-slate-700 flex justify-center gap-1">
                    <X className="h-3.5 w-3.5"/>Reject
                  </button>
                  <button disabled title="Planned feature" className="border border-slate-300 rounded-lg py-2 text-xs font-medium text-slate-400 flex justify-center gap-1 cursor-not-allowed">
                    <ArrowUpRight className="h-3.5 w-3.5"/>Escalate · planned
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="mt-3">
              <p className="text-xs text-slate-500">No active recovery recommendation pending. Click below to trigger the 5-agent investigation cycle.</p>
              <button onClick={()=>onInvestigate(order.order_id)} disabled={isInvestigating} className="w-full mt-4 bg-[#0F6CBD] hover:bg-[#0b5ca3] text-white rounded-lg py-2.5 text-sm font-semibold">
                {isInvestigating?"Analysing case…":"Run risk analysis"}
              </button>
            </div>
          )}

          <div className="mt-5 pt-4 border-t border-slate-100 flex gap-2 text-[11px] text-slate-500">
            <UserRoundCheck className="h-4 w-4 shrink-0"/>
            <span>No action is executed until an authorised reviewer approves this plan.</span>
          </div>
        </aside>
      </div>}
      {tab==="evidence" && <AgentInspector selectedOrder={order} activeIncident={incident} traces={traces} isInvestigating={isInvestigating} onRunInvestigation={onInvestigate}/>} 
      {tab==="ask" && <div className="space-y-4"><div className="bg-white border border-slate-200 rounded-xl p-5"><div className="flex items-center justify-between"><h3 className="text-sm font-semibold">Ask this case</h3><span className="text-[11px] bg-slate-100 px-2 py-1 rounded">Read-only advisory</span></div>{answer&&<div className="mt-4 bg-blue-50 border border-blue-100 rounded-lg p-4"><div className="flex gap-2 mb-2"><span className={`text-[10px] px-2 py-1 rounded font-semibold ${answer.retrieval_quality==="GROUNDED"?"bg-emerald-100 text-emerald-800":"bg-amber-100 text-amber-800"}`}>{answer.retrieval_quality==="GROUNDED"?"Grounded answer":"Insufficient evidence"}</span><span className="text-[10px] px-2 py-1 rounded bg-white text-slate-600">{answer.execution_mode==="AWS_BEDROCK"?"Bedrock":"Demo fallback"}</span></div><p className="text-sm text-slate-800">{answer.answer}</p>{answer.retrieved_sources?.length>0&&<details className="mt-3"><summary className="text-xs font-semibold cursor-pointer">Sources used ({answer.retrieved_sources.length})</summary><div className="mt-2 space-y-2">{answer.retrieved_sources.map(s=><div key={s.chunk_id} className="bg-white border rounded p-3 text-xs"><strong>{s.title}</strong><p className="text-slate-500">{s.policy_id||s.case_id} · version {s.version} · score {s.score.toFixed(3)}</p><p className="mt-1 text-slate-600">{s.text_excerpt}</p></div>)}</div></details>}</div>}<div className="flex gap-2 mt-4"><input value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>e.key==="Enter"&&question&&ask()} placeholder="Ask about evidence, policy, or permitted actions" className="flex-1 border rounded-lg px-3 py-2 text-sm"/><button disabled={!question||asking} onClick={()=>ask()} className="bg-[#0F6CBD] text-white rounded-lg px-4 text-sm disabled:opacity-50">{asking?"Retrieving…":"Ask"}</button></div>{askError&&<p role="alert" className="text-sm text-rose-700 mt-2">{askError}</p>}</div><div className="flex flex-wrap gap-2">{["Why is this order at risk?","Which policy allows the voucher?","Can the customer be contacted automatically?","What evidence supports carrier escalation?"].map(q=><button key={q} onClick={()=>ask(q)} className="text-xs bg-white border border-slate-200 rounded-full px-3 py-2 hover:border-blue-400">{q}</button>)}</div></div>}
      {tab==="audit" && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <History className="h-4 w-4 text-[#0F6CBD]"/>Compliance Audit History
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">Immutable record of Human-in-the-Loop reviewer authorizations for this case</p>
            </div>
            <span className="text-[11px] bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md font-medium">
              PostgreSQL Action Ledger
            </span>
          </div>
          {caseAudit.length > 0 ? (
            <div className="space-y-3">
              {caseAudit.map(a => (
                <div key={a.action_id} className="border border-slate-200 rounded-lg p-4 bg-slate-50/60 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-900">{a.action_type.replaceAll("_", " ")}</span>
                      <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono">{a.action_id}</span>
                    </div>
                    <span className={`text-[11px] px-2 py-0.5 rounded font-semibold ${a.status === "APPROVED_FOR_EXECUTION" ? "bg-emerald-100 text-[#1A7F37]" : "bg-rose-100 text-rose-700"}`}>
                      {a.status.replaceAll("_", " ")}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 pt-1">
                    <div>
                      <span className="text-slate-400">Authorised by: </span>
                      <span className="font-medium text-slate-800">{a.approved_by || "Operations Specialist"}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Timestamp: </span>
                      <span className="font-mono text-[11px]">{a.executed_at ? new Date(a.executed_at).toLocaleString() : "Recently"}</span>
                    </div>
                  </div>
                  {a.notes && (
                    <div className="text-xs bg-white border border-slate-200 rounded p-2.5 text-slate-700 mt-2">
                      <span className="font-semibold text-slate-500 block text-[10px] uppercase tracking-wider">Reviewer Rationale</span>
                      "{a.notes}"
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-400">
              <History className="h-8 w-8 mx-auto text-slate-300 mb-2"/>
              <p className="font-medium text-slate-600">No human decisions recorded yet for this order</p>
              <p className="text-slate-400 mt-1 max-w-sm mx-auto">
                Trigger risk analysis, review the recovery plan, and click <strong>"Approve recovery plan"</strong> or <strong>"Reject"</strong> in the Case overview tab to record a permanent audit entry.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  </section>;
}
