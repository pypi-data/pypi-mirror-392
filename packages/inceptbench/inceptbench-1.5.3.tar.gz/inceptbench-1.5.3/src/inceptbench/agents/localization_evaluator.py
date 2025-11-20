"""
Localization Evaluator: Comprehensive checks for localized educational content.

Evaluates content against localization guidelines including:
- Schema fidelity (JSON structure preservation)
- Language correctness (grammar, spelling, terminology)
- Neutral scenario policy (cultural neutrality)
- Sensitivity guardrails (no religion, politics, etc.)
- Terminology & units (UAE curriculum standards, metric units)
- Tone & voice (appropriate educational tone)
- Clarity & cognitive load (minimal narrative overhead)
- Localization guardrail coverage
- Review checklist compliance
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import textwrap
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from pydantic import BaseModel

from .core.api_key_manager import get_openai_client

logger = logging.getLogger(__name__)

GUIDANCE_JSON_PATH = Path(__file__).with_name("localization_guidelines.json")

SECTION_CONFIG = {
    "neutral scenario policy": {"field": "neutral_scenario", "title": "Neutral Scenario Policy"},
    "sensitivity guardrails": {"field": "sensitivity_guardrails", "title": "Sensitivity Guardrails"},
    "localization guardrail coverage": {"field": "guardrail_coverage", "title": "Localization Guardrail Coverage"},
    "rule-based regionalization (itd guidance)": {
        "field": "regionalization_rules",
        "title": "Rule-Based Regionalization (ITD Guidance)"
    },
}

SECTION_CRITICAL_FLAGS: Dict[str, bool] = {}
MAX_RULE_CONCURRENCY = max(1, int(os.getenv("LOCALIZATION_RULE_CONCURRENCY", "5")))

RULE_SYSTEM_PROMPT = textwrap.dedent("""
You are a localization quality specialist. Evaluate ONE localization rule at a time.
- Return PASS (score=1) only if the localized content clearly satisfies the rule.
- Return FAIL (score=0) if there is any violation, uncertainty, or missing evidence.
- Keep reasoning concise and cite concrete evidence.

Output JSON with:
{ "rule_id": string, "passed": bool, "score": 0 or 1, "reasoning": string }
""")


def _load_localization_sections() -> List[Dict[str, Any]]:
    """Load localization guidance sections from JSON."""
    try:
        with GUIDANCE_JSON_PATH.open("r", encoding="utf-8") as guidance_file:
            data = json.load(guidance_file)
    except FileNotFoundError:
        logger.error("Localization guidance file %s not found.", GUIDANCE_JSON_PATH)
        return []
    except json.JSONDecodeError as exc:
        logger.error(
            "Localization guidance file %s is invalid JSON (%s).",
            GUIDANCE_JSON_PATH,
            exc,
        )
        return []

    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        logger.error(
            "Localization guidance file %s does not define any sections.",
            GUIDANCE_JSON_PATH,
        )
        return []

    return sections


def _slugify_title(title: str) -> str:
    """Return a filesystem-friendly slug for a section title."""
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in title.strip())
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_") or "section"


def _build_rule_entries(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten sections into individual rule entries for evaluation."""
    entries: List[Dict[str, Any]] = []

    for section in sections:
        raw_title = section.get("title", "").strip()
        if not raw_title:
            continue

        lookup_key = raw_title.lower()
        config = SECTION_CONFIG.get(lookup_key)
        field_name = config["field"] if config else _slugify_title(raw_title)
        canonical_title = config["title"] if config else raw_title
        section_slug = _slugify_title(raw_title)
        section_critical = bool(section.get("critical", False))
        SECTION_CRITICAL_FLAGS[field_name] = section_critical
        rules = section.get("rules", [])

        if not isinstance(rules, list) or not rules:
            continue

        for idx, raw_rule in enumerate(rules, start=1):
            if isinstance(raw_rule, dict):
                rule_text = str(
                    raw_rule.get("description")
                    or raw_rule.get("text")
                    or raw_rule.get("rule")
                    or ""
                ).strip()
                prompt_text = str(raw_rule.get("prompt") or rule_text).strip()
                custom_id = raw_rule.get("id")
            else:
                rule_text = str(raw_rule).strip()
                prompt_text = rule_text
                custom_id = None

            if not rule_text:
                continue

            rule_id = custom_id or f"{section_slug}.{idx}"
            entries.append(
                {
                    "rule_id": rule_id,
                    "section_title": canonical_title,
                    "section_key": lookup_key,
                    "field": field_name,
                    "rule_text": rule_text,
                    "prompt_text": prompt_text,
                    "critical_section": section_critical,
                }
            )

    return entries


