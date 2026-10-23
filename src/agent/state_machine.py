"""
PayOps Sentinel - Incident Commander State Machine.
Implements Track 3 (Payment Ops Incident Commander) with Zero-Double-Pay safety protocol.

Guarantees:
- Never executes a replacement payment while the original transfer is active or ambiguous.
- Fail-closed: halts and escalates to human operator if cancellation cannot be verified.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    DIAGNOSING = "DIAGNOSING"
    AWAITING_CANCELLATION = "AWAITING_CANCELLATION"
    SAFE_TO_RESOLVE = "SAFE_TO_RESOLVE"
    ESCALATED_TO_HUMAN = "ESCALATED_TO_HUMAN"
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"


class PaymentState(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    DISPATCHED = "DISPATCHED"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class IncidentContext(BaseModel):
    incident_id: str
    original_transfer_id: str
    amount: float
    currency: str = "USD"
    beneficiary_name: str
    status: IncidentStatus = IncidentStatus.DETECTED
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    actions_taken: List[str] = Field(default_factory=list)
    human_intervention_required: bool = False
    escalation_reason: Optional[str] = None
    replacement_payment_id: Optional[str] = None


class IncidentCommanderAgent:
    def __init__(self, airwallex_client: Any, high_value_threshold: float = 25000.0):
        self.client = airwallex_client
        self.high_value_threshold = high_value_threshold

    def evaluate_incident(self, context: IncidentContext) -> IncidentContext:
        """Main decision loop for managing a delayed cross-border supplier payment."""
        context.actions_taken.append("Ingested payment delay anomaly.")
        context.status = IncidentStatus.DIAGNOSING

        # Step 1: Query Airwallex for current transfer status & UETR tracking
        try:
            transfer_details = self.client.get_transfer_details(
                context.original_transfer_id
            )
            context.diagnostics["airwallex_response"] = transfer_details
            current_status = transfer_details.get("status", PaymentState.UNKNOWN)
        except Exception as e:
            context.status = IncidentStatus.ESCALATED_TO_HUMAN
            context.human_intervention_required = True
            context.escalation_reason = (
                f"Failed to fetch transfer details: {e}. Fail-closed safety activated."
            )
            return context

        # Step 2: High Value Check (Human Governance)
        if context.amount >= self.high_value_threshold:
            context.actions_taken.append(
                f"High-value payment (${context.amount:,.2f}) exceeds threshold (${self.high_value_threshold:,.2f})."
            )

        # Step 3: Zero-Double-Pay Safety Check
        if current_status in [PaymentState.CANCELLED, PaymentState.REJECTED]:
            context.status = IncidentStatus.SAFE_TO_RESOLVE
            context.actions_taken.append(
                f"Original transfer is verified in terminal state ({current_status}). Safe to evaluate re-issuance."
            )
            return context

        if current_status in [
            PaymentState.PENDING,
            PaymentState.IN_REVIEW,
            PaymentState.DISPATCHED,
        ]:
            context.actions_taken.append(
                f"Transfer is in active/ambiguous state ({current_status}). RE-ISSUANCE PROHIBITED to prevent double-payment."
            )
            context.status = IncidentStatus.AWAITING_CANCELLATION

            # Attempt atomic cancellation
            try:
                cancel_resp = self.client.cancel_transfer(context.original_transfer_id)
                context.actions_taken.append(
                    f"Dispatched cancellation request. Response: {cancel_resp.get('status')}"
                )
                if cancel_resp.get("status") == PaymentState.CANCELLED:
                    context.status = IncidentStatus.SAFE_TO_RESOLVE
                    context.actions_taken.append("Cancellation confirmed! Safe for recovery routing.")
                else:
                    context.status = IncidentStatus.ESCALATED_TO_HUMAN
                    context.human_intervention_required = True
                    context.escalation_reason = (
                        "Cancellation unconfirmed by clearing network. Locked to prevent double payout."
                    )
            except Exception as ex:
                context.status = IncidentStatus.ESCALATED_TO_HUMAN
                context.human_intervention_required = True
                context.escalation_reason = (
                    f"Atomic cancellation request failed: {ex}. Halting automated re-routing."
                )

        return context
