"""Tests for Agni-Pariksha T&C scanner module."""

import pytest


class TestTCScanner:
    """Test privacy policy scanner functionality."""

    def test_import(self):
        """Module imports without error."""
        from nyaya_dhwani.tc_scanner import (
            analyze_policy,
            format_scan_result,
            quick_pattern_scan,
            ScanResult,
            RedFlag,
        )
        assert analyze_policy is not None
        assert format_scan_result is not None

    def test_quick_pattern_scan_detects_third_party(self):
        """Pattern scan should detect third-party sharing."""
        from nyaya_dhwani.tc_scanner import quick_pattern_scan

        policy = "We may share your information with third parties for marketing purposes."
        flags = quick_pattern_scan(policy)

        assert len(flags) > 0
        assert any("third" in f.issue.lower() for f in flags)

    def test_quick_pattern_scan_detects_implied_consent(self):
        """Pattern scan should detect implied consent."""
        from nyaya_dhwani.tc_scanner import quick_pattern_scan

        policy = "By using this service you agree to all our data practices."
        flags = quick_pattern_scan(policy)

        assert len(flags) > 0
        assert any("consent" in f.issue.lower() or "implied" in f.issue.lower() for f in flags)

    def test_quick_pattern_scan_clean_policy(self):
        """Clean policy should have minimal flags."""
        from nyaya_dhwani.tc_scanner import quick_pattern_scan

        policy = """
        We collect only necessary data.
        You can withdraw consent at any time.
        Contact our Data Protection Officer for questions.
        """
        flags = quick_pattern_scan(policy)

        assert len(flags) == 0

    def test_scan_result_structure(self):
        """ScanResult should have all required fields."""
        from nyaya_dhwani.tc_scanner import ScanResult, RedFlag

        result = ScanResult(
            risk_score=50,
            risk_level="medium",
            red_flags=[
                RedFlag(
                    clause="test clause",
                    issue="test issue",
                    severity="medium",
                    dpdp_section="Section 6",
                    recommendation="test recommendation",
                )
            ],
            summary="Test summary",
            compliant_aspects=["Good thing 1"],
            recommendations=["Do this"],
        )

        assert result.risk_score == 50
        assert result.risk_level == "medium"
        assert len(result.red_flags) == 1
        assert result.red_flags[0].severity == "medium"

    def test_format_scan_result(self):
        """Scan result formatting should include all sections."""
        from nyaya_dhwani.tc_scanner import format_scan_result, ScanResult, RedFlag

        result = ScanResult(
            risk_score=75,
            risk_level="high",
            red_flags=[
                RedFlag(
                    clause="We sell your data",
                    issue="Data monetization",
                    severity="high",
                    dpdp_section="Section 7",
                    recommendation="Avoid this service",
                )
            ],
            summary="High risk policy",
            compliant_aspects=["Clear language"],
            recommendations=["Consider alternatives"],
        )

        formatted = format_scan_result(result)

        assert "Agni-Pariksha" in formatted
        assert "HIGH" in formatted
        assert "75" in formatted
        assert "Data monetization" in formatted
        assert "Section 7" in formatted
        assert "Clear language" in formatted
        assert "Consider alternatives" in formatted

    def test_risk_levels(self):
        """Risk levels should be correctly assigned."""
        from nyaya_dhwani.tc_scanner import _score_to_level

        assert _score_to_level(10) == "low"
        assert _score_to_level(30) == "medium"
        assert _score_to_level(60) == "high"
        assert _score_to_level(80) == "critical"

    def test_analyze_policy_no_llm(self):
        """Analysis without LLM should work."""
        from nyaya_dhwani.tc_scanner import analyze_policy

        policy = """
        We may share your data with third parties.
        By using our service you consent to everything.
        We retain your data indefinitely.
        """

        result = analyze_policy(policy, "TestApp", use_llm=False)

        assert result.risk_score > 0
        assert len(result.red_flags) > 0
        assert result.risk_level in ("low", "medium", "high", "critical")

    def test_dpdp_requirements_defined(self):
        """DPDP requirements should be defined."""
        from nyaya_dhwani.tc_scanner import (
            SECTION_6_REQUIREMENTS,
            SECTION_7_REQUIREMENTS,
        )

        assert "Notice" in SECTION_6_REQUIREMENTS
        assert "Section 6" in SECTION_6_REQUIREMENTS
        assert "Consent" in SECTION_7_REQUIREMENTS
        assert "Section 7" in SECTION_7_REQUIREMENTS
        assert "FREE" in SECTION_7_REQUIREMENTS
        assert "SPECIFIC" in SECTION_7_REQUIREMENTS
        assert "INFORMED" in SECTION_7_REQUIREMENTS

    def test_red_flag_patterns_defined(self):
        """Red flag patterns should be defined."""
        from nyaya_dhwani.tc_scanner import RED_FLAG_PATTERNS

        assert len(RED_FLAG_PATTERNS) > 5
        # Each pattern should be a tuple of (regex, description)
        for pattern, description in RED_FLAG_PATTERNS:
            assert isinstance(pattern, str)
            assert isinstance(description, str)
            assert len(description) > 10
