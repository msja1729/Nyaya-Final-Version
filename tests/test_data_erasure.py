"""Tests for Pralaya data erasure module."""

import pytest


class TestDataErasure:
    """Test data erasure functionality."""

    def test_import(self):
        """Module imports without error."""
        from nyaya_dhwani.data_erasure import (
            SessionData,
            get_session,
            erase_session,
            format_erasure_result,
            ErasureResult,
            PRALAYA_CSS,
        )
        assert SessionData is not None
        assert get_session is not None
        assert erase_session is not None

    def test_session_data_operations(self):
        """SessionData should support basic operations."""
        from nyaya_dhwani.data_erasure import SessionData

        session = SessionData()

        # Chat history
        session.set_chat_history([["Q1", "A1"], ["Q2", "A2"]])
        assert session.get_chat_history() == [["Q1", "A1"], ["Q2", "A2"]]

        # Metadata
        session.set_metadata("user_lang", "hi")
        assert session.get_metadata("user_lang") == "hi"
        assert session.get_metadata("nonexistent", "default") == "default"

        # Arbitrary data
        session.store("custom_key", {"data": 123})
        assert session.retrieve("custom_key") == {"data": 123}

    def test_session_get_all_keys(self):
        """Get all keys should list stored data."""
        from nyaya_dhwani.data_erasure import SessionData

        session = SessionData()
        session.set_chat_history([["Q", "A"]])
        session.set_metadata("lang", "en")
        session.store("key1", "value1")
        session.store("key2", "value2")

        keys = session.get_all_keys()

        assert "key1" in keys
        assert "key2" in keys
        assert "chat_history" in keys
        assert "metadata:lang" in keys

    def test_erase_all(self):
        """Erase all should clear all data."""
        from nyaya_dhwani.data_erasure import SessionData

        session = SessionData()
        session.set_chat_history([["Q", "A"]])
        session.set_metadata("test", "value")
        session.store("key", "data")

        result = session.erase_all()

        assert result.success is True
        assert len(result.items_erased) > 0
        assert "PRALAYA" in result.confirmation_id
        assert session.get_chat_history() == []
        assert session.get_metadata("test") is None
        assert session.retrieve("key") is None

    def test_erase_session_new(self):
        """Erasing non-existent session should succeed gracefully."""
        from nyaya_dhwani.data_erasure import erase_session

        result = erase_session("nonexistent-session-xyz")

        assert result.success is True
        assert "PRALAYA" in result.confirmation_id
        assert "nothing to erase" in result.compliance_note.lower() or len(result.items_erased) == 0

    def test_erase_session_existing(self):
        """Erasing existing session should clear data."""
        from nyaya_dhwani.data_erasure import get_session, erase_session

        # Create and populate session
        session = get_session("test-session-erase")
        session.set_chat_history([["Q", "A"]])
        session.store("data", "value")

        # Erase
        result = erase_session("test-session-erase")

        assert result.success is True
        assert len(result.items_erased) > 0
        assert "DPDP Act 2023" in result.compliance_note

    def test_format_erasure_result(self):
        """Erasure result formatting should be complete."""
        from nyaya_dhwani.data_erasure import format_erasure_result, ErasureResult

        result = ErasureResult(
            success=True,
            timestamp="2024-01-01T00:00:00",
            items_erased=["chat_history", "metadata:lang", "key1"],
            confirmation_id="PRALAYA-ABC123",
            compliance_note="Data erased per DPDP Act",
        )

        formatted = format_erasure_result(result)

        assert "Pralaya" in formatted or "प्रलय" in formatted
        assert "PRALAYA-ABC123" in formatted
        assert "Erasure Complete" in formatted
        assert "Items Erased" in formatted
        assert "Compliance" in formatted
        assert "Section 12" in formatted

    def test_format_erasure_failure(self):
        """Failed erasure should show error."""
        from nyaya_dhwani.data_erasure import format_erasure_result, ErasureResult

        result = ErasureResult(
            success=False,
            timestamp="",
            items_erased=[],
            confirmation_id="",
            compliance_note="",
        )

        formatted = format_erasure_result(result)
        assert "Failed" in formatted

    def test_pralaya_css_defined(self):
        """Pralaya CSS animation should be defined."""
        from nyaya_dhwani.data_erasure import PRALAYA_CSS

        assert "@keyframes pralaya-fire" in PRALAYA_CSS
        assert "pralaya-button" in PRALAYA_CSS
        assert "animation" in PRALAYA_CSS

    def test_erasure_result_fields(self):
        """ErasureResult should have all required fields."""
        from nyaya_dhwani.data_erasure import ErasureResult

        result = ErasureResult(
            success=True,
            timestamp="2024-01-01T00:00:00",
            items_erased=["item1"],
            confirmation_id="PRALAYA-XYZ",
            compliance_note="Test note",
        )

        assert result.success is True
        assert result.timestamp == "2024-01-01T00:00:00"
        assert result.items_erased == ["item1"]
        assert result.confirmation_id == "PRALAYA-XYZ"
        assert result.compliance_note == "Test note"

    def test_session_isolation(self):
        """Different sessions should be isolated."""
        from nyaya_dhwani.data_erasure import get_session, erase_session

        session1 = get_session("session-1")
        session2 = get_session("session-2")

        session1.store("key", "value1")
        session2.store("key", "value2")

        assert session1.retrieve("key") == "value1"
        assert session2.retrieve("key") == "value2"

        # Erase session1
        erase_session("session-1")

        # session2 should be unaffected
        session2_check = get_session("session-2")
        assert session2_check.retrieve("key") == "value2"
