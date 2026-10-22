# HACKEREARTH SUBMISSION DETAILS

## FIELD 1: Title
PayOps Sentinel: Autonomous Cross-Border Payment Incident Commander with Zero-Double-Pay Protocol

---

## FIELD 2: Description
(Copy everything below into the Description box)

### 1. Problem Statement
Cross-border B2B supplier payments frequently suffer from "silent failures"—funds stuck in intermediary SWIFT correspondent banks, delayed clearing window cut-offs, AML/sanctions false positives, or invalid routing parameters.

When a critical payment (e.g. $50,000 for manufacturing parts) is delayed, payment operations teams face an operational trap:
- **If they wait:** The supplier halts production, disrupting business operations.
- **If they re-issue payment:** If the first payment eventually clears, the company incurs a catastrophic **double payment**. Recovering cross-border duplicate wire transfers can take months of legal disputes with massive financial exposure.

---

### 2. Our Solution: PayOps Sentinel
**PayOps Sentinel** is an autonomous, safety-first AI Payment Ops Incident Commander built on Airwallex's API ecosystem and Model Context Protocol (MCP). It continuously listens to payment events, identifies delayed or stalled transfers, performs automated root-cause diagnostics, and safely recovers or re-routes the payment while mathematically guaranteeing **Zero-Double-Pay idempotency**.

#### Key Capabilities:
1. **Real-Time Anomaly Triage:** Ingests Airwallex webhooks (`payment.delayed`, `payment.failed`, `payout.compliance_review`) to detect anomalies within seconds.
2. **Autonomous Root-Cause Analysis (RCA):** Queries Airwallex Payout Details API, inspecting UETR tracking references, correspondent bank hold reasons, and rail statuses.
3. **Zero-Double-Pay Safe Execution Protocol:**
   - Enforces a 2-phase terminal lock: initiates an atomic cancellation via Airwallex Payout Cancel API (`/api/v1/payouts/{id}/cancel`).
   - Awaits verified `payout.cancelled` terminal status and funds credited back before releasing any secondary funds.
4. **Adaptive Failover Routing:**
   - Routes via Airwallex local clearing rails (ACH / SEPA Instant / Faster Payments) to bypass stuck SWIFT correspondent networks.
   - **Emergency Virtual Card Fallback:** If wire transfer remains unresolvable before a hard cutoff, the agent programmatically issues an instant, single-use Airwallex Corporate Virtual Card locked to the supplier's Merchant Category Code (MCC) and capped strictly to the invoice amount.
5. **Human-In-The-Loop (HITL) Governance:** High-value transactions (> $25,000) or high-risk edge cases generate an interactive Slack/Teams alert with full diagnostic traces and a 1-click human sign-off button.

---

### 3. Airwallex API Integration Plan
Our architecture directly connects to core Airwallex endpoints:
- **Airwallex Payouts API (`/api/v1/payouts/*`):** Real-time payout status tracking, UETR lookup, and atomic cancellations.
- **Airwallex Issuing API (`/api/v1/issuing/cards`):** Dynamic generation of purpose-bound, merchant-locked virtual cards for emergency supplier settlement.
- **Airwallex Balances & FX API (`/api/v1/balances`, `/api/v1/fx/quotes`):** Multi-currency balance checks and automated currency conversions for cross-border re-routing.
- **Airwallex Webhooks & MCP Server:** Event-driven architecture connecting Claude 3.5 tool-calling to Airwallex developer sandbox tools.

---

### 4. Technical Architecture & Tech Stack
- **AI Agent Framework:** LangGraph / StateGraph with deterministic guardrail nodes for financial safety.
- **LLM & Tool Calling:** Claude 3.5 Sonnet connected via Model Context Protocol (MCP) to Airwallex APIs.
- **Backend:** FastAPI (Python) with HMAC-secured webhook listeners and PostgreSQL for idempotency state tracking.
- **Frontend Dashboard:** Next.js, TailwindCSS, React Flow (providing a visual live stream of the agent's reasoning steps, SWIFT rail status, and action logs).
- **Incident Escalation:** Slack Bolt API for HITL approval workflows.

---

### 5. Expected Business Impact
- **Eliminates 100% of duplicate payment risks** through deterministic cancellation verification locks.
- **Reduces cross-border payment incident MTTR (Mean Time to Resolution)** from 6–12 hours of manual investigation down to under 3 minutes.
- **Maintains critical vendor relationships** by automatically generating MT103 confirmation proofs and alternative instant settlement channels.

---

### 6. Prototype & Repository
- **GitHub Repository:** https://github.com/KGupta171025/Agentic_Banking_Hackthon
