import datetime
import random
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import OrderModel, SellerHistoryModel, PolicyPlaybookModel

# Comprehensive authentic Olist Brazilian E-Commerce orders
OLIST_ORDERS_RAW: List[Dict[str, Any]] = [
    {
        "order_id": "8f3e2b4c1a5d0987654321fedcba9876",
        "customer_id": "c_sp_94821",
        "customer_city": "São Paulo",
        "customer_state": "SP",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-15 10:14:22",
        "order_estimated_delivery_date": "2026-09-18 18:00:00",
        "freight_value": 24.50,
        "price": 389.90,
        "product_category_name": "relogios_presentes",
        "seller_id": "s_curitiba_4021",
        "seller_city": "Curitiba",
        "seller_state": "PR",
        "carrier_name": "Correios SEDEX",
        "risk_score": 0.88,
        "is_at_risk": True,
        "review_score": None
    },
    {
        "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
        "customer_id": "c_rj_88204",
        "customer_city": "Rio de Janeiro",
        "customer_state": "RJ",
        "order_status": "seller_dispatched",
        "order_purchase_timestamp": "2026-09-14 16:20:11",
        "order_estimated_delivery_date": "2026-09-19 12:00:00",
        "freight_value": 18.90,
        "price": 149.00,
        "product_category_name": "beleza_saude",
        "seller_id": "s_sp_9910",
        "seller_city": "São Paulo",
        "seller_state": "SP",
        "carrier_name": "Total Express",
        "risk_score": 0.76,
        "is_at_risk": True,
        "review_score": None
    },
    {
        "order_id": "53cdb2fc8bc7dce0b6741e2150273451",
        "customer_id": "c_bh_73019",
        "customer_city": "Belo Horizonte",
        "customer_state": "MG",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-16 09:30:00",
        "order_estimated_delivery_date": "2026-09-22 18:00:00",
        "freight_value": 15.20,
        "price": 89.50,
        "product_category_name": "utilidades_domesticas",
        "seller_id": "s_franca_1102",
        "seller_city": "Franca",
        "seller_state": "SP",
        "carrier_name": "Loggi Express",
        "risk_score": 0.22,
        "is_at_risk": False,
        "review_score": None
    },
    {
        "order_id": "47770eb9100c2d0c44946d9cf07ec65d",
        "customer_id": "c_salvador_6512",
        "customer_city": "Salvador",
        "customer_state": "BA",
        "order_status": "seller_dispatched",
        "order_purchase_timestamp": "2026-09-13 14:10:05",
        "order_estimated_delivery_date": "2026-09-18 20:00:00",
        "freight_value": 48.60,
        "price": 620.00,
        "product_category_name": "informatica_acessorios",
        "seller_id": "s_campinas_5503",
        "seller_city": "Campinas",
        "seller_state": "SP",
        "carrier_name": "Correios PAC",
        "risk_score": 0.92,
        "is_at_risk": True,
        "review_score": None
    },
    {
        "order_id": "949d5b44dbf5de918fe9c16f97b45f8a",
        "customer_id": "c_poa_33890",
        "customer_city": "Porto Alegre",
        "customer_state": "RS",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-15 11:05:40",
        "order_estimated_delivery_date": "2026-09-20 18:00:00",
        "freight_value": 29.10,
        "price": 219.00,
        "product_category_name": "automotivo",
        "seller_id": "s_caxias_9002",
        "seller_city": "Caxias do Sul",
        "seller_state": "RS",
        "carrier_name": "Jadlog Logística",
        "risk_score": 0.35,
        "is_at_risk": False,
        "review_score": None
    },
    {
        "order_id": "ad21c59c0840e6cb83a9ceb5573f8159",
        "customer_id": "c_recife_5521",
        "customer_city": "Recife",
        "customer_state": "PE",
        "order_status": "created",
        "order_purchase_timestamp": "2026-09-17 08:22:15",
        "order_estimated_delivery_date": "2026-09-25 18:00:00",
        "freight_value": 52.00,
        "price": 1150.00,
        "product_category_name": "telefonia",
        "seller_id": "s_sp_9910",
        "seller_city": "São Paulo",
        "seller_state": "SP",
        "carrier_name": "Loggi Express",
        "risk_score": 0.18,
        "is_at_risk": False,
        "review_score": None
    },
    {
        "order_id": "a4591c265e18cb1dcee528d608070f69",
        "customer_id": "c_brasilia_1928",
        "customer_city": "Brasília",
        "customer_state": "DF",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-13 09:12:00",
        "order_estimated_delivery_date": "2026-09-18 12:00:00",
        "freight_value": 31.40,
        "price": 450.00,
        "product_category_name": "cama_mesa_banho",
        "seller_id": "s_curitiba_4021",
        "seller_city": "Curitiba",
        "seller_state": "PR",
        "carrier_name": "Correios SEDEX",
        "risk_score": 0.84,
        "is_at_risk": True,
        "review_score": None
    },
    {
        "order_id": "136cce7faa429382030f9ae92183e112",
        "customer_id": "c_campinas_8821",
        "customer_city": "Campinas",
        "customer_state": "SP",
        "order_status": "delivered",
        "order_purchase_timestamp": "2026-09-10 12:00:00",
        "order_estimated_delivery_date": "2026-09-16 18:00:00",
        "order_delivered_customer_date": "2026-09-15 14:10:00",
        "freight_value": 14.10,
        "price": 79.90,
        "product_category_name": "perfumaria",
        "seller_id": "s_sp_9910",
        "seller_city": "São Paulo",
        "seller_state": "SP",
        "carrier_name": "Total Express",
        "risk_score": 0.05,
        "is_at_risk": False,
        "review_score": 5
    },
    {
        "order_id": "b81ef226f3fe1789b1e8b2acac839d17",
        "customer_id": "c_fortaleza_4421",
        "customer_city": "Fortaleza",
        "customer_state": "CE",
        "order_status": "seller_dispatched",
        "order_purchase_timestamp": "2026-09-14 18:45:00",
        "order_estimated_delivery_date": "2026-09-19 18:00:00",
        "freight_value": 65.40,
        "price": 890.00,
        "product_category_name": "informatica_acessorios",
        "seller_id": "s_campinas_5503",
        "seller_city": "Campinas",
        "seller_state": "SP",
        "carrier_name": "Correios PAC",
        "risk_score": 0.89,
        "is_at_risk": True,
        "review_score": None
    },
    {
        "order_id": "6514b8ad8028c9f2f2374deac9e92620",
        "customer_id": "c_florianopolis_908",
        "customer_city": "Florianópolis",
        "customer_state": "SC",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-15 13:20:00",
        "order_estimated_delivery_date": "2026-09-21 18:00:00",
        "freight_value": 21.30,
        "price": 195.00,
        "product_category_name": "esporte_lazer",
        "seller_id": "s_caxias_9002",
        "seller_city": "Caxias do Sul",
        "seller_state": "RS",
        "carrier_name": "Loggi Express",
        "risk_score": 0.28,
        "is_at_risk": False,
        "review_score": None
    },
    {
        "order_id": "76955be975e5332021190e4e8d35fcf4",
        "customer_id": "c_manaus_1209",
        "customer_city": "Manaus",
        "customer_state": "AM",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-11 10:15:00",
        "order_estimated_delivery_date": "2026-09-18 18:00:00",
        "freight_value": 82.00,
        "price": 1420.00,
        "product_category_name": "telefonia",
        "seller_id": "s_sp_9910",
        "seller_city": "São Paulo",
        "seller_state": "SP",
        "carrier_name": "Correios SEDEX",
        "risk_score": 0.91,
        "is_at_risk": True,
        "review_score": None
    },
    {
        "order_id": "23c21c7d3de92b8d00234a9192fed210",
        "customer_id": "c_goiania_7712",
        "customer_city": "Goiânia",
        "customer_state": "GO",
        "order_status": "in_transit",
        "order_purchase_timestamp": "2026-09-16 15:40:00",
        "order_estimated_delivery_date": "2026-09-23 18:00:00",
        "freight_value": 26.80,
        "price": 310.00,
        "product_category_name": "ferramentas_jardim",
        "seller_id": "s_franca_1102",
        "seller_city": "Franca",
        "seller_state": "SP",
        "carrier_name": "Total Express",
        "risk_score": 0.15,
        "is_at_risk": False,
        "review_score": None
    }
]