LOCALIZATION_SECTIONS = _load_localization_sections()
RULE_ENTRIES = _build_rule_entries(LOCALIZATION_SECTIONS)


class RuleEvaluationLLMResponse(BaseModel):
    """Structured response for a single rule check."""
    rule_id: str
    passed: bool
    score: int  # 0 or 1
    reasoning: str


def _build_rule_user_prompt(
    rule_entry: Dict[str, Any],
    content_payload: str,
    metadata: Dict[str, Any],
    original_content: Optional[str] = None,
) -> str:
    """Create a concise user prompt for a single-rule check."""
    prompt_lines = [
        "Evaluate the localized educational content against ONE localization rule.",
        "",
        f"Rule ID: {rule_entry['rule_id']}",
        f"Section: {rule_entry['section_title']}",
        f"Rule Description: {rule_entry['rule_text']}",
        f"Evaluation Prompt: {rule_entry.get('prompt_text', rule_entry['rule_text'])}",
        "",
        "Context:",
        f"- Content Type: {metadata.get('content_type', 'unknown')}",
        f"- Target Language: {metadata.get('target_language', 'unknown')}",
        f"- Target Locale: {metadata.get('target_locale', 'Not specified')}",
        f"- Cultural Context: {metadata.get('cultural_context', 'Not specified')}",
        f"- Grade: {metadata.get('grade', 'Not specified')}",
        f"- Subject: {metadata.get('subject', 'Not specified')}",
        f"- Topic: {metadata.get('skill_title', 'Not specified')}",
        "",
        "Localized Content:",
        content_payload,
    ]

    if original_content:
        prompt_lines.extend(
            [
                "",
                "Original Reference Content:",
                original_content,
            ]
        )

    prompt_lines.extend(
        [
            "",
            "Return PASS (score=1) only if the localized content clearly satisfies this rule.",
            "Return FAIL (score=0) if there is any violation, ambiguity, or missing evidence.",
        ]
    )

    return "\n".join(prompt_lines)


def _extract_parsed_response(response) -> Optional[RuleEvaluationLLMResponse]:
    """Helper to extract the parsed Pydantic object from responses.parse output."""
    for output_item in getattr(response, "output", []):
        if output_item.type != "message":
            continue
        for content_item in getattr(output_item, "content", []):
            if (
                content_item.type == "output_text"
                and hasattr(content_item, "parsed")
                and content_item.parsed is not None
            ):
                parsed = content_item.parsed
                if isinstance(parsed, RuleEvaluationLLMResponse):
                    return parsed
                if hasattr(parsed, "model_dump"):
                    return RuleEvaluationLLMResponse(**parsed.model_dump())
    return None


