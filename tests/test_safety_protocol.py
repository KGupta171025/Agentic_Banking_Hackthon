"""
Test suite validating the Zero-Double-Pay safety guarantee of PayOps Sentinel.
"""

from unittest.mock import MagicMock
from src.agent.state_machine import (
    IncidentCommanderAgent,
    IncidentContext,
    IncidentStatus,
)


def test_blocks_reissuance_on_active_transfer():
    """Verify that an active/in-review transfer is never permitted to re-issue."""
    mock_client = MagicMock()
    mock_client.get_transfer_details.return_value = {
        "id": "tr_123",
        "status": "IN_REVIEW",
    }
    # Cancellation cannot be immediately confirmed by downstream bank
    mock_client.cancel_transfer.return_value = {"id": "tr_123", "status": "PENDING"}

    agent = IncidentCommanderAgent(airwallex_client=mock_client)
    context = IncidentContext(
        incident_id="inc_001",
        original_transfer_id="tr_123",
        amount=50000.0,
        currency="USD",
        beneficiary_name="Acme Components Ltd",
    )

    result = agent.evaluate_incident(context)

    # Must escalate to human and lock re-issuance to prevent double-payment!
    assert result.status == IncidentStatus.ESCALATED_TO_HUMAN
    assert result.human_intervention_required is True
    assert "Locked to prevent double payout" in result.escalation_reason


def test_allows_reissuance_after_verified_cancellation():
    """Verify that once cancellation is confirmed, safe recovery is unlocked."""
    mock_client = MagicMock()
    mock_client.get_transfer_details.return_value = {
        "id": "tr_456",
        "status": "IN_REVIEW",
    }
    mock_client.cancel_transfer.return_value = {"id": "tr_456", "status": "CANCELLED"}

    agent = IncidentCommanderAgent(airwallex_client=mock_client)
    context = IncidentContext(
        incident_id="inc_002",
        original_transfer_id="tr_456",
        amount=15000.0,
        currency="USD",
        beneficiary_name="Apex Logistics",
    )

    result = agent.evaluate_incident(context)

    assert result.status == IncidentStatus.SAFE_TO_RESOLVE
    assert result.human_intervention_required is False
