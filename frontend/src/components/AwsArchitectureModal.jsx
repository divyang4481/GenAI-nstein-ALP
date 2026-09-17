import React from "react";
import { X, Cloud, ArrowRight, Server, Database, Zap, Cpu, Shield, Layers } from "lucide-react";

export default function AwsArchitectureModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const architectureMapping = [
    {
      domain: "Event Stream Replay",
      local: "Async Event Replay Engine (Python FastAPI Generator)",
      aws: "Amazon Kinesis Data Streams / Amazon MSK",
      icon: Zap,
      benefit: "High-throughput real-time ingestion of millions of marketplace fulfillment lifecycle events."
    },
    {
      domain: "Application Backend",
      local: "FastAPI Async Web Server (Python 3.11)",
      aws: "AWS ECS Fargate / AWS Lambda Container Runtime",
      icon: Server,
      benefit: "Auto-scaling serverless container compute with zero operational overhead."
    },
    {
      domain: "Agentic AI & LLMs",
      local: "Multi-Agent Engine (Risk, Evidence, Policy, Recovery, Guardrails)",
      aws: "Amazon Bedrock (Claude 3.5 Sonnet / Titan Text Express)",
      icon: Cpu,
      benefit: "Enterprise-grade foundational models with strict data privacy and prompt routing."
    },
    {
      domain: "Real-Time Dashboard Comms",
      local: "FastAPI WebSocket Manager",
      aws: "Amazon API Gateway WebSocket API",
      icon: Layers,
      benefit: "Managed persistent duplex connections broadcasting agent thoughts to operations consoles."
    },
    {
      domain: "Relational State Store",
      local: "SQLite (Orders, Incidents, Policies, Playbooks)",
      aws: "Amazon RDS (PostgreSQL Multi-AZ)",
      icon: Database,
      benefit: "ACID compliance for order tracking, SLA configurations, and operations state."
    },
    {
      domain: "Audit Ledger & Guardrails",
      local: "Action Ledger Model & Step Traces",
      aws: "Amazon DynamoDB + Amazon CloudWatch Logs",
      icon: Shield,
      benefit: "Immutable, single-digit millisecond latency ledger for compliance and post-mortem analysis."
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="glass-panel-elevated rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col border border-slate-700 shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-400">
              <Cloud className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">AWS Production Enterprise Architecture</h2>
              <p className="text-xs text-slate-400">RetailFlow Local MVP to AWS Cloud Production Topology Mapping</p>
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
          <div className="bg-indigo-950/30 border border-indigo-500/20 rounded-xl p-4 text-xs text-indigo-200 leading-relaxed">
            <strong>Architecture Rationale:</strong> RetailFlow is engineered to separate high-frequency live event ingestion from multi-agent reasoning. In AWS production, Amazon Kinesis buffers high-velocity order status events, while Amazon Bedrock executes goal-directed agents with strict IAM and Guardrail constraints.
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-2">
            {architectureMapping.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div key={idx} className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 text-xs space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-200 flex items-center gap-1.5">
                      <Icon className="h-3.5 w-3.5 text-cyan-400" />
                      {item.domain}
                    </span>
                  </div>

                  <div className="space-y-1.5 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 font-mono text-[11px]">
                    <div className="text-slate-400">
                      <span className="text-slate-500">Local MVP:</span> {item.local}
                    </div>
                    <div className="text-indigo-300 font-semibold flex items-center gap-1">
                      <ArrowRight className="h-3 w-3 text-cyan-400 shrink-0" />
                      <span className="text-cyan-400">AWS Cloud:</span> {item.aws}
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 italic">
                    {item.benefit}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition"
          >
            Close Architecture View
          </button>
        </div>

      </div>
    </div>
  );
}
