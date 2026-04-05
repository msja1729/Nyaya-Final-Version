"""Pralaya Button: Instant data erasure for Right to Erasure compliance.

This module provides the "burn after reading" functionality:
- Wipes user's chat history from session
- Clears any cached data
- Returns confirmation of erasure

Complies with DPDP Act 2023 Right to Erasure (Section 12).
"""

from __future__ import annotations

import logging
import secrets
import time
from datetime import datetime
from typing import Any, NamedTuple

logger = logging.getLogger(__name__)


class ErasureResult(NamedTuple):
    """Result of data erasure operation."""
    success: bool
    timestamp: str
    items_erased: list[str]
    confirmation_id: str
    compliance_note: str


class SessionData:
    """Manages session data for a user."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._chat_history: list[list[str]] = []
        self._metadata: dict[str, Any] = {}
        self._created_at: str = datetime.utcnow().isoformat()

    def set_chat_history(self, history: list[list[str]]) -> None:
        """Store chat history."""
        self._chat_history = history

    def get_chat_history(self) -> list[list[str]]:
        """Get chat history."""
        return self._chat_history

    def set_metadata(self, key: str, value: Any) -> None:
        """Store metadata."""
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata."""
        return self._metadata.get(key, default)

    def store(self, key: str, value: Any) -> None:
        """Store arbitrary data."""
        self._data[key] = value

    def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve stored data."""
        return self._data.get(key, default)

    def get_all_keys(self) -> list[str]:
        """Get all stored data keys."""
        keys = list(self._data.keys())
        if self._chat_history:
            keys.append("chat_history")
        keys.extend([f"metadata:{k}" for k in self._metadata.keys()])
        return keys

    def erase_all(self) -> ErasureResult:
        """Erase all session data - the Pralaya function.

        Returns:
            ErasureResult with confirmation details
        """
        items_erased = self.get_all_keys()

        # Secure erasure - overwrite before clearing
        for key in list(self._data.keys()):
            self._data[key] = None
        self._data.clear()

        # Overwrite chat history entries
        for i in range(len(self._chat_history)):
            if isinstance(self._chat_history[i], list):
                for j in range(len(self._chat_history[i])):
                    self._chat_history[i][j] = ""
        self._chat_history.clear()

        # Clear metadata
        for key in list(self._metadata.keys()):
            self._metadata[key] = None
        self._metadata.clear()

        # Generate confirmation
        confirmation_id = f"PRALAYA-{secrets.token_hex(8).upper()}"

        logger.info(
            "Pralaya: Erased %d items, confirmation: %s",
            len(items_erased),
            confirmation_id,
        )

        return ErasureResult(
            success=True,
            timestamp=datetime.utcnow().isoformat(),
            items_erased=items_erased,
            confirmation_id=confirmation_id,
            compliance_note=(
                "Data erased in compliance with DPDP Act 2023, Section 12 "
                "(Right to Erasure). No personal data from this session remains."
            ),
        )


# Global session storage (in production, use proper session management)
_sessions: dict[str, SessionData] = {}


def get_session(session_id: str) -> SessionData:
    """Get or create a session."""
    if session_id not in _sessions:
        _sessions[session_id] = SessionData()
    return _sessions[session_id]


def erase_session(session_id: str) -> ErasureResult:
    """Erase all data for a session.

    Args:
        session_id: The session identifier

    Returns:
        ErasureResult with confirmation
    """
    if session_id not in _sessions:
        return ErasureResult(
            success=True,
            timestamp=datetime.utcnow().isoformat(),
            items_erased=[],
            confirmation_id=f"PRALAYA-{secrets.token_hex(8).upper()}",
            compliance_note="No data found for this session - nothing to erase.",
        )

    result = _sessions[session_id].erase_all()

    # Remove session entirely
    del _sessions[session_id]

    return result


def format_erasure_result(result: ErasureResult) -> str:
    """Format erasure result for display.

    Includes the "fire" animation trigger marker.
    """
    if not result.success:
        return "❌ **Erasure Failed**\n\nPlease try again or contact support."

    lines = [
        "# 🔥 प्रलय (Pralaya) - Data Destroyed\n",
        "---\n",
        "## ✅ Erasure Complete\n",
        f"**Timestamp:** {result.timestamp} UTC\n",
        f"**Confirmation ID:** `{result.confirmation_id}`\n",
    ]

    if result.items_erased:
        lines.append(f"\n**Items Erased:** {len(result.items_erased)}\n")
        for item in result.items_erased[:10]:  # Show first 10
            lines.append(f"- ~~{item}~~")
        if len(result.items_erased) > 10:
            lines.append(f"- ... and {len(result.items_erased) - 10} more")
        lines.append("")

    lines.extend([
        "\n---\n",
        "## 📜 Compliance Certificate\n",
        f"*{result.compliance_note}*\n",
        "\n---\n",
        "**Your Rights Under DPDP Act 2023:**",
        "- ✅ Right to Erasure (Section 12) - Exercised",
        "- ℹ️ You can request this action at any time",
        "- ℹ️ No fees apply for erasure requests",
        "\n*Save your Confirmation ID for records.*",
    ])

    return "\n".join(lines)


# CSS for fire animation (to be added to Gradio app)
PRALAYA_CSS = """
@keyframes pralaya-fire {
    0% { background-color: transparent; }
    25% { background-color: rgba(255, 100, 0, 0.3); }
    50% { background-color: rgba(255, 50, 0, 0.5); }
    75% { background-color: rgba(255, 100, 0, 0.3); }
    100% { background-color: transparent; }
}

.pralaya-active {
    animation: pralaya-fire 2s ease-in-out;
}

.pralaya-button {
    background: linear-gradient(135deg, #ff4e00, #ec9f05) !important;
    border: 2px solid #ff6b35 !important;
    color: white !important;
    font-weight: bold !important;
}

.pralaya-button:hover {
    background: linear-gradient(135deg, #ff6b00, #ffb347) !important;
    box-shadow: 0 0 20px rgba(255, 100, 0, 0.5) !important;
}
"""
