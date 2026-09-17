import React, { useMemo, useState } from "react";
import { Search, SlidersHorizontal, ArrowDownUp, MapPin, Clock3, ChevronRight } from "lucide-react";

const urgency = (score) => score >= .9 ? "Critical" : score >= .7 ? "At risk" : "On track";

export default function LiveEventStream({ orders, selectedOrderId, onSelectOrder }) {
  const [filter, setFilter] = useState("RISK");
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => orders
    .filter(o => filter === "ALL" || o.is_at_risk)
    .filter(o => `${o.order_id} ${o.customer_city} ${o.seller_city}`.toLowerCase().includes(query.toLowerCase()))
    .sort((a,b)=>(b.risk_score||0)-(a.risk_score||0)), [orders, filter, query]);
  return <aside className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[calc(100vh-184px)] min-h-[650px]">
    <div className="p-4 border-b border-slate-200">
      <div className="flex items-center justify-between"><div><h2 className="text-sm font-semibold text-slate-900">Risk work queue</h2><p className="text-xs text-slate-500 mt-0.5">Prioritised by SLA and business impact</p></div><button className="p-2 border border-slate-200 rounded-lg text-slate-500"><SlidersHorizontal className="h-4 w-4"/></button></div>
      <div className="relative mt-3"><Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400"/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search queue" className="w-full pl-9 pr-3 py-2 text-xs rounded-lg bg-slate-50 border border-slate-200 outline-none focus:border-[#0F6CBD]"/></div>
      <div className="flex items-center justify-between mt-3"><div className="flex gap-1 bg-slate-100 rounded-lg p-1">{[["RISK","Needs attention"],["ALL","All orders"]].map(([v,l])=><button key={v} onClick={()=>setFilter(v)} className={`px-2.5 py-1 text-[11px] rounded-md ${filter===v?"bg-white text-slate-900 shadow-sm font-medium":"text-slate-500"}`}>{l}</button>)}</div><button className="flex items-center gap-1 text-[11px] text-slate-500"><ArrowDownUp className="h-3 w-3"/> Priority</button></div>
    </div>
    <div className="flex-1 overflow-auto divide-y divide-slate-100">
      {filtered.map((order, index)=>{ const score=Math.round((order.risk_score||0)*100), level=urgency(order.risk_score||0), selected=order.order_id===selectedOrderId; return <button key={order.order_id} onClick={()=>onSelectOrder(order.order_id)} className={`w-full text-left p-4 transition border-l-4 ${selected?"bg-blue-50/70 border-[#0F6CBD]":"bg-white border-transparent hover:bg-slate-50"}`}>
        <div className="flex justify-between gap-2"><div><div className="flex items-center gap-2"><span className={`h-2 w-2 rounded-full ${level==="Critical"?"bg-[#C4314B]":level==="At risk"?"bg-[#C68A00]":"bg-[#1A7F37]"}`}/><span className="text-xs font-semibold text-slate-900">Order {order.order_id.slice(0,8).toUpperCase()}</span></div><p className="text-[11px] text-slate-500 mt-1 ml-4">{order.product_category_name?.replaceAll("_"," ")}</p></div><div className="text-right"><span className={`text-[11px] font-semibold ${level==="Critical"?"text-[#C4314B]":"text-[#9A6700]"}`}>{score}% · {level}</span><p className="text-[11px] text-slate-500 mt-1">#{index+1}</p></div></div>
        <div className="flex items-center gap-1.5 mt-3 text-xs text-slate-600"><MapPin className="h-3.5 w-3.5 text-slate-400"/><span className="truncate">{order.seller_city}, {order.seller_state}</span><ChevronRight className="h-3 w-3 text-slate-400"/><span className="truncate">{order.customer_city}, {order.customer_state}</span></div>
        <div className="flex justify-between mt-3 text-[11px]"><span className={`flex items-center gap-1 font-medium ${level==="Critical"?"text-[#C4314B]":"text-[#9A6700]"}`}><Clock3 className="h-3.5 w-3.5"/>{level==="Critical"?"4h 12m":"17h 42m"} to SLA</span><span className="font-semibold text-slate-700">R$ {order.price?.toFixed(2)}</span></div>
      </button>})}
    </div>
  </aside>;
}
