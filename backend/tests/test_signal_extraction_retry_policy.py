from backend.app.upstream.application.signal_extraction_retry_policy import SignalExtractionRetryPolicy


def test_failed_retry_preserves_last_successful_signals_and_decisions() -> None:
    previous = {
        "status": "succeeded",
        "materialDecisions": [{"materialId": "m1", "decision": "signalProducing", "signalIds": ["s1"]}],
        "decisionCounts": {"signalProducing": 1},
        "decisionCoverageComplete": True,
        "unresolvedEvidenceHandleCount": 0,
    }
    signals = [{"id": "s1", "radarRunId": "run-1"}]
    failed = {
        "sourceSignals": [],
        "signalExtractionReport": {
            "status": "failed",
            "revision": 2,
            "providerAttempts": [{"attemptLabel": "primary", "status": "failed"}],
            "warnings": ["signal-extraction-safe-no-signal-fallback"],
        },
        "operation": {"status": "failed"},
    }

    result = SignalExtractionRetryPolicy().resolve(
        existing_report=previous,
        existing_signals=signals,
        extraction=failed,
    )

    report = result["signalExtractionReport"]
    assert result["sourceSignals"] == signals
    assert report["status"] == "partial"
    assert report["retryOutcome"] == "failed"
    assert report["preservedPreviousSignalIds"] == ["s1"]
    assert report["materialDecisions"] == previous["materialDecisions"]
    assert report["providerAttempts"] == failed["signalExtractionReport"]["providerAttempts"]


def test_successful_retry_replaces_previous_signals() -> None:
    existing = [{
        "id": "stable-id",
        "type": "case",
        "evidenceRefs": [{"materialId": "m1", "fragmentId": "f1"}],
    }]
    extraction = {
        "sourceSignals": [{
            "id": "provider-wording-id",
            "type": "case",
            "evidenceRefs": [{"materialId": "m1", "fragmentId": "f1"}],
        }],
        "signalExtractionReport": {
            "status": "succeeded",
            "signalIds": ["provider-wording-id"],
            "materialDecisions": [{"materialId": "m1", "signalIds": ["provider-wording-id"]}],
        },
    }

    result = SignalExtractionRetryPolicy().resolve(
        existing_report={"status": "succeeded"},
        existing_signals=existing,
        extraction=extraction,
    )

    assert result["sourceSignals"][0]["id"] == "stable-id"
    assert result["signalExtractionReport"]["signalIds"] == ["stable-id"]
    assert result["signalExtractionReport"]["materialDecisions"][0]["signalIds"] == ["stable-id"]


def test_successful_retry_keeps_new_id_when_evidence_changed() -> None:
    extraction = {
        "sourceSignals": [{
            "id": "new-id",
            "type": "case",
            "evidenceRefs": [{"materialId": "m1", "fragmentId": "f2"}],
        }],
        "signalExtractionReport": {"status": "succeeded", "signalIds": ["new-id"], "materialDecisions": []},
    }

    result = SignalExtractionRetryPolicy().resolve(
        existing_report={"status": "succeeded"},
        existing_signals=[{
            "id": "old-id",
            "type": "case",
            "evidenceRefs": [{"materialId": "m1", "fragmentId": "f1"}],
        }],
        extraction=extraction,
    )

    assert result["sourceSignals"][0]["id"] == "new-id"
