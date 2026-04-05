"""Agni-Pariksha: Terms & Conditions / Privacy Policy Scanner.

This module analyzes privacy policies and T&C documents against:
- Section 6 (Notice) of DPDP Act 2023
- Section 7 (Consent) of DPDP Act 2023

Returns a risk score and list of red flag clauses that may violate Indian law.
"""

from __future__ import annotations

import logging
import re
from typing import NamedTuple

from nyaya_dhwani.llm_client import chat_completions, extract_assistant_text

logger = logging.getLogger(__name__)

# DPDP Act 2023 key requirements for Notice (Section 6)
SECTION_6_REQUIREMENTS = """
DPDP Act 2023 - Section 6 (Notice):
1. Data Fiduciary must give notice with:
   - Description of personal data being collected
   - Purpose of processing
   - Rights of the Data Principal (access, correction, erasure, grievance redressal)
   - How to make a complaint to the Data Protection Board
2. Notice must be given BEFORE or AT THE TIME of collection
3. Notice must be in clear, plain language
4. If consent was given before the Act, notice must still be given
"""

# DPDP Act 2023 key requirements for Consent (Section 7)
SECTION_7_REQUIREMENTS = """
DPDP Act 2023 - Section 7 (Consent):
1. Consent must be FREE, SPECIFIC, INFORMED, UNCONDITIONAL, and UNAMBIGUOUS
2. Must indicate clear AFFIRMATIVE action
3. Must be LIMITED to specified purpose
4. Can be WITHDRAWN at any time
5. Withdrawal must be as EASY as giving consent
6. Cannot be bundled/tied to service (no "take it or leave it")
7. Consent for children requires verifiable parental consent
8. Cannot process data beyond what is NECESSARY for the purpose
"""

# Common red flag patterns in privacy policies
RED_FLAG_PATTERNS = [
    (r"we\s+may\s+share.*with\s+third\s+part", "Vague third-party sharing without specific identification"),
    (r"by\s+using\s+(?:this|our)\s+(?:service|app|website).*you\s+(?:agree|consent)", "Implied consent by use (violates explicit consent requirement)"),
    (r"we\s+(?:may|can|reserve)\s+(?:the\s+right\s+to\s+)?(?:change|modify|update).*(?:without\s+notice|at\s+any\s+time)", "Policy changes without proper notice"),
    (r"indefinite(?:ly)?|perpetual|forever|unlimited\s+(?:period|time)", "Indefinite data retention"),
    (r"irrevocable|cannot\s+be\s+(?:withdrawn|revoked)", "Irrevocable consent (violates withdrawal right)"),
    (r"all\s+(?:data|information)|any\s+(?:data|information)", "Overly broad data collection"),
    (r"sell.*(?:data|information)|monetize.*(?:data|information)", "Data monetization/selling"),
    (r"(?:waive|surrender|give\s+up).*(?:rights?|claims?)", "Rights waiver clause"),
    (r"(?:no|not)\s+(?:responsible|liable).*(?:breach|leak|loss)", "Blanket liability disclaimer for data breaches"),
    (r"transfer.*(?:country|jurisdiction|overseas)", "Cross-border transfer without adequate safeguards notice"),
]


class RedFlag(NamedTuple):
    """A red flag clause identified in the policy."""
    clause: str
    issue: str
    severity: str  # "high", "medium", "low"
    dpdp_section: str
    recommendation: str


class ScanResult(NamedTuple):
    """Result of T&C/Privacy Policy scan."""
    risk_score: int  # 0-100
    risk_level: str  # "low", "medium", "high", "critical"
    red_flags: list[RedFlag]
    summary: str
    compliant_aspects: list[str]
    recommendations: list[str]


