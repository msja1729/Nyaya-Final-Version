"""Nyaya Sahayak — Legal RAG assistant with DPDP Act 2023 compliance features.

Features:
- Trial of Justice: Multi-agent RAG with Kira/L/Shinigami personas
- Chitragupta's Secret: Steganographic data portability
- Agni-Pariksha: T&C/Privacy Policy Scanner
- Pralaya: Instant data erasure (Right to Erasure)
- Dharma-Guard: Intent firewall for query filtering
"""

__version__ = "0.2.0"

# Expose main modules
from nyaya_dhwani.intent_firewall import check_query, get_firewall
from nyaya_dhwani.trial_of_justice import run_trial
from nyaya_dhwani.tc_scanner import analyze_policy, format_scan_result
from nyaya_dhwani.data_erasure import erase_session, get_session

# Optional steganography (requires Pillow + cryptography)
try:
    from nyaya_dhwani.steganography import create_portable_export, import_from_image
except ImportError:
    create_portable_export = None
    import_from_image = None

__all__ = [
    "check_query",
    "get_firewall",
    "run_trial",
    "analyze_policy",
    "format_scan_result",
    "erase_session",
    "get_session",
    "create_portable_export",
    "import_from_image",
]