def _evaluate_rule_sync(rule_entry: Dict[str, Any], user_prompt: str) -> RuleEvaluationLLMResponse:
    """Synchronously evaluate a single rule with retry logic."""
    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            client = get_openai_client(timeout=180.0)
            response = client.responses.parse(
                model="o3-mini",
                input=[
                    {"role": "system", "content": RULE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                text_format=RuleEvaluationLLMResponse,
            )

            parsed = _extract_parsed_response(response)
            if parsed:
                return parsed

            raise ValueError("Rule evaluation did not return a parsed response")

        except Exception as exc:
            attempt_num = attempt + 1
            logger.warning(
                "Error evaluating localization rule %s (attempt %s/%s): %s: %s",
                rule_entry["rule_id"],
                attempt_num,
                max_retries + 1,
                type(exc).__name__,
                exc,
            )

            if attempt < max_retries:
                backoff = min(2 ** attempt, 10)
                time.sleep(backoff)
            else:
                logger.error(
                    "Rule %s evaluation failed after %s attempts",
                    rule_entry["rule_id"],
                    max_retries + 1,
                )
                raise

    raise RuntimeError(f"Rule {rule_entry['rule_id']} evaluation failed with unknown error")


async def _evaluate_rule_async(
    rule_entry: Dict[str, Any],
    content_payload: str,
    metadata: Dict[str, Any],
    original_content: Optional[str] = None,
) -> Dict[str, Any]:
    """Async wrapper to evaluate a single rule and attach metadata."""
    loop = asyncio.get_event_loop()
    user_prompt = _build_rule_user_prompt(rule_entry, content_payload, metadata, original_content)
    parsed = await loop.run_in_executor(None, _evaluate_rule_sync, rule_entry, user_prompt)

    score = 1 if parsed.score else 0
    passed = bool(parsed.passed and score == 1)

    return {
        "rule_id": parsed.rule_id or rule_entry["rule_id"],
        "section_title": rule_entry["section_title"],
        "section_key": rule_entry["section_key"],
        "field": rule_entry["field"],
        "rule_text": rule_entry["rule_text"],
        "prompt_text": rule_entry.get("prompt_text", rule_entry["rule_text"]),
        "passed": passed,
        "score": score,
        "reasoning": parsed.reasoning.strip(),
        "critical_section": rule_entry.get("critical_section", False),
    }


async def _evaluate_rules_concurrently(
    rule_entries: List[Dict[str, Any]],
    content_payload: str,
    metadata: Dict[str, Any],
    original_content: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Evaluate multiple rules using limited concurrency."""

    if MAX_RULE_CONCURRENCY <= 1:
        results = []
        for entry in rule_entries:
            result = await _evaluate_rule_async(entry, content_payload, metadata, original_content)
            results.append(result)
        return results

    semaphore = asyncio.Semaphore(MAX_RULE_CONCURRENCY)

    async def _bounded_evaluate(entry: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            return await _evaluate_rule_async(entry, content_payload, metadata, original_content)

    tasks = [_bounded_evaluate(entry) for entry in rule_entries]
    return await asyncio.gather(*tasks)


def _summarize_section(rules: List[Dict[str, Any]], title: str, critical: bool = False) -> Dict[str, Any]:
    """Aggregate individual rule scores for a section."""
    total = len(rules)
    passes = sum(rule["score"] for rule in rules)
    percentage = (passes / total) if total else 0.0

    if passes == total and total > 0:
        score = 2
        pass_fail = "PASS"
    elif passes == 0:
        score = 0
        pass_fail = "FAIL"
    else:
        score = 1
        pass_fail = "FAIL"

    issues = [
        f"{rule['rule_text']} — {rule['reasoning']}"
        for rule in rules
        if not rule["passed"]
    ]
    strengths = [
        f"{rule['rule_text']} — {rule['reasoning']}"
        for rule in rules
        if rule["passed"]
    ]

    reasoning = f"{passes}/{total} rules satisfied ({percentage:.0%})."

    return {
        "criterion": title,
        "pass_fail": pass_fail,
        "score": score,
        "reasoning": reasoning,
        "issues": issues,
        "strengths": strengths,
        "percentage": percentage,
        "critical": critical,
    }


def _aggregate_rule_results(rule_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate per-rule scores into section-level and overall summaries."""
    sections: Dict[str, Dict[str, Any]] = {}

    for result in rule_results:
        field = result["field"]
        if field not in sections:
            sections[field] = {
                "title": result["section_title"],
                "rules": [],
                "critical": result.get("critical_section", False),
            }
        sections[field]["rules"].append(result)
        sections[field]["critical"] = sections[field]["critical"] or result.get("critical_section", False)

    section_summaries: Dict[str, Dict[str, Any]] = {}
    overall_passes = 0
    total_rules = 0

    for field, data in sections.items():
        summary = _summarize_section(
            data["rules"],
            data["title"],
            critical=data.get("critical", False) or SECTION_CRITICAL_FLAGS.get(field, False),
        )
        section_summaries[field] = summary
        total_rules += len(data["rules"])
        overall_passes += sum(rule["score"] for rule in data["rules"])

    # Ensure every expected section has an entry, even if no rules were loaded.
    for section_key, config in SECTION_CONFIG.items():
        field = config["field"]
        if field not in section_summaries:
            section_summaries[field] = {
                "criterion": config["title"],
                "pass_fail": "FAIL",
                "score": 0,
                "reasoning": "No rules defined for this criterion.",
                "issues": ["No localization rules defined for this section."],
                "strengths": [],
                "percentage": 0.0,
                "critical": SECTION_CRITICAL_FLAGS.get(field, False),
            }

    overall_score = (overall_passes / total_rules) if total_rules else 0.0

    issues = [
        issue
        for summary in section_summaries.values()
        for issue in summary.get("issues", [])
    ]
    strengths = [
        strength
        for summary in section_summaries.values()
        for strength in summary.get("strengths", [])
    ]

    critical_failures = [
        summary["criterion"]
        for summary in section_summaries.values()
        if summary.get("critical") and summary["pass_fail"] == "FAIL"
    ]

    if critical_failures:
        recommendation = "reject"
        risk_notes = (
            "Critical localization guardrails failed: "
            + ", ".join(critical_failures)
        )
    elif overall_score >= 0.85:
        recommendation = "accept"
        risk_notes = ""
    elif overall_score >= 0.5:
        recommendation = "revise"
        risk_notes = ""
    else:
        recommendation = "reject"
        risk_notes = "Overall localization score below acceptable threshold."

    result_payload = {
        **{field: {
            "criterion": summary["criterion"],
            "pass_fail": summary["pass_fail"],
            "score": summary["score"],
            "reasoning": summary["reasoning"],
            "issues": summary["issues"],
            "strengths": summary["strengths"],
        } for field, summary in section_summaries.items()},
        "overall_score": overall_score,
        "recommendation": recommendation,
        "issues": issues,
        "strengths": strengths,
        "risk_notes": risk_notes,
        "rule_breakdown": [
            {
                "rule_id": rule["rule_id"],
                "section": rule["section_title"],
                "rule": rule["rule_text"],
                "prompt": rule.get("prompt_text", rule["rule_text"]),
                "passed": rule["passed"],
                "score": rule["score"],
                "reasoning": rule["reasoning"],
            }
            for rule in rule_results
        ],
    }

    return result_payload

async def evaluate_localization(
    content: str,
    target_language: str = "ar",
    target_locale: Optional[str] = None,
    cultural_context: Optional[str] = None,
    content_type: str = "question",
    original_content: Optional[str] = None,
    grade: Optional[str] = None,
    subject: Optional[str] = None,
    skill_title: Optional[str] = None
) -> str:
    """
    Evaluates localized educational content by issuing many small rule checks.
    
    Parameters
    ----------
    content : str
        The localized content to evaluate (question text, answer, explanation, etc.)
    target_language : str
        Target language code (e.g., "ar" for Arabic, "en" for English)
    target_locale : Optional[str]
        Locale identifier (e.g., "ar-AE" for Arabic/UAE, "en-IN" for English/India)
    cultural_context : Optional[str]
        Cultural region (e.g., "AE", "IN") to guide cultural guardrails
    content_type : str
        Type of content: "question", "text", or "article"
    original_content : Optional[str]
        Original content for schema comparison (if available)
    grade : Optional[str]
        Target grade level
    subject : Optional[str]
        Subject area
    skill_title : Optional[str]
        Skill/topic title
        
    Returns
    -------
    str
        The evaluation response from the model as a JSON string
    """
    logger.info(
        "Evaluating localization (%s) for language %s%s",
        content_type,
        target_language,
        f" ({target_locale})" if target_locale else "",
    )

    if not RULE_ENTRIES:
        return json.dumps(
            {
                "error": (
                    "Localization guidance is missing or empty. "
                    "Update localization_guidelines.json."
                )
            }
        )

    content_payload = (content or "").strip()
    if not content_payload:
        return json.dumps({"error": "No localized content provided for evaluation."})

    metadata = {
        "content_type": content_type,
        "target_language": target_language,
        "target_locale": target_locale or "Not specified",
        "cultural_context": cultural_context or "Not specified",
        "grade": grade or "Not specified",
        "subject": subject or "Not specified",
        "skill_title": skill_title or "Not specified",
    }

    try:
        rule_results: List[Dict[str, Any]] = await _evaluate_rules_concurrently(
            RULE_ENTRIES,
            content_payload,
            metadata,
            original_content,
        )
        aggregated = _aggregate_rule_results(rule_results)
        return json.dumps(aggregated)

    except Exception as exc:
        logger.error("Localization evaluation error: %s", exc)
        return json.dumps({"error": f"Localization evaluation failed: {exc}"})