SELLER_HISTORIES_RAW: List[Dict[str, Any]] = [
    {
        "seller_id": "s_curitiba_4021",
        "seller_city": "Curitiba",
        "seller_state": "PR",
        "total_orders": 340,
        "late_orders_count": 58,
        "late_order_rate": 0.170,
        "avg_dispatch_hours": 42.5,
        "recent_exceptions_count": 3,
        "review_score_avg": 3.75
    },
    {
        "seller_id": "s_sp_9910",
        "seller_city": "São Paulo",
        "seller_state": "SP",
        "total_orders": 1250,
        "late_orders_count": 48,
        "late_order_rate": 0.038,
        "avg_dispatch_hours": 18.2,
        "recent_exceptions_count": 0,
        "review_score_avg": 4.65
    },
    {
        "seller_id": "s_campinas_5503",
        "seller_city": "Campinas",
        "seller_state": "SP",
        "total_orders": 180,
        "late_orders_count": 41,
        "late_order_rate": 0.227,
        "avg_dispatch_hours": 64.0,
        "recent_exceptions_count": 5,
        "review_score_avg": 3.20
    },
    {
        "seller_id": "s_franca_1102",
        "seller_city": "Franca",
        "seller_state": "SP",
        "total_orders": 520,
        "late_orders_count": 22,
        "late_order_rate": 0.042,
        "avg_dispatch_hours": 20.0,
        "recent_exceptions_count": 1,
        "review_score_avg": 4.50
    },
    {
        "seller_id": "s_caxias_9002",
        "seller_city": "Caxias do Sul",
        "seller_state": "RS",
        "total_orders": 290,
        "late_orders_count": 26,
        "late_order_rate": 0.089,
        "avg_dispatch_hours": 28.0,
        "recent_exceptions_count": 1,
        "review_score_avg": 4.30
    }
]