SCANNER_SYSTEM_PROMPT = """You are Agni-Pariksha, a legal compliance analyzer specializing in Indian data protection law.
Your task is to analyze privacy policies and Terms & Conditions against the Digital Personal Data Protection Act 2023.

Focus on:
1. Section 6 (Notice) - Does the policy clearly inform users about data collection, purpose, and rights?
2. Section 7 (Consent) - Is consent free, specific, informed, and withdrawable?

For each issue found, provide:
- The exact clause or excerpt that's problematic
- Which DPDP section it potentially violates
- Severity: "high" (clear violation), "medium" (ambiguous/potentially non-compliant), "low" (minor concern)
- A specific recommendation for users

Also identify any compliant aspects.

Respond in this JSON format:
{
    "risk_score": <0-100>,
    "red_flags": [
        {
            "clause": "<exact text from policy>",
            "issue": "<what's wrong>",
            "severity": "high|medium|low",
            "dpdp_section": "Section 6 or 7",
            "recommendation": "<what user should do>"
        }
    ],
    "compliant_aspects": ["<list of things done right>"],
    "summary": "<2-3 sentence overall assessment>"
}"""


def _extract_sentences_around_match(text: str, match_start: int, match_end: int, context: int = 100) -> str:
    """Extract text around a regex match for context."""
    start = max(0, match_start - context)
    end = min(len(text), match_end + context)
    excerpt = text[start:end].strip()
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."
    return excerpt


def quick_pattern_scan(policy_text: str) -> list[RedFlag]:
    """Quick regex-based scan for obvious red flags."""
    flags = []
    text_lower = policy_text.lower()

    for pattern, issue in RED_FLAG_PATTERNS:
        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
        for match in matches[:2]:  # Limit to 2 matches per pattern
            clause = _extract_sentences_around_match(
                policy_text, match.start(), match.end()
            )
            flags.append(RedFlag(
                clause=clause,
                issue=issue,
                severity="medium",
                dpdp_section="Section 6/7",
                recommendation="Review this clause carefully before agreeing",
            ))

    return flags


def analyze_policy(
    policy_text: str,
    app_name: str = "the application",
    use_llm: bool = True,
) -> ScanResult:
    """Analyze a privacy policy or T&C document against DPDP Act.

    Args:
        policy_text: The full text of the privacy policy
        app_name: Name of the app/service (for context)
        use_llm: Whether to use LLM for deep analysis (requires API)

    Returns:
        ScanResult with risk score, red flags, and recommendations
    """
    # Quick pattern-based scan
    pattern_flags = quick_pattern_scan(policy_text)

    if not use_llm:
        # Return pattern-based results only
        risk_score = min(100, len(pattern_flags) * 15)
        risk_level = _score_to_level(risk_score)
        return ScanResult(
            risk_score=risk_score,
            risk_level=risk_level,
            red_flags=pattern_flags,
            summary=f"Found {len(pattern_flags)} potential issues via pattern matching. "
                    "Enable LLM analysis for deeper review.",
            compliant_aspects=[],
            recommendations=[
                "Read the full policy carefully",
                "Look for data deletion/withdrawal options",
                "Check what data is being collected and why",
            ],
        )

    # LLM-based deep analysis
    try:
        return _llm_analyze(policy_text, app_name, pattern_flags)
    except Exception as e:
        logger.warning("LLM analysis failed, using pattern results: %s", e)
        risk_score = min(100, len(pattern_flags) * 15)
        return ScanResult(
            risk_score=risk_score,
            risk_level=_score_to_level(risk_score),
            red_flags=pattern_flags,
            summary=f"Pattern-based analysis found {len(pattern_flags)} issues. "
                    f"LLM analysis unavailable: {e}",
            compliant_aspects=[],
            recommendations=["Review manually or try again later"],
        )


