import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import MetricsRibbon from "./components/MetricsRibbon";
import LiveEventStream from "./components/LiveEventStream";
import CaseWorkspace from "./components/CaseWorkspace";
import AwsArchitectureModal from "./components/AwsArchitectureModal";
import EvaluationModal from "./components/EvaluationModal";
import PolicyModal from "./components/PolicyModal";
import NeuroAiAlignmentModal from "./components/NeuroAiAlignmentModal";

import {
  fetchOrders,
  fetchIncidents,
  fetchIncidentDetails,
  fetchMetrics,
  fetchPolicies,
  fetchAuditLedger,
  submitDecision,
  triggerInvestigation,
  startReplay,
  pauseReplay,
  resetReplay,
  triggerNextEvent,
  setReplaySpeed,
  connectWebSocket
} from "./services/api";

export default function App() {
  const [orders, setOrders] = useState([]);
  const [events, setEvents] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [auditLedger, setAuditLedger] = useState([]);

  const [selectedOrderId, setSelectedOrderId] = useState(null);
  const [activeIncident, setActiveIncident] = useState(null);
  const [traces, setTraces] = useState([]);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState("");

  // Replay State
  const [isReplaying, setIsReplaying] = useState(false);
  const [currentSpeed, setCurrentSpeed] = useState(1.5);
  const [wsConnected, setWsConnected] = useState(false);

  // Modals
  const [isAwsModalOpen, setIsAwsModalOpen] = useState(false);
  const [isEvalModalOpen, setIsEvalModalOpen] = useState(false);
  const [isPolicyModalOpen, setIsPolicyModalOpen] = useState(false);
  const [isNeuroModalOpen, setIsNeuroModalOpen] = useState(false);

  // Initial Data Load
  const loadInitialData = async () => {
    try {
      const [ordersData, incidentsData, metricsData, policiesData, ledgerData] = await Promise.all([
        fetchOrders(),
        fetchIncidents(),
        fetchMetrics(),
        fetchPolicies(),
        fetchAuditLedger()
      ]);

      setOrders(ordersData);
      setIncidents(incidentsData);
      setMetrics(metricsData);
      setPolicies(policiesData);
      setAuditLedger(ledgerData);

      // Automatically select first high risk order if available
      const firstRisk = ordersData.find(o => o.is_at_risk) || ordersData[0];
      if (firstRisk) {
        setSelectedOrderId(firstRisk.order_id);
        const matchingIncident = incidentsData.find(i => i.order_id === firstRisk.order_id);
        if (matchingIncident) {
          loadIncidentDetails(matchingIncident.incident_id);
        }
      }
    } catch (err) {
      console.error("Failed to load initial data", err);
      setApiError(err.message || "Unable to load RetailFlow data.");
    }
  };

  const loadIncidentDetails = async (incidentId) => {
    try {
      const details = await fetchIncidentDetails(incidentId);
      setActiveIncident(details.incident);
      setTraces(details.traces);
    } catch (err) {
      console.error("Failed to load incident details", err);
      setApiError(err.message || "Unable to load incident details.");
    }
  };

  useEffect(() => {
    loadInitialData();

    // Setup WebSocket
    const ws = connectWebSocket(
      (data) => {
        handleWebSocketMessage(data);
      },
      () => setWsConnected(true),
      () => setWsConnected(false)
    );

    return () => {
      ws.close();
    };
  }, []);

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case "ORDER_EVENT_EMITTED":
        setEvents((prev) => [data.event, ...prev.slice(0, 49)]);
        break;

      case "AGENT_STEP_STARTED":
        setIsInvestigating(true);
        break;

      case "AGENT_STEP_COMPLETED":
        setTraces((prev) => {
          const exists = prev.some(t => t.step_index === data.trace.step_index);
          return exists ? prev : [...prev, data.trace];
        });
        break;

      case "INCIDENT_DISPATCHED_FOR_APPROVAL":
        setIsInvestigating(false);
        setActiveIncident(data.incident);
        setIncidents((prev) => [data.incident, ...prev.filter(i => i.incident_id !== data.incident.incident_id)]);
        fetchMetrics().then(setMetrics);
        break;

      case "HITL_DECISION_RECORDED":
        fetchIncidents().then(setIncidents);
        fetchAuditLedger().then(setAuditLedger);
        fetchMetrics().then(setMetrics);
        break;

      default:
        break;
    }
  };

  // Order selection handler
  const handleSelectOrder = (orderId) => {
    setSelectedOrderId(orderId);
    const inc = incidents.find(i => i.order_id === orderId);
    if (inc) {
      loadIncidentDetails(inc.incident_id);
    } else {
      setActiveIncident(null);
      setTraces([]);
    }
  };

  // Manual trigger of investigation
  const handleRunInvestigation = async (orderId) => {
    setIsInvestigating(true);
    setTraces([]);
    try {
      const res = await triggerInvestigation(orderId);
      if (res.traces) {
        setTraces(res.traces);
      }
      if (res.incident) {
        setActiveIncident(res.incident);
        setIncidents(prev => [res.incident, ...prev.filter(i => i.incident_id !== res.incident.incident_id && i.order_id !== res.incident.order_id)]);
      }
      const updatedMetrics = await fetchMetrics();
      setMetrics(updatedMetrics);
    } catch (e) {
      console.error("Investigation failed", e);
      setApiError(e.message || "Investigation failed.");
    } finally {
      setIsInvestigating(false);
    }
  };

  // Submit operations approval / rejection
  const handleSubmitDecision = async (incidentId, decision, reviewerNotes, reviewerName) => {
    setIsSubmitting(true);
    try {
      await submitDecision(incidentId, decision, reviewerNotes, reviewerName);
      if (activeIncident) {
        setActiveIncident(prev => ({
          ...prev,
          status: decision,
          resolution_decision: decision,
          reviewer_notes: reviewerNotes
        }));
      }
      const [updatedIncidents, updatedLedger, updatedMetrics] = await Promise.all([
        fetchIncidents(),
        fetchAuditLedger(),
        fetchMetrics()
      ]);
      setIncidents(updatedIncidents);
      setAuditLedger(updatedLedger);
      setMetrics(updatedMetrics);
    } catch (e) {
      console.error("Failed to submit decision", e);
      setApiError(e.message || "Decision could not be recorded.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Replay Handlers
  const handleStartReplay = async () => {
    await startReplay();
    setIsReplaying(true);
  };

  const handlePauseReplay = async () => {
    await pauseReplay();
    setIsReplaying(false);
  };

  const handleResetReplay = async () => {
    await resetReplay();
    setEvents([]);
    setIsReplaying(false);
    setActiveIncident(null);
    setTraces([]);
    await loadInitialData();
  };

  const handleTriggerNext = async () => {
    await triggerNextEvent();
  };

  const handleSetSpeed = async (speed) => {
    await setReplaySpeed(speed);
    setCurrentSpeed(speed);
  };

  const selectedOrder = orders.find(o => o.order_id === selectedOrderId);

  return (
    <div className="min-h-screen bg-[#F1F5F9] text-slate-900 flex flex-col selection:bg-blue-100 selection:text-blue-900">
      
      {/* Top Header & Replay Controls */}
      <Header
        isReplaying={isReplaying}
        onStartReplay={handleStartReplay}
        onPauseReplay={handlePauseReplay}
        onResetReplay={handleResetReplay}
        onTriggerNext={handleTriggerNext}
        onSetSpeed={handleSetSpeed}
        currentSpeed={currentSpeed}
        onOpenAwsModal={() => setIsAwsModalOpen(true)}
        onOpenEvalModal={() => setIsEvalModalOpen(true)}
        onOpenPolicyModal={() => setIsPolicyModalOpen(true)}
        onOpenNeuroModal={() => setIsNeuroModalOpen(true)}
        wsConnected={wsConnected}
      />
      <div className="h-7 bg-slate-900 text-slate-300 px-6 flex items-center text-[11px]" aria-live="polite">
        <span className="font-semibold text-sky-300 mr-2">LATEST EVENT</span>
        {events[0] ? `${events[0].timestamp} · ${events[0].event_type.replaceAll("_", " ")} · Order ${events[0].order_id.slice(0, 8).toUpperCase()}` : "Historical Olist event replay paused"}
      </div>
      {apiError && <div role="alert" className="bg-rose-50 border-b border-rose-200 text-rose-800 px-6 py-2 text-sm flex justify-between"><span><strong>API error:</strong> {apiError}</span><button onClick={()=>setApiError("")} aria-label="Dismiss error">×</button></div>}

      {/* Main Content Dashboard */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-6 py-5 flex flex-col space-y-4">
        
        {/* KPI Metrics Ribbon */}
        <MetricsRibbon metrics={metrics} />

        <div className="grid grid-cols-1 lg:grid-cols-[370px_minmax(0,1fr)] gap-4 flex-1">
          <div>
            <LiveEventStream
              orders={orders}
              events={events}
              selectedOrderId={selectedOrderId}
              onSelectOrder={handleSelectOrder}
              onInvestigate={handleRunInvestigation}
            />
          </div>

          <div>
            <CaseWorkspace
              order={selectedOrder}
              incident={activeIncident}
              traces={traces}
              isInvestigating={isInvestigating}
              onInvestigate={handleRunInvestigation}
              onDecision={handleSubmitDecision}
              isSubmitting={isSubmitting}
              auditLedger={auditLedger}
            />
          </div>
        </div>
      </main>

      {/* Modals */}
      <NeuroAiAlignmentModal
        isOpen={isNeuroModalOpen}
        onClose={() => setIsNeuroModalOpen(false)}
      />

      <AwsArchitectureModal
        isOpen={isAwsModalOpen}
        onClose={() => setIsAwsModalOpen(false)}
      />

      <EvaluationModal
        isOpen={isEvalModalOpen}
        onClose={() => setIsEvalModalOpen(false)}
      />

      <PolicyModal
        isOpen={isPolicyModalOpen}
        onClose={() => setIsPolicyModalOpen(false)}
        policies={policies}
      />

    </div>
  );
}
