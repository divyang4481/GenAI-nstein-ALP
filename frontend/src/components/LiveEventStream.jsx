import React, { useState } from "react";
import { 
  Radio, 
  MapPin, 
  Truck, 
  Sparkles, 
  AlertOctagon, 
  CheckCircle, 
  Clock, 
  ArrowRight,
  Filter,
  Search
} from "lucide-react";

export default function LiveEventStream({ 
  orders, 
  events, 
  selectedOrderId, 
  onSelectOrder, 
  onInvestigate 
}) {
  const [filter, setFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredOrders = orders.filter((o) => {
    if (filter === "AT_RISK" && !o.is_at_risk) return false;
    if (filter === "IN_TRANSIT" && o.order_status !== "in_transit") return false;
    if (filter === "DELIVERED" && o.order_status !== "delivered") return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        o.order_id.toLowerCase().includes(q) ||
        o.product_category_name.toLowerCase().includes(q) ||
        o.customer_city.toLowerCase().includes(q) ||
        o.seller_city.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const getStatusBadge = (status, isAtRisk) => {
    if (isAtRisk) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40">
          <AlertOctagon className="h-3 w-3" /> SLA Risk High
        </span>
      );
    }
    switch (status) {
      case "delivered":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            <CheckCircle className="h-3 w-3" /> Delivered
          </span>
        );
      case "in_transit":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#0088cc]/20 text-[#38bdf8] border border-[#0088cc]/40">
            <Truck className="h-3 w-3" /> In Transit
          </span>
        );
      case "seller_dispatched":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            <Clock className="h-3 w-3" /> Dispatched
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#27354a] text-[#cbd5e1] border border-[#33445e]">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="glass-panel rounded-2xl flex flex-col h-[780px] overflow-hidden border border-[#27354a] bg-[#141c28]">
      
      {/* Header & Live Event Ticker */}
      <div className="p-4 border-b border-[#27354a] bg-[#0f1622]">
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center space-x-2">
            <Radio className="h-4 w-4 text-emerald-400 animate-pulse" />
            <h2 className="text-sm font-bold text-white tracking-wide uppercase">Live Event Stream</h2>
          </div>
          <span className="text-[11px] font-mono text-[#38bdf8] bg-[#0c121c] px-2 py-0.5 rounded border border-[#27354a]">
            {events.length} Events Replayed
          </span>
        </div>

        {/* Latest Event Banner */}
        {events.length > 0 && (
          <div className="bg-[#0c121c] rounded-xl p-2.5 border border-[#0088cc]/30 mb-3 text-xs flex items-center justify-between shadow-inner">
            <div className="flex items-center gap-2 truncate">
              <span className="font-mono text-[#00b4d8] font-bold">{events[0].timestamp}</span>
              <span className="text-[#475569]">•</span>
              <span className="font-semibold text-[#f1f5f9] capitalize">{events[0].event_type.replace(/_/g, " ")}</span>
              <span className="text-[#64748b] truncate">({events[0].order_id.slice(0, 8)}...)</span>
            </div>
            <div className="text-[10px] text-[#38bdf8] font-mono flex items-center gap-1 shrink-0 ml-2">
              <MapPin className="h-3 w-3 text-[#0088cc]" />
              {events[0].seller_state} → {events[0].customer_state}
            </div>
          </div>
        )}

        {/* Filters and Search */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="h-3.5 w-3.5 absolute left-2.5 top-2.5 text-[#64748b]" />
            <input
              type="text"
              placeholder="Search order, city, category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-[#0c121c] border border-[#27354a] text-[#f1f5f9] placeholder-[#64748b] focus:outline-none focus:border-[#0088cc]"
            />
          </div>
          <div className="flex rounded-lg bg-[#0c121c] p-0.5 border border-[#27354a] text-[11px]">
            {["ALL", "AT_RISK", "IN_TRANSIT"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-2 py-1 rounded font-medium transition ${
                  filter === f 
                    ? "bg-[#0088cc] text-white shadow-xs" 
                    : "text-[#94a3b8] hover:text-white"
                }`}
              >
                {f.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Orders List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {filteredOrders.map((order) => {
          const isSelected = selectedOrderId === order.order_id;
          const riskPercent = Math.round((order.risk_score || 0) * 100);

          return (
            <div
              key={order.order_id}
              onClick={() => onSelectOrder(order.order_id)}
              className={`p-3.5 rounded-xl transition-all cursor-pointer border text-xs ${
                isSelected
                  ? "bg-[#1c2738] border-[#0088cc] shadow-md shadow-[#0088cc]/20"
                  : order.is_at_risk
                  ? "bg-rose-950/15 border-rose-500/30 hover:border-rose-500/50"
                  : "bg-[#16202e] border-[#27354a] hover:border-[#38bdf8]/40"
              }`}
            >
              {/* Top row */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5 font-mono text-[#cbd5e1] font-bold">
                  <span>#{order.order_id.slice(0, 8)}...</span>
                  <span className="text-[#64748b] text-[10px]">({order.product_category_name.replace(/_/g, " ")})</span>
                </div>
                {getStatusBadge(order.order_status, order.is_at_risk)}
              </div>

              {/* Transit Corridor Route */}
              <div className="flex items-center justify-between text-[#94a3b8] mb-2.5 bg-[#0c121c] p-2 rounded-lg border border-[#27354a]">
                <div className="flex items-center gap-1 truncate">
                  <span className="font-semibold text-white">{order.seller_city}</span>
                  <span className="text-[10px] text-[#64748b]">[{order.seller_state}]</span>
                </div>
                <div className="flex items-center gap-1 text-[#475569] px-1">
                  <span className="h-0.5 w-3 bg-[#27354a]"></span>
                  <Truck className="h-3 w-3 text-[#38bdf8]" />
                  <span className="h-0.5 w-3 bg-[#27354a]"></span>
                </div>
                <div className="flex items-center gap-1 truncate text-right">
                  <span className="font-semibold text-white">{order.customer_city}</span>
                  <span className="text-[10px] text-[#64748b]">[{order.customer_state}]</span>
                </div>
              </div>

              {/* Financials & Risk Meter */}
              <div className="flex items-center justify-between text-[11px] text-[#94a3b8]">
                <div>
                  <span className="text-[#64748b]">Value:</span>{" "}
                  <span className="font-mono text-white font-semibold">R$ {order.price.toFixed(2)}</span>
                  <span className="text-[#475569] ml-1">(+R${order.freight_value.toFixed(2)})</span>
                </div>

                {order.is_at_risk ? (
                  <div className="flex items-center gap-1.5">
                    <span className="text-rose-400 font-bold">{riskPercent}% Risk</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onInvestigate(order.order_id);
                      }}
                      className="flex items-center gap-1 px-2.5 py-1 rounded bg-gradient-to-r from-[#0088cc] to-[#0ea5e9] text-white font-semibold text-[10px] hover:brightness-110 transition shadow-xs"
                    >
                      <Sparkles className="h-2.5 w-2.5" /> Investigate
                    </button>
                  </div>
                ) : (
                  <div className="text-[#64748b] font-mono">Carrier: {order.carrier_name}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
