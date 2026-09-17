import React, { useMemo, useState } from "react";
import { Search, SlidersHorizontal, ArrowDownUp, MapPin, Clock3, ChevronRight, CheckCircle2 } from "lucide-react";

const urgency = (score) => score >= .9 ? "Critical" : score >= .7 ? "At risk" : "On track";

export default function LiveEventStream({ orders = [], incidents = [], selectedOrderId, onSelectOrder }) {
  const [filter, setFilter] = useState("RISK");
  const [query, setQuery] = useState("");

  const incidentMap = useMemo(() => {
    const map = {};
    for (const inc of incidents) {
      if (inc.order_id && !map[inc.order_id]) {
        map[inc.order_id] = inc;
      }
    }
    return map;
  }, [incidents]);

  const stats = useMemo(() => {
    let needsAttention = 0;
    let approved = 0;
    for (const o of orders) {
      const inc = incidentMap[o.order_id];
      const isApproved = inc?.status === "APPROVED_FOR_EXECUTION" || inc?.status === "APPROVED" || inc?.resolution_decision === "APPROVED";
      if (isApproved) {
        approved += 1;
      } else if (o.is_at_risk || inc?.status === "PENDING_REVIEW") {
        needsAttention += 1;
      }
    }
    return { needsAttention, approved, all: orders.length };
  }, [orders, incidentMap]);

  const filtered = useMemo(() => orders
    .filter(o => {
      const inc = incidentMap[o.order_id];
      const isApproved = inc?.status === "APPROVED_FOR_EXECUTION" || inc?.status === "APPROVED" || inc?.resolution_decision === "APPROVED";
      
      if (filter === "APPROVED") {
        return isApproved;
      }
      if (filter === "RISK") {
        return (o.is_at_risk || inc?.status === "PENDING_REVIEW") && !isApproved;
      }
      return true; // "ALL"
    })
    .filter(o => `${o.order_id} ${o.customer_city} ${o.seller_city} ${o.product_category_name || ""}`.toLowerCase().includes(query.toLowerCase()))
    .sort((a,b)=>(b.risk_score||0)-(a.risk_score||0)), [orders, filter, query, incidentMap]);

  return <aside className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[calc(100vh-184px)] min-h-[650px]">
    <div className="p-4 border-b border-slate-200">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Risk work queue</h2>
          <p className="text-xs text-slate-500 mt-0.5">Prioritised by SLA and resolution status</p>
        </div>
        <button className="p-2 border border-slate-200 rounded-lg text-slate-500 hover:bg-slate-50">
          <SlidersHorizontal className="h-4 w-4"/>
        </button>
      </div>
      <div className="relative mt-3">
        <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400"/>
        <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search queue by order, city, category…" className="w-full pl-9 pr-3 py-2 text-xs rounded-lg bg-slate-50 border border-slate-200 outline-none focus:border-[#0F6CBD]"/>
      </div>
      <div className="flex items-center justify-between mt-3">
        <div className="flex gap-1 bg-slate-100 rounded-lg p-1">
          {[
            ["RISK", `Needs attention (${stats.needsAttention})`],
            ["APPROVED", `Approved (${stats.approved})`],
            ["ALL", `All (${stats.all})`]
          ].map(([v, l]) => (
            <button
              key={v}
              onClick={() => setFilter(v)}
              className={`px-2.5 py-1 text-[11px] rounded-md transition ${filter === v ? "bg-white text-slate-900 shadow-sm font-semibold" : "text-slate-500 hover:text-slate-800"}`}
            >
              {l}
            </button>
          ))}
        </div>
        <button className="flex items-center gap-1 text-[11px] text-slate-500">
          <ArrowDownUp className="h-3 w-3"/> Priority
        </button>
      </div>
    </div>
    <div className="flex-1 overflow-auto divide-y divide-slate-100">
      {filtered.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-400">
          {filter === "APPROVED" ? "No approved orders in this queue yet." : filter === "RISK" ? "All high-risk orders have been resolved!" : "No orders match your filter."}
        </div>
      ) : (
        filtered.map((order, index) => {
          const score = Math.round((order.risk_score || 0) * 100);
          const level = urgency(order.risk_score || 0);
          const selected = order.order_id === selectedOrderId;
          const inc = incidentMap[order.order_id];
          const isApproved = inc?.status === "APPROVED_FOR_EXECUTION" || inc?.status === "APPROVED" || inc?.resolution_decision === "APPROVED";
          const isPending = inc?.status === "PENDING_REVIEW";

          return (
            <button
              key={order.order_id}
              onClick={() => onSelectOrder(order.order_id)}
              className={`w-full text-left p-4 transition border-l-4 ${selected ? "bg-blue-50/70 border-[#0F6CBD]" : "bg-white border-transparent hover:bg-slate-50"}`}
            >
              <div className="flex justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    {isApproved ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-[#1A7F37] shrink-0" />
                    ) : (
                      <span className={`h-2 w-2 rounded-full ${level === "Critical" ? "bg-[#C4314B]" : level === "At risk" ? "bg-[#C68A00]" : "bg-[#1A7F37]"}`} />
                    )}
                    <span className="text-xs font-semibold text-slate-900">
                      Order {order.order_id.slice(0, 8).toUpperCase()}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1 ml-5">
                    {order.product_category_name?.replaceAll("_", " ") || "General merchandise"}
                  </p>
                </div>
                <div className="text-right">
                  {isApproved ? (
                    <span className="text-[10px] font-semibold text-[#1A7F37] bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      ✓ Approved
                    </span>
                  ) : isPending ? (
                    <span className="text-[10px] font-semibold text-[#9A6700] bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                      Pending review
                    </span>
                  ) : (
                    <span className={`text-[11px] font-semibold ${level === "Critical" ? "text-[#C4314B]" : "text-[#9A6700]"}`}>
                      {score}% · {level}
                    </span>
                  )}
                  <p className="text-[11px] text-slate-400 mt-1">#{index + 1}</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5 mt-3 text-xs text-slate-600">
                <MapPin className="h-3.5 w-3.5 text-slate-400"/>
                <span className="truncate">{order.seller_city}, {order.seller_state}</span>
                <ChevronRight className="h-3 w-3 text-slate-400"/>
                <span className="truncate">{order.customer_city}, {order.customer_state}</span>
              </div>
              <div className="flex justify-between mt-3 text-[11px]">
                <span className={`flex items-center gap-1 font-medium ${isApproved ? "text-[#1A7F37]" : level === "Critical" ? "text-[#C4314B]" : "text-[#9A6700]"}`}>
                  <Clock3 className="h-3.5 w-3.5"/>
                  {isApproved ? "Action Executed" : level === "Critical" ? "4h 12m to SLA" : "17h 42m to SLA"}
                </span>
                <span className="font-semibold text-slate-700">R$ {order.price?.toFixed(2)}</span>
              </div>
            </button>
          );
        })
      )}
    </div>
  </aside>;
}
