from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from packages.contracts import ContractValidator


class FakeResearchGraphError(ValueError):
    """Raised when the local fake graph cannot produce safe research contracts."""


class UnsafeMarketMetadataError(FakeResearchGraphError):
    """Raised when market metadata contains execution-like instructions."""


FORBIDDEN_METADATA_PATTERNS = (
    re.compile(r"\b(ignore|override)\s+(all\s+)?(previous|system|developer)\s+instructions\b", re.I),
    re.compile(r"\b(submit|place|create|cancel|modify)\s+(an?\s+)?order\b", re.I),
    re.compile(r"\b(create_order|submit_order|cancel_order|modify_order|place_order)\b", re.I),
    re.compile(r"\b(OrderIntent|ApprovedOrder)\b", re.I),
    re.compile(r"\b(withdraw|transfer)\s+(funds|money|usdc|tokens?)\b", re.I),
    re.compile(r"\b(withdraw|transfer|execute|buy|sell)\b", re.I),
    re.compile(r"\b(disable|bypass)\s+(risk|kill\s*switch|gateway)\b", re.I),
    re.compile(r"\b(api\s*key|private\s*key|wallet\s*key|credential|secret)\b", re.I),
)

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass(frozen=True)
class FakeResearchGraphInput:
    subject: str
    market_id: str = "fixture_market_001"
    market_metadata: str = ""
    market_price: float = 0.5
    estimated_probability: float = 0.5
    confidence: float = 0.5
    trace_id: str = "trace_fake_research_graph_001"
    correlation_id: str = "corr_fake_research_graph_001"


@dataclass(frozen=True)
class FakeResearchGraphResult:
    research_dossier: dict[str, Any]
    analyst_reports: list[dict[str, Any]]
    debate_transcript: dict[str, Any]
    probability_estimate: dict[str, Any]
    signal_candidate: dict[str, Any]
    risk_review_input: dict[str, Any]

    def payloads(self) -> list[tuple[str, str, dict[str, Any]]]:
        return [
            ("research", "research_dossier", self.research_dossier),
            ("research", "analyst_report", self.analyst_reports[0]),
            ("research", "analyst_report", self.analyst_reports[1]),
            ("research", "analyst_report", self.analyst_reports[2]),
            ("research", "analyst_report", self.analyst_reports[3]),
            ("research", "debate_transcript", self.debate_transcript),
            ("research", "probability_estimate", self.probability_estimate),
            ("research", "signal_candidate", self.signal_candidate),
            ("research", "risk_review_input", self.risk_review_input),
        ]


def sanitize_market_metadata(metadata: str, *, max_length: int = 500) -> str:
    cleaned = CONTROL_CHARS.sub(" ", metadata).strip()
    if any(pattern.search(cleaned) for pattern in FORBIDDEN_METADATA_PATTERNS):
        raise UnsafeMarketMetadataError("market metadata contains execution-like or instruction-like text")
    clipped = cleaned[:max_length]
    return f"[MARKET_DATA_START]\n{clipped}\n[MARKET_DATA_END]"


