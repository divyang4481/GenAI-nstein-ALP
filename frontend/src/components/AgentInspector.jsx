import React, { useState } from "react";
import { 
  Bot, 
  Terminal, 
  ChevronDown, 
  ChevronRight, 
  ShieldAlert, 
  FileText, 
  Scale, 
  Wrench, 
  CheckCircle2, 
  Cpu, 
  Clock, 
  Sparkles
} from "lucide-react";

export default function AgentInspector({ 
  selectedOrder, 
  activeIncident, 
  traces, 
  isInvestigating,
  onRunInvestigation 
}) {
  const [expandedTools, setExpandedTools] = useState({});

  const toggleToolExpand = (stepIndex) => {
    setExpandedTools((prev) => ({
      ...prev,
      [stepIndex]: !prev[stepIndex]
    }));
  };

  const getAgentIcon = (agentName) => {
    switch (agentName) {
      case "Delivery-Risk Agent":
        return <ShieldAlert className="h-4 w-4 text-rose-400" />;
      case "Evidence Agent":
        return <FileText className="h-4 w-4 text-[#38bdf8]" />;
      case "Policy & RAG Agent":
        return <Scale className="h-4 w-4 text-[#00b4d8]" />;
      case "Recovery Agent":
        return <Wrench className="h-4 w-4 text-amber-400" />;
      case "Enterprise Guardrail Agent":
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
      default:
        return <Bot className="h-4 w-4 text-[#0088cc]" />;
    }
  };

  return (
    <div className="rounded-xl flex flex-col min-h-[520px] overflow-hidden border border-slate-200 bg-white text-slate-800">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-white flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 rounded-lg bg-[#0088cc]/15 border border-[#0088cc]/30">
            <Cpu className="h-4 w-4 text-[#38bdf8]" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-900">AI Evidence & Audit Trail</h2>
            <p className="text-[11px] text-slate-500">Supporting evidence, reasoning and technical details</p>
          </div>
        </div>

        {selectedOrder && (
          <button
            onClick={() => onRunInvestigation(selectedOrder.order_id)}
            disabled={isInvestigating}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0088cc] hover:bg-[#0099e6] text-white text-xs font-semibold transition disabled:opacity-50 shadow-md shadow-[#0088cc]/30"
          >
            <Sparkles className={`h-3.5 w-3.5 ${isInvestigating ? 'animate-spin' : ''}`} />
            {isInvestigating ? "Agents Investigating..." : "Run Multi-Agent Cycle"}
          </button>
        )}
      </div>

      {/* Main Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
        {!selectedOrder ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-[#64748b]">
            <Bot className="h-10 w-10 mb-2 opacity-40" />
            <p className="text-xs">Select an order or incident from the event stream to inspect agent reasoning traces.</p>
          </div>
        ) : traces.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-[#64748b]">
            <Bot className="h-10 w-10 mb-2 text-[#38bdf8] animate-bounce" />
            <h3 className="text-sm font-semibold text-[#cbd5e1] mb-1">Ready for Autonomous Investigation</h3>
            <p className="text-xs max-w-sm mb-4">Click "Run Multi-Agent Cycle" to dispatch Risk, Evidence, Policy, Recovery, and Guardrail agents.</p>
            <button
              onClick={() => onRunInvestigation(selectedOrder.order_id)}
              className="px-4 py-2 rounded-xl bg-[#0088cc] hover:bg-[#0099e6] text-white text-xs font-bold transition shadow-lg shadow-[#0088cc]/30"
            >
              Start Agent Investigation
            </button>
          </div>
        ) : (
          traces.map((trace, idx) => {
            const isToolOpen = expandedTools[trace.step_index];
            return (
              <div 
                key={idx}
                className="bg-[#16202e] rounded-xl border border-[#27354a] p-3.5 space-y-2.5 transition-all hover:border-[#0088cc]/50 shadow-sm"
              >
                {/* Agent Title Row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="p-1 rounded-md bg-[#0c121c] border border-[#27354a]">
                      {getAgentIcon(trace.agent_name)}
                    </div>
                    <span className="text-xs font-bold text-white">
                      Step {trace.step_index}: {trace.agent_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#94a3b8]">
                    <Clock className="h-3 w-3 text-[#64748b]" />
                    <span>{trace.latency_ms || 45}ms</span>
                  </div>
                </div>

                {/* Agent Thought / Reasoning */}
                <div className="text-xs text-[#cbd5e1] bg-[#0c121c] rounded-lg p-2.5 border border-[#27354a] leading-relaxed">
                  <span className="text-[10px] font-mono text-[#38bdf8] uppercase tracking-wider block mb-1 font-semibold">
                    🧠 Agent Thought & Reasoning:
                  </span>
                  {trace.thought}
                </div>

                {/* MCP Tool Call Section */}
                {trace.tool_name && (
                  <div className="rounded-lg border border-[#27354a] bg-[#0c121c] overflow-hidden text-xs">
                    <button
                      onClick={() => toggleToolExpand(trace.step_index)}
                      className="w-full px-2.5 py-1.5 flex items-center justify-between text-[11px] font-mono text-[#94a3b8] hover:text-white hover:bg-[#16202e] transition"
                    >
                      <span className="flex items-center gap-1.5">
                        <Terminal className="h-3 w-3 text-[#00b4d8]" />
                        <span>MCP Tool Call: <strong className="text-[#38bdf8]">{trace.tool_name}</strong></span>
                      </span>
                      {isToolOpen ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
                    </button>

                    {isToolOpen && (
                      <div className="p-2.5 bg-[#080d14] border-t border-[#27354a] space-y-2 text-[11px] font-mono">
                        <div>
                          <span className="text-[#64748b] text-[10px] block">Input Parameters:</span>
                          <pre className="text-emerald-400 bg-[#0c121c] p-2 rounded overflow-x-auto text-[10px] border border-[#27354a]">
                            {JSON.stringify(trace.tool_input, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <span className="text-[#64748b] text-[10px] block">Tool Return Payload:</span>
                          <pre className="text-[#38bdf8] bg-[#0c121c] p-2 rounded overflow-x-auto text-[10px] border border-[#27354a]">
                            {JSON.stringify(trace.tool_output, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Guardrail Status Badge */}
                {trace.agent_name === "Enterprise Guardrail Agent" && (
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400 bg-emerald-950/30 border border-emerald-500/30 px-2.5 py-1.5 rounded-lg">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Guardrail Status: PASSED (Zero Unauthorized Action Violations)</span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
