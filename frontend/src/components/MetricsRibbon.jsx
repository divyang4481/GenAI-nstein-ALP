import React from "react";
import { AlertTriangle, Clock3, UserCheck, CircleDollarSign } from "lucide-react";

export default function MetricsRibbon({ metrics }) {
  const items = [
    { label: "At-risk orders", value: metrics?.at_risk_orders ?? "—", note: "record count", icon: AlertTriangle, tone: "text-[#C4314B]", bg: "bg-rose-50" },
    { label: "Mean agent step", value: metrics ? `${metrics.avg_agent_step_duration_ms} ms` : "—", note: "measured", icon: Clock3, tone: "text-[#C68A00]", bg: "bg-amber-50" },
    { label: "Pending approvals", value: metrics?.pending_human_approvals ?? "—", note: "record count", icon: UserCheck, tone: "text-[#0F6CBD]", bg: "bg-blue-50" },
    { label: "Approved value indicator", value: metrics ? `R$ ${metrics.estimated_retention_roi_brl.toLocaleString("pt-BR", {minimumFractionDigits: 2})}` : "—", note: "demo estimate", icon: CircleDollarSign, tone: "text-[#1A7F37]", bg: "bg-emerald-50" }
  ];
  return <div className="grid grid-cols-2 lg:grid-cols-4 bg-white border border-slate-200 rounded-xl divide-x divide-slate-200 shadow-sm overflow-hidden">{items.map(({label,value,note,icon:Icon,tone,bg})=><div key={label} className="p-4 flex items-center gap-3"><div className={`h-10 w-10 rounded-lg ${bg} ${tone} flex items-center justify-center`}><Icon className="h-5 w-5"/></div><div><p className="text-xs text-slate-500">{label}</p><div className="flex items-baseline gap-2"><strong className="text-xl text-slate-900 font-semibold">{value}</strong><span className="text-[11px] text-slate-500">{note}</span></div></div></div>)}</div>;
}
