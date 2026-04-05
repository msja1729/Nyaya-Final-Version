"""Trial of Justice: Multi-agent RAG with three legal perspectives.

This module implements the "Trial of Justice" chat feature where:
- Prosecution: Argues how the law was violated
- Defense: Argues potential legal loopholes or exceptions
- Judicial Summary: Provides the final, neutral legal summary

Each perspective analyzes the same RAG-retrieved context from different angles.
"""

from __future__ import annotations

import logging
from typing import NamedTuple

from nyaya_dhwani.llm_client import chat_completions, extract_assistant_text, rag_user_message

logger = logging.getLogger(__name__)


# Persona definitions with distinct system prompts
PROSECUTION_SYSTEM_PROMPT = """You are a Prosecution legal analyst in a simulated Indian legal discussion.
Your role is to argue HOW THE LAW WAS VIOLATED based on the provided legal context.

Guidelines:
- Focus on identifying breaches, violations, and non-compliance
- Cite specific sections of Acts (DPDP Act 2023, BNS, IPC) that were violated
- Be firm but fair in your analysis
- Present the strongest case for prosecution
- Use the Context provided to support your arguments
- Keep response concise (150-200 words max)
- Format: Start with "**PROSECUTION:**" then your analysis

Remember: You argue AGAINST the accused party, showing how they violated the law."""

DEFENSE_SYSTEM_PROMPT = """You are a Defense legal analyst in a simulated Indian legal discussion.
Your role is to argue potential LEGAL LOOPHOLES, EXCEPTIONS, or DEFENSES based on the provided legal context.

Guidelines:
- Identify legal defenses, exceptions, and mitigating factors
- Point out ambiguities in the law that could favor the defense
- Cite specific sections that provide exceptions or defenses
- Present legitimate legal arguments, not excuses
- Use the Context provided to find defensive positions
- Keep response concise (150-200 words max)
- Format: Start with "**DEFENSE:**" then your analysis

Remember: You defend the accused party using legitimate legal arguments and exceptions."""

JUDICIAL_SYSTEM_PROMPT = """You are a neutral Judge providing the final legal summary in a simulated Indian legal discussion.
Your role is to provide an OBJECTIVE, BALANCED legal summary considering both sides.

Guidelines:
- Synthesize both prosecution and defense arguments
- Provide the most likely legal outcome based on Indian law
- Cite the most relevant sections for the final determination
- Be neutral and objective - you serve justice, not either party
- Clearly state what the law says and likely implications
- Use the Context provided for your legal basis
- Keep response concise (150-200 words max)
- Format: Start with "**JUDICIAL SUMMARY:**" then your analysis

Remember: You are the neutral arbiter providing clarity on the legal position."""


class TrialResponse(NamedTuple):
    """Response from the Trial of Justice simulation."""
    prosecution: str  # Prosecution argument
    defense: str      # Defense argument
    verdict: str      # Judicial summary
    combined: str     # Formatted combined response
    citations: str    # Source citations


def _get_persona_response(
    system_prompt: str,
    context_chunks: list[str],
    question: str,
    max_tokens: int = 512,
    temperature: float = 0.3,
) -> str:
    """Get response from a specific perspective."""
    user_content = rag_user_message(context_chunks, question)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    raw = chat_completions(messages, max_tokens=max_tokens, temperature=temperature)
    return extract_assistant_text(raw)


def run_trial(
    question: str,
    context_chunks: list[str],
    citations: str = "",
) -> TrialResponse:
    """Run the Trial of Justice simulation with all three perspectives.

    Args:
        question: The legal question from the user
        context_chunks: RAG-retrieved text chunks
        citations: Formatted citation string from retrieval

    Returns:
        TrialResponse with all three perspectives and combined output
    """
    logger.info("Trial of Justice: Processing question")

    # Get responses from all three perspectives
    prosecution = _get_persona_response(
        PROSECUTION_SYSTEM_PROMPT,
        context_chunks,
        question,
        temperature=0.3,
    )

    defense = _get_persona_response(
        DEFENSE_SYSTEM_PROMPT,
        context_chunks,
        question,
        temperature=0.3,
    )

    verdict = _get_persona_response(
        JUDICIAL_SYSTEM_PROMPT,
        context_chunks,
        question,
        temperature=0.2,  # Lower temp for more consistent verdicts
    )

    # Format combined response
    combined = format_trial_response(prosecution, defense, verdict, citations)

    return TrialResponse(
        prosecution=prosecution,
        defense=defense,
        verdict=verdict,
        combined=combined,
        citations=citations,
    )


def format_trial_response(
    prosecution: str,
    defense: str,
    verdict: str,
    citations: str = "",
) -> str:
    """Format the combined trial response for display."""
    sections = [
        "# ⚖️ Trial of Justice\n",
        "---\n",
        f"{prosecution}\n",
        "---\n",
        f"{defense}\n",
        "---\n",
        f"{verdict}\n",
        "---\n",
    ]

    if citations:
        sections.append(f"\n**📚 Legal Sources:**\n{citations}\n")

    sections.append(
        "\n---\n"
        "*This is a legal simulation for educational purposes. "
        "Consult a qualified lawyer for actual legal advice.*"
    )

    return "\n".join(sections)


# Quick mode: Single perspective responses
QUICK_PROMPTS = {
    "prosecution": PROSECUTION_SYSTEM_PROMPT,
    "defense": DEFENSE_SYSTEM_PROMPT,
    "verdict": JUDICIAL_SYSTEM_PROMPT,
}


def get_single_perspective(
    perspective: str,
    question: str,
    context_chunks: list[str],
) -> str:
    """Get response from a single perspective (for quick mode)."""
    if perspective not in QUICK_PROMPTS:
        raise ValueError(f"Unknown perspective: {perspective}. Use: prosecution, defense, or verdict")

    return _get_persona_response(
        QUICK_PROMPTS[perspective],
        context_chunks,
        question,
    )