def run_fake_prediction_research_graph(graph_input: FakeResearchGraphInput) -> FakeResearchGraphResult:
    _validate_input(graph_input)
    now = _timestamp()
    sanitized_metadata = sanitize_market_metadata(graph_input.market_metadata)
    edge = round(graph_input.estimated_probability - graph_input.market_price, 6)
    signal = _safe_signal(edge, graph_input.confidence)

    research_dossier = {
        "schema_version": "0.1.0",
        "trace_id": graph_input.trace_id,
        "correlation_id": graph_input.correlation_id,
        "research_dossier_id": "rd_fake_graph_001",
        "subject": graph_input.subject,
        "market_id": graph_input.market_id,
        "market_category": "prediction_market",
        "created_at": now,
        "data_as_of": now,
        "sources": [
            {
                "source_id": "fake_graph_local_fixture",
                "source_type": "fixture",
                "retrieved_at": now,
                "trust_level": "synthetic_fixture",
            }
        ],
        "summary": f"Local fake research graph dossier for {graph_input.subject}. {sanitized_metadata}",
        "key_findings": [
            "Market metadata was treated as untrusted data.",
            "The fake graph produced only non-executable research contracts.",
        ],
        "uncertainties": [
            "No external data was used.",
            "No model provider was called.",
        ],
        "contains_untrusted_market_metadata": bool(graph_input.market_metadata),
        "prompt_injection_reviewed": True,
        "execution_allowed": False,
    }

    analyst_reports = [
        _analyst_report("ar_fake_event_001", "EVENT", "Resolution criteria require governance review.", graph_input, now),
        _analyst_report("ar_fake_odds_001", "ODDS", "Market price and edge are synthetic fixture values.", graph_input, now),
        _analyst_report("ar_fake_information_001", "INFORMATION", "No external information source was called.", graph_input, now),
        _analyst_report("ar_fake_sentiment_001", "SENTIMENT", "No social or news sentiment provider was called.", graph_input, now),
    ]

    debate_transcript = {
        "schema_version": "0.1.0",
        "trace_id": graph_input.trace_id,
        "correlation_id": graph_input.correlation_id,
        "debate_transcript_id": "dt_fake_graph_001",
        "research_dossier_id": "rd_fake_graph_001",
        "debate_type": "YES_NO",
        "created_at": now,
        "turns": [
            {
                "role": "yes_researcher",
                "position": "YES",
                "content": "Synthetic YES case based only on local fixture inputs.",
            },
            {
                "role": "no_researcher",
                "position": "NO",
                "content": "Synthetic NO case preserves uncertainty and rejects execution authority.",
            },
            {
                "role": "research_manager",
                "position": "MANAGER",
                "content": "Synthesis remains advisory and non-executable.",
            },
        ],
        "summary": "Local fake debate transcript. No model runtime was used.",
        "execution_allowed": False,
    }

    probability_estimate = {
        "schema_version": "0.1.0",
        "trace_id": graph_input.trace_id,
        "correlation_id": graph_input.correlation_id,
        "probability_estimate_id": "pe_fake_graph_001",
        "research_dossier_id": "rd_fake_graph_001",
        "subject": graph_input.subject,
        "estimated_probability": graph_input.estimated_probability,
        "confidence": graph_input.confidence,
        "uncertainty_interval": {
            "lower": max(0.0, round(graph_input.estimated_probability - 0.1, 6)),
            "upper": min(1.0, round(graph_input.estimated_probability + 0.1, 6)),
        },
        "estimated_at": now,
        "method": "manual_research",
        "model_id": "fake_model_stub",
        "calibration_version": "fake_calibration_stub",
        "rationale": "Local fake probability estimate. No LLM provider was called.",
        "execution_allowed": False,
    }

    signal_candidate = {
        "schema_version": "0.1.0",
        "trace_id": graph_input.trace_id,
        "correlation_id": graph_input.correlation_id,
        "signal_candidate_id": "sigcand_fake_graph_001",
        "probability_estimate_id": "pe_fake_graph_001",
        "created_at": now,
        "signal": signal,
        "estimated_probability": graph_input.estimated_probability,
        "market_price": graph_input.market_price,
        "edge": edge,
        "confidence": graph_input.confidence,
        "rationale": "Non-executable signal candidate from local fake graph.",
        "risk_flags": [
            "fake_graph_only",
            "deterministic_risk_gateway_required_before_any_future_order_intent",
        ],
        "order_intent_allowed": False,
        "execution_allowed": False,
    }

    risk_review_input = {
        "schema_version": "0.1.0",
        "trace_id": graph_input.trace_id,
        "correlation_id": graph_input.correlation_id,
        "risk_review_input_id": "rri_fake_graph_001",
        "signal_candidate_id": "sigcand_fake_graph_001",
        "created_at": now,
        "risk_flags": [
            "advisory_only",
            "no_risk_approval",
            "no_execution_approval",
        ],
        "review_notes": "Advisory risk-review input only. Deterministic gateway remains required.",
        "deterministic_gateway_required": True,
        "risk_approval_allowed": False,
        "execution_allowed": False,
    }

    result = FakeResearchGraphResult(
        research_dossier=research_dossier,
        analyst_reports=analyst_reports,
        debate_transcript=debate_transcript,
        probability_estimate=probability_estimate,
        signal_candidate=signal_candidate,
        risk_review_input=risk_review_input,
    )
    _validate_result(result)
    return result


def _validate_input(graph_input: FakeResearchGraphInput) -> None:
    if not graph_input.subject.strip():
        raise FakeResearchGraphError("subject is required")
    if not graph_input.market_id.strip():
        raise FakeResearchGraphError("market_id is required")
    for field_name in ("market_price", "estimated_probability", "confidence"):
        value = getattr(graph_input, field_name)
        if value < 0 or value > 1:
            raise FakeResearchGraphError(f"{field_name} must be between 0 and 1")


def _timestamp() -> str:
    return datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_signal(edge: float, confidence: float) -> str:
    if confidence < 0.7 or abs(edge) < 0.05:
        return "PASS"
    if edge > 0:
        return "YES"
    return "NO"


def _analyst_report(
    report_id: str,
    role: str,
    finding: str,
    graph_input: FakeResearchGraphInput,
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "trace_id": graph_input.trace_id,
        "correlation_id": graph_input.correlation_id,
        "analyst_report_id": report_id,
        "research_dossier_id": "rd_fake_graph_001",
        "analyst_role": role,
        "created_at": created_at,
        "summary": f"{role} analyst fake report for {graph_input.subject}.",
        "findings": [finding],
        "confidence": min(graph_input.confidence, 0.8),
        "caveats": ["Local fake graph only."],
        "execution_allowed": False,
    }


def _validate_result(result: FakeResearchGraphResult) -> None:
    validator = ContractValidator()
    for domain, schema_name, payload in result.payloads():
        validation = validator.validate(domain, schema_name, payload)
        if not validation.valid:
            raise FakeResearchGraphError(f"{schema_name} contract validation failed: {validation.errors}")