def _llm_analyze(
    policy_text: str,
    app_name: str,
    pattern_flags: list[RedFlag],
) -> ScanResult:
    """Use LLM for deep policy analysis."""
    import json

    # Truncate very long policies
    max_length = 8000
    if len(policy_text) > max_length:
        policy_text = policy_text[:max_length] + "\n\n[... truncated for analysis ...]"

    user_prompt = f"""Analyze this privacy policy from {app_name} against DPDP Act 2023.

{SECTION_6_REQUIREMENTS}

{SECTION_7_REQUIREMENTS}

---
PRIVACY POLICY TEXT:
{policy_text}
---

Provide your analysis in the JSON format specified."""

    messages = [
        {"role": "system", "content": SCANNER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    raw = chat_completions(messages, max_tokens=2048, temperature=0.1)
    response_text = extract_assistant_text(raw)

    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if not json_match:
        raise ValueError("Could not parse LLM response as JSON")

    result = json.loads(json_match.group())

    # Parse red flags
    llm_flags = []
    for flag_data in result.get("red_flags", []):
        llm_flags.append(RedFlag(
            clause=flag_data.get("clause", ""),
            issue=flag_data.get("issue", ""),
            severity=flag_data.get("severity", "medium"),
            dpdp_section=flag_data.get("dpdp_section", ""),
            recommendation=flag_data.get("recommendation", ""),
        ))

    # Combine pattern and LLM flags, deduplicate
    all_flags = llm_flags + [f for f in pattern_flags if f.clause not in [lf.clause for lf in llm_flags]]

    risk_score = result.get("risk_score", 50)
    risk_level = _score_to_level(risk_score)

    return ScanResult(
        risk_score=risk_score,
        risk_level=risk_level,
        red_flags=all_flags,
        summary=result.get("summary", "Analysis complete."),
        compliant_aspects=result.get("compliant_aspects", []),
        recommendations=_generate_recommendations(all_flags, risk_level),
    )


def _score_to_level(score: int) -> str:
    """Convert numeric score to risk level."""
    if score >= 75:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 25:
        return "medium"
    return "low"


def _generate_recommendations(flags: list[RedFlag], risk_level: str) -> list[str]:
    """Generate actionable recommendations based on findings."""
    recs = []

    if risk_level in ("critical", "high"):
        recs.append("⚠️ Consider not using this service until the privacy policy is improved")
        recs.append("📝 Document your concerns and contact the company's data protection officer")

    high_severity = [f for f in flags if f.severity == "high"]
    if high_severity:
        recs.append(f"🚨 Address {len(high_severity)} high-severity issues immediately")

    if any("third" in f.issue.lower() for f in flags):
        recs.append("🔍 Request a list of all third parties your data is shared with")

    if any("consent" in f.issue.lower() for f in flags):
        recs.append("✋ Check if you can use the service without giving broad consent")

    if any("retention" in f.issue.lower() or "indefinite" in f.clause.lower() for f in flags):
        recs.append("📅 Ask about data retention periods and deletion policies")

    recs.append("📞 If you proceed, know you can complain to the Data Protection Board of India")
    recs.append("🔗 Review your rights under DPDP Act 2023 Sections 11-14")

    return recs[:6]  # Limit to 6 recommendations


def format_scan_result(result: ScanResult) -> str:
    """Format scan result for display in Gradio UI."""
    risk_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴",
    }

    lines = [
        f"# 🔥 Agni-Pariksha Analysis Report\n",
        f"## Risk Assessment: {risk_emoji.get(result.risk_level, '⚪')} {result.risk_level.upper()} ({result.risk_score}/100)\n",
        f"*{result.summary}*\n",
        "---\n",
    ]

    if result.red_flags:
        lines.append("## 🚩 Red Flag Clauses\n")
        for i, flag in enumerate(result.red_flags, 1):
            severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}.get(flag.severity, "⚪")
            lines.append(f"### {i}. {severity_emoji} {flag.issue}\n")
            lines.append(f"> \"{flag.clause}\"\n")
            lines.append(f"- **DPDP Section:** {flag.dpdp_section}")
            lines.append(f"- **Recommendation:** {flag.recommendation}\n")

    if result.compliant_aspects:
        lines.append("\n## ✅ Compliant Aspects\n")
        for aspect in result.compliant_aspects:
            lines.append(f"- {aspect}")
        lines.append("")

    lines.append("\n## 💡 Recommendations\n")
    for rec in result.recommendations:
        lines.append(f"- {rec}")

    lines.append("\n---\n")
    lines.append("*This analysis is based on DPDP Act 2023 Sections 6 (Notice) and 7 (Consent). "
                 "Consult a legal professional for definitive guidance.*")

    return "\n".join(lines)