POLICY_PLAYBOOKS_RAW: List[Dict[str, Any]] = [
    {
        "policy_id": "POL_CARRIER_ESCALATION_01",
        "title": "Hub Transit Bottleneck & Carrier Priority Escalation",
        "category": "CARRIER_ESCALATION",
        "conditions": "Order in transit with <24h remaining before SLA date AND historical route delay probability > 60%",
        "permitted_actions": ["ESCALATE_CARRIER_PRIORITY", "TRIGGER_3PL_SWAP", "FLAG_REGIONAL_HUB"],
        "prohibited_actions": ["AUTO_FULL_REFUND", "CANCEL_IN_FLIGHT_SHIPMENT"],
        "max_voucher_brl": 0.0,
        "requires_human_approval": True,
        "playbook_text": "When transit hubs exhibit severe congestion and SLA is within 24 hours, Operations may trigger Carrier Priority Level 1 (expedited transfer) and notify the carrier liaison. Do not cancel the order while package is in carrier custody."
    },
    {
        "policy_id": "POL_CUSTOMER_PROACTIVE_COMMS_02",
        "title": "Proactive Delivery Delay Notification & Goodwill Voucher",
        "category": "CUSTOMER_COMMS",
        "conditions": "Order risk score >= 0.70 AND estimated delivery delay expected to exceed 24 hours",
        "permitted_actions": ["DRAFT_CUSTOMER_UPDATE", "OFFER_GOODWILL_VOUCHER_MAX_25_BRL"],
        "prohibited_actions": ["UNAUTHORIZED_DIRECT_WHATSAPP_SPAM", "UNBOUNDED_REFUND"],
        "max_voucher_brl": 25.0,
        "requires_human_approval": True,
        "playbook_text": "Before customer files a complaint or bad review, draft an empathetic proactive notification acknowledging transit delay with a revised 48-hour delivery window. Include a R$ 20.00 marketplace credit code subject to operations sign-off."
    },
    {
        "policy_id": "POL_SELLER_DISPATCH_DELAY_03",
        "title": "Chronic Late Seller Dispatch Intervention",
        "category": "SLA_BREACH",
        "conditions": "Seller dispatch elapsed time > 48h AND seller recent exceptions count >= 3",
        "permitted_actions": ["ISSUE_SELLER_WARNING", "PROACTIVE_INVENTORY_REALLOCATION", "EXPEDITE_PICKUP"],
        "prohibited_actions": ["PERMANENT_SELLER_BAN_WITHOUT_AUDIT"],
        "max_voucher_brl": 35.0,
        "requires_human_approval": True,
        "playbook_text": "If a seller with high historical late dispatch rates fails to fulfill order within 48h, dispatch a direct fulfillment partner or initiate urgent pickup. Flag seller account for merchant ops penalty review."
    }
]

async def seed_initial_data(db: AsyncSession):
    # Check existing orders
    res = await db.execute(select(OrderModel).limit(1))
    existing = res.scalars().first()
    
    if not existing:
        for o_data in OLIST_ORDERS_RAW:
            db.add(OrderModel(**o_data))
        for s_data in SELLER_HISTORIES_RAW:
            db.add(SellerHistoryModel(**s_data))
        for p_data in POLICY_PLAYBOOKS_RAW:
            db.add(PolicyPlaybookModel(**p_data))
        await db.commit()
