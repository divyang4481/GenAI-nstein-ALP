import React, { useState } from "react";
import { X, BarChart3, RefreshCw, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";
import { runBenchmark } from "../services/api";

export default function EvaluationModal({ isOpen, onClose }) {
  const [evalResults, setEvalResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  if (!isOpen) return null;

  const handleRunEvaluation = async () => {
    setIsRunning(true);
    try {
      const data = await runBenchmark();
      setEvalResults(data);
    } catch (e) {
      console.error("Evaluation failed", e);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="glass-panel-elevated rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col border border-slate-700 shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-400">
              <BarChart3 className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">LLM Evaluation & Guardrail Benchmark</h2>
              <p className="text-xs text-slate-400">Auditable Ground-Truth Test on Historical Olist Fulfillment Records</p>
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
          <div className="flex items-center justify-between bg-slate-900/80 p-4 rounded-xl border border-slate-800">
            <div>
              <div className="text-xs font-bold text-slate-200">Ground Truth Test Suite</div>
              <p className="text-[11px] text-slate-400">Evaluates Risk Classification Precision, Recall, and Policy Guardrail Compliance.</p>
            </div>
            <button
              onClick={handleRunEvaluation}
              disabled={isRunning}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRunning ? 'animate-spin' : ''}`} />
              {isRunning ? "Running Benchmark..." : "Run Evaluation Benchmark"}
            </button>
          </div>

          {evalResults ? (
            <div className="space-y-4">
              {/* Metric KPI Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="bg-slate-900 p-3 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] uppercase text-slate-400 font-semibold">Precision</span>
                  <div className="text-xl font-bold text-emerald-400 mt-1">{(evalResults.metrics.precision * 100).toFixed(1)}%</div>
                </div>
                <div className="bg-slate-900 p-3 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] uppercase text-slate-400 font-semibold">Recall</span>
                  <div className="text-xl font-bold text-cyan-400 mt-1">{(evalResults.metrics.recall * 100).toFixed(1)}%</div>
                </div>
                <div className="bg-slate-900 p-3 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] uppercase text-slate-400 font-semibold">F1-Score</span>
                  <div className="text-xl font-bold text-purple-400 mt-1">{evalResults.metrics.f1_score.toFixed(3)}</div>
                </div>
                <div className="bg-slate-900 p-3 rounded-xl border border-slate-800 text-center">
                  <span className="text-[10px] uppercase text-slate-400 font-semibold">Guardrail Compliance</span>
                  <div className="text-xl font-bold text-emerald-400 mt-1">{evalResults.metrics.guardrail_compliance_rate_percent}%</div>
                </div>
              </div>

              {/* Confusion Matrix */}
              <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 text-xs">
                <div className="text-xs font-bold text-slate-200 mb-2">Confusion Matrix Breakdown:</div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                  <div className="p-2 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
                    True Positives (At-Risk Correct): <strong>{evalResults.confusion_matrix.true_positives}</strong>
                  </div>
                  <div className="p-2 rounded bg-blue-950/40 border border-blue-500/30 text-blue-300">
                    True Negatives (On-Time Correct): <strong>{evalResults.confusion_matrix.true_negatives}</strong>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-400">
                    False Positives: <strong>{evalResults.confusion_matrix.false_positives}</strong>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800 text-slate-400">
                    False Negatives: <strong>{evalResults.confusion_matrix.false_negatives}</strong>
                  </div>
                </div>
              </div>

              {/* Case breakdown list */}
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {evalResults.cases.map((c, idx) => (
                  <div key={idx} className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 text-xs flex items-center justify-between font-mono">
                    <span className="text-slate-300">{c.order_id.slice(0, 10)}...</span>
                    <span className="text-purple-400">{c.classification}</span>
                    <span className="text-emerald-400 flex items-center gap-1">
                      <ShieldCheck className="h-3 w-3" /> Guardrail Passed
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs">
              Click "Run Evaluation Benchmark" to trigger automated testing against Olist ground-truth datasets.
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
}
