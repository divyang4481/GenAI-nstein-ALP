import React from "react";
import { Package, AlertTriangle, UserCheck, CheckCircle2, DollarSign, Clock } from "lucide-react";

export default function MetricsRibbon({ metrics }) {
  const cards = [
    {
      title: "Orders Monitored",
      value: metrics?.total_orders_monitored || 12,
      subtitle: "Live Olist Lifecycle Stream",
      icon: Package,
      color: "text-[#38bdf8]",
      bg: "bg-[#0088cc]/15",
      border: "border-[#27354a]"
    },
    {
      title: "High Delivery Risks",
      value: metrics?.at_risk_orders || 6,
      subtitle: "Approaching SLA Deadlines",
      icon: AlertTriangle,
      color: "text-amber-400",
      bg: "bg-amber-500/15",
      border: "border-[#27354a]"
    },
    {
      title: "Pending Operations Approvals",
      value: metrics?.pending_human_approvals || 4,
      subtitle: "Human-in-the-Loop Queue",
      icon: UserCheck,
      color: "text-rose-400",
      bg: "bg-rose-500/15",
      border: "border-[#27354a]"
    },
    {
      title: "SLA Recovery Rate",
      value: `${metrics?.sla_recovery_rate_percent || 94.2}%`,
      subtitle: "Prevented Order Delays",
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/15",
      border: "border-[#27354a]"
    },
    {
      title: "Retained GMV Value",
      value: `R$ ${(metrics?.estimated_retention_roi_brl || 740.0).toFixed(2)}`,
      subtitle: "Protected Marketplace Revenue",
      icon: DollarSign,
      color: "text-[#00b4d8]",
      bg: "bg-[#00b4d8]/15",
      border: "border-[#27354a]"
    },
    {
      title: "Avg Agent Pipeline",
      value: `${metrics?.avg_agent_pipeline_duration_ms || 320} ms`,
      subtitle: "5-Agent Multi-Step Analysis",
      icon: Clock,
      color: "text-purple-400",
      bg: "bg-purple-500/15",
      border: "border-[#27354a]"
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5 my-3">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div 
            key={idx} 
            className={`glass-panel rounded-xl p-3.5 border ${c.border} bg-[#141c28] flex flex-col justify-between hover:border-[#0088cc]/60 transition shadow-md`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-medium uppercase tracking-wider text-[#94a3b8]">{c.title}</span>
              <div className={`p-1.5 rounded-lg ${c.bg}`}>
                <Icon className={`h-4 w-4 ${c.color}`} />
              </div>
            </div>
            <div>
              <div className="text-xl font-bold tracking-tight text-white">{c.value}</div>
              <div className="text-[11px] text-[#64748b] mt-0.5 truncate">{c.subtitle}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
