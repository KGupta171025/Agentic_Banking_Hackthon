# PayOps Sentinel: Autonomous Cross-Border Payment Ops Incident Commander

> **Hackathon Track:** Track 3 — Payment Ops Incident Commander  
> **Host:** Airwallex | HackerEarth Agentic Banking Hackathon  
> **Team:** Krishna's Team 5  

---

## 📌 Executive Summary

Cross-border business payouts are notoriously prone to silent delays: SWIFT intermediary hold-ups, compliance/sanction false-positives, timezone rail cutoffs, and beneficiary account mismatches. When a high-value supplier payment ($50,000+) is stalled, payment operations teams face a critical dilemma: **retrying the payment risks a catastrophic double-payment**, while waiting risks severed vendor relations or supply chain halts.

**PayOps Sentinel** is an autonomous, safety-first AI Incident Commander powered by Airwallex APIs, Claude 3.5/Sonnet tool-calling, and Model Context Protocol (MCP). It continuously monitors payment webhooks, diagnoses root causes in real-time, safely attempts cancellations/recalls, dynamically re-routes transactions across local clearing rails or single-use virtual cards, and guarantees **Zero-Double-Pay idempotency**.

---

## 🚨 The Core Problem & The "Double-Payment Trap"

In enterprise treasury and payment operations:
1. **Opaque Delay Diagnostics:** Payment statuses often sit in "PENDING" or "IN_REVIEW" across correspondent banking chains with no actionable insight.
2. **The Double-Payment Disaster:** When operations teams rush to resolve an urgent supplier escalation by re-issuing funds before confirming cancellation of the initial payment, both payments clear. Recovering cross-border duplicate payments takes 45–90 days with legal expenses and massive balance sheet risk.
3. **High Human Friction:** Investigating MT103 messages, SWIFT gpi tracker data, beneficiary details, and FX quotes wastes hours of manual effort during critical business outages.

---

## 💡 The Solution: PayOps Sentinel Architecture

```
+-----------------------------------------------------------------------------------+
|                            Airwallex Event Stream                                 |
|  (Webhook Triggers: payment.delayed, payment.failed, payout.compliance_review)    |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                        Stage 1: Anomaly Ingestion & Triage                        |
|  - Validates webhook signatures                                                   |
|  - Normalizes incident payload (UETR, Beneficiary, Currency, SLA window)          |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|              Stage 2: Deterministic Diagnostic Agent (Airwallex MCP)              |
|  - Queries Airwallex Payout Details API: GET /api/v1/payouts/{id}                 |
|  - Traces SWIFT gpi / UETR / Intermediary Bank status                             |
|  - Verifies FX quote validity & account balance sufficiency                       |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|           Stage 3: Decision & Policy Engine (Zero-Double-Pay Protocol)            |
|  [Decision Matrix]:                                                               |
|   ├── State A: Rail Delay (Wait & generate MT103 confirmation to vendor)          |
|   ├── State B: Recoverable (Execute atomic cancel -> verify refund -> re-route)   |
|   └── State C: Non-recoverable Critical (Issue dynamic locked Virtual Card)       |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                        Stage 4: Autonomous Safe Execution                         |
|  - Cancel Stalled Payout: POST /api/v1/payouts/{id}/cancel                        |
|  - Atomic Lock: Awaits Airwallex CANCELLED webhook before releasing new funds     |
|  - Failover Rails: Dispatches via Airwallex Local Rail (SEPA/FedNow) OR           |
|    Issues instant single-use virtual card via Airwallex Issuing API               |
+-----------------------------------------------------------------------------------+
                                      │
                                      ▼
+-----------------------------------------------------------------------------------+
|                 Stage 5: Auditability & Human-In-The-Loop (HITL)                   |
|  - Generates full incident post-mortem and compliance audit log                   |
|  - High-value escalation (> $25,000) dispatched to Slack/Teams for 1-click signoff|
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Airwallex API Integration Blueprint

| Capability | Airwallex API Endpoint | Purpose in PayOps Sentinel |
| :--- | :--- | :--- |
| **Payout Tracking** | `GET /api/v1/payouts/{id}` | Inspect real-time status, UETR, failure codes, and tracking references |
| **Atomic Cancellation** | `POST /api/v1/payouts/{id}/cancel` | Safely abort in-flight transactions before initiating failover |
| **FX & Wallet Check** | `GET /api/v1/balances`, `POST /api/v1/fx/quotes` | Check available multi-currency balances and re-quote FX spreads |
| **Local Rail Payout** | `POST /api/v1/payouts/create` | Re-route via optimal local clearing rail (ACH, SEPA, Faster Payments) |
| **Emergency Card Issuing** | `POST /api/v1/issuing/cards` | Issue instantaneous single-use virtual card locked to supplier MCC |
| **Webhook Ingestion** | `/api/v1/webhooks` | Real-time event listener for payment anomalies and status transitions |

---

## 🛡️ Zero-Double-Pay Idempotency & Safety Protocol

1. **State Machine Lock:** The agent enforces a strict state machine lock. A replacement payout or card issuance can **NEVER** be initiated while the prior payment is in `PENDING`, `DISPATCHED`, or `PROCESSING` state.
2. **Two-Phase Verification:** 
   - Phase 1: Issue cancellation request to Airwallex Payouts API.
   - Phase 2: Await `payout.cancelled` terminal webhook + verify funds returned to Global Account balance. Only then is the replacement transaction unlocked.
3. **Emergency Card Bridge (Fallback):** If the supplier demands instant payment while a wire is under bank investigation, the agent can issue an Airwallex Virtual Card with an expiry window of 2 hours, capped exactly to the invoice amount, and locked to the supplier's merchant category.

---

## 🚀 Tech Stack

- **Agent Reasoning & LLM:** Claude 3.5 Sonnet / GPT-4o via Model Context Protocol (MCP)
- **Agent Orchestration:** LangGraph / StateGraph with deterministic safety guardrails
- **Banking Infrastructure:** Airwallex Sandbox APIs (Payouts, Global Accounts, FX, Issuing)
- **Backend & Event System:** FastAPI / Node.js, Webhook receiver with HMAC validation
- **Frontend / Incident Dashboard:** Next.js, TailwindCSS, React Flow (Live Agent State Visualization)
- **Monitoring & Alerts:** Slack Bolt API / Discord webhooks for Human-In-The-Loop escalation

---

## 👥 Team
- **Team Leader:** Krishna (Krishna's Team 5)
- **Repository:** [https://github.com/KGupta171025/Agentic_Banking_Hackthon](https://github.com/KGupta171025/Agentic_Banking_Hackthon)
