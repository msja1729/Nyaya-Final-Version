"""Tests for Trial of Justice multi-agent module."""

import pytest


class TestTrialOfJustice:
    """Test multi-agent personas and response formatting."""

    def test_import(self):
        """Module imports without error."""
        from nyaya_dhwani.trial_of_justice import (
            run_trial,
            format_trial_response,
            get_single_perspective,
            KIRA_SYSTEM_PROMPT,
            L_SYSTEM_PROMPT,
            SHINIGAMI_SYSTEM_PROMPT,
        )
        assert run_trial is not None
        assert format_trial_response is not None
        assert KIRA_SYSTEM_PROMPT is not None

    def test_persona_prompts_exist(self):
        """All three persona prompts should be defined."""
        from nyaya_dhwani.trial_of_justice import (
            KIRA_SYSTEM_PROMPT,
            L_SYSTEM_PROMPT,
            SHINIGAMI_SYSTEM_PROMPT,
        )

        assert "Kira" in KIRA_SYSTEM_PROMPT
        assert "Prosecution" in KIRA_SYSTEM_PROMPT
        assert "violated" in KIRA_SYSTEM_PROMPT.lower()

        assert "L" in L_SYSTEM_PROMPT
        assert "Defense" in L_SYSTEM_PROMPT
        assert "loophole" in L_SYSTEM_PROMPT.lower() or "exception" in L_SYSTEM_PROMPT.lower()

        assert "Shinigami" in SHINIGAMI_SYSTEM_PROMPT
        assert "neutral" in SHINIGAMI_SYSTEM_PROMPT.lower() or "verdict" in SHINIGAMI_SYSTEM_PROMPT.lower()

    def test_format_trial_response(self):
        """Test response formatting."""
        from nyaya_dhwani.trial_of_justice import format_trial_response

        formatted = format_trial_response(
            prosecution="**PROSECUTION (Kira):** The law was violated.",
            defense="**DEFENSE (L):** There are exceptions.",
            verdict="**VERDICT (Shinigami):** The case is balanced.",
            citations="- DPDP Act Section 6",
        )

        assert "Trial of Justice" in formatted
        assert "PROSECUTION" in formatted
        assert "DEFENSE" in formatted
        assert "VERDICT" in formatted
        assert "DPDP Act" in formatted
        assert "not constitute legal advice" in formatted.lower() or "legal simulation" in formatted.lower()

    def test_trial_response_namedtuple(self):
        """TrialResponse should have expected fields."""
        from nyaya_dhwani.trial_of_justice import TrialResponse

        response = TrialResponse(
            prosecution="prosecution text",
            defense="defense text",
            verdict="verdict text",
            combined="combined text",
            citations="citations",
        )

        assert response.prosecution == "prosecution text"
        assert response.defense == "defense text"
        assert response.verdict == "verdict text"
        assert response.combined == "combined text"
        assert response.citations == "citations"

    def test_quick_prompts_keys(self):
        """Quick prompts should have standard keys."""
        from nyaya_dhwani.trial_of_justice import QUICK_PROMPTS

        assert "prosecution" in QUICK_PROMPTS
        assert "defense" in QUICK_PROMPTS
        assert "verdict" in QUICK_PROMPTS

    def test_get_single_perspective_invalid(self):
        """Invalid perspective should raise error."""
        from nyaya_dhwani.trial_of_justice import get_single_perspective

        with pytest.raises(ValueError) as excinfo:
            get_single_perspective("invalid", "test question", [])

        assert "Unknown perspective" in str(excinfo.value)
