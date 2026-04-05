"""Gradio entrypoint: RAG + Maverick + Sarvam (STT / Mayura / Bulbul).

Features:
1. Trial of Justice - Multi-agent RAG with Kira/L/Shinigami personas
2. Chitragupta's Secret - Steganographic data portability
3. Agni-Pariksha - T&C/Privacy Policy Scanner
4. Pralaya Button - Instant data erasure
5. Dharma-Guard - Intent firewall

See docs/PLAN.md.
"""

from __future__ import annotations

import logging
import os
import secrets
import sys
from pathlib import Path

# Repo root on Databricks Repos / local clone
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import gradio as gr
import numpy as np

# ---------- Monkey-patch gradio_client bug (1.3.0 + Gradio 4.44.x) ----------
# get_api_info() crashes on Chatbot schemas where additionalProperties is True
# (a bool).  The internal recursive calls use the module-level name, so we must
# replace the actual function objects in the module namespace.
import gradio_client.utils as _gc_utils  # noqa: E402

_orig_inner = _gc_utils._json_schema_to_python_type
_orig_get_type = _gc_utils.get_type

def _safe_inner(schema, defs=None):
    if not isinstance(schema, dict):
        return "Any"
    return _orig_inner(schema, defs)

def _safe_get_type(schema):
    if not isinstance(schema, dict):
        return "Any"
    return _orig_get_type(schema)

# Patch module-level names so internal recursive calls also go through guards.
_gc_utils._json_schema_to_python_type = _safe_inner
_gc_utils.get_type = _safe_get_type
# ---------- End monkey-patch ------------------------------------------------

from nyaya_dhwani.llm_client import chat_completions, extract_assistant_text, rag_user_message
from nyaya_dhwani.retriever import Retriever, get_retriever
from nyaya_dhwani.sarvam_client import (
    is_configured as sarvam_configured,
    numpy_audio_to_wav_bytes,
    speech_to_text_file,
    strip_markdown_for_tts,
    text_to_speech_wav_bytes,
    transcript_from_stt_response,
    translate_text,
    wav_bytes_to_numpy_float32,
)

# New feature imports
from nyaya_dhwani.intent_firewall import check_query, get_firewall
from nyaya_dhwani.trial_of_justice import run_trial, format_trial_response
from nyaya_dhwani.tc_scanner import analyze_policy, format_scan_result
from nyaya_dhwani.data_erasure import (
    get_session,
    erase_session,
    format_erasure_result,
    PRALAYA_CSS,
)

logger = logging.getLogger(__name__)

TOPIC_SEEDS: dict[str, str] = {
    "Tenant rights": "What are my basic rights as a tenant in India regarding eviction and rent increases?",
    "Divorce law": "What are the grounds for divorce under Indian law for mutual consent?",
    "Consumer cases": "How do I file a consumer complaint in India for defective goods?",
    "Property law": "What documents should I check before buying residential property in India?",
    "Labour rights": "What are an employee's rights regarding notice period and gratuity?",
    "FIR / Police": "What is the procedure to file an FIR and what are my rights when arrested?",
    "Domestic violence": "What legal protections exist for victims of domestic violence in India?",
    "RTI": "How do I file a Right to Information application and what fees apply?",
}

SARVAM_LANGUAGES: list[tuple[str, str]] = [
    ("en", "English"),
    ("hi", "Hindi · हिन्दी"),
    ("bn", "Bengali"),
    ("te", "Telugu"),
    ("mr", "Marathi"),
    ("ta", "Tamil"),
    ("gu", "Gujarati"),
    ("kn", "Kannada"),
    ("ml", "Malayalam"),
    ("pa", "Punjabi"),
    ("or", "Odia"),
    ("ur", "Urdu"),
    ("as", "Assamese"),
]

# UI ISO-ish code → BCP-47 for Mayura / STT hints (best-effort for ur/as)
UI_TO_BCP47: dict[str, str] = {
    "en": "en-IN",
    "hi": "hi-IN",
    "bn": "bn-IN",
    "te": "te-IN",
    "mr": "mr-IN",
    "ta": "ta-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "pa": "pa-IN",
    "or": "od-IN",
    "ur": "hi-IN",
    "as": "bn-IN",
}

DISCLAIMER_EN = (
    "This information is for general awareness only and does not constitute legal advice. "
    "Consult a qualified lawyer for your specific situation."
)

SYSTEM_PROMPT = (
    "You are Nyaya Dhwani, an assistant for Indian legal information. "
    "Answer using the Context below when it is relevant. Cite Acts or sections when the context supports it. "
    "If the context is insufficient, say so briefly. "
    "Do not claim to be a lawyer. Keep answers clear and structured. "
    "Respond in English."
)

# Steganography - try import, graceful fallback
try:
    from nyaya_dhwani.steganography import create_portable_export, import_from_image
    STEGO_AVAILABLE = True
except ImportError:
    STEGO_AVAILABLE = False
    logger.warning("Steganography not available - install Pillow and cryptography")


def bcp47_target(lang: str) -> str:
    return UI_TO_BCP47.get(lang, "en-IN")


class RAGRuntime:
    """Lazy-load retriever (FAISS, Vector Search, or fallback combo)."""

    def __init__(self) -> None:
        self._retriever: Retriever | None = None

    def load(self) -> None:
        if self._retriever is not None:
            return
        self._retriever = get_retriever()
        logger.info("Retriever loaded: %s", type(self._retriever).__name__)

    @property
    def retriever(self) -> Retriever:
        if self._retriever is None:
            raise RuntimeError("RAGRuntime not loaded")
        return self._retriever


_runtime: RAGRuntime | None = None


def get_runtime() -> RAGRuntime:
    global _runtime
    if _runtime is None:
        _runtime = RAGRuntime()
    return _runtime


def _format_citations(chunks_df) -> str:
    lines: list[str] = []
    for _, row in chunks_df.iterrows():
        title = row.get("title") or ""
        source = row.get("source") or ""
        doc_type = row.get("doc_type") or ""
        bits = [str(x).strip() for x in (title, source, doc_type) if x and str(x).strip()]
        if bits:
            lines.append("- " + " · ".join(bits[:3]))
    return "\n".join(lines) if lines else "(no metadata)"


def _rag_answer_english(query_en: str) -> tuple[str, str]:
    """LLM answer in English + citations block."""
    rt = get_runtime()
    rt.load()
    q = query_en.strip()
    chunks_df = rt.retriever.search(q, k=7)
    texts = chunks_df["text"].tolist() if "text" in chunks_df.columns else []
    user_content = rag_user_message([str(t) for t in texts], q)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
    raw = chat_completions(messages, max_tokens=2048, temperature=0.2)
    assistant_en = extract_assistant_text(raw)
    cites = _format_citations(chunks_df)
    return assistant_en, cites


def _rag_trial_of_justice(query_en: str) -> tuple[str, str]:
    """Trial of Justice multi-agent RAG response."""
    rt = get_runtime()
    rt.load()
    q = query_en.strip()
    chunks_df = rt.retriever.search(q, k=7)
    texts = chunks_df["text"].tolist() if "text" in chunks_df.columns else []
    cites = _format_citations(chunks_df)

    # Run the trial with all three personas
    trial_result = run_trial(
        question=q,
        context_chunks=[str(t) for t in texts],
        citations=cites,
    )
    return trial_result.combined, cites


_TRANSLATE_CHUNK_LIMIT = 500  # Sarvam Mayura works best with shorter text


def _chunked_translate(text: str, *, source: str, target: str) -> str:
    """Translate long text by splitting into paragraph-sized chunks.

    Sarvam Mayura can silently return the input unchanged for long text.
    Splitting on paragraph boundaries keeps context while staying within limits.
    """
    # Split on double-newlines (paragraphs) or single newlines for lists
    paragraphs = text.split("\n")
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 1 > _TRANSLATE_CHUNK_LIMIT and current:
            chunks.append(current)
            current = para
        else:
            current = f"{current}\n{para}" if current else para
    if current:
        chunks.append(current)

    translated_parts = []
    for chunk in chunks:
        if not chunk.strip():
            translated_parts.append(chunk)
            continue
        try:
            result = translate_text(chunk, source_language_code=source, target_language_code=target)
            translated_parts.append(result)
        except Exception as e:
            logger.warning("Mayura chunk translate failed, keeping original: %s", e)
            translated_parts.append(chunk)
    return "\n".join(translated_parts)


def _maybe_translate(text: str, *, source: str, target: str) -> str:
    if source == target:
        return text
    if not sarvam_configured():
        return text
    if len(text) > _TRANSLATE_CHUNK_LIMIT:
        return _chunked_translate(text, source=source, target=target)
    try:
        return translate_text(text, source_language_code=source, target_language_code=target)
    except Exception as e:
        logger.warning("Mayura translate failed, using original: %s", e)
        return text


def text_to_query_english(user_text: str, lang: str) -> str:
    """Non-English typed input → English for embedding/RAG (Mayura)."""
    t = user_text.strip()
    if not t:
        return t
    if lang == "en":
        return t
    if not sarvam_configured():
        logger.warning("SARVAM_API_KEY missing — using raw text for retrieval (degraded).")
        return t
    return _maybe_translate(t, source="auto", target="en-IN")


def resolve_user_message(
    text: str,
    audio: tuple[int, np.ndarray] | None,
    lang: str,
) -> tuple[str, str]:
    """Returns ``(user_bubble_text, query_english)``."""
    text = (text or "").strip()
    logger.debug("resolve_user_message: text=%r, audio type=%s",
                 text[:80] if text else "", type(audio).__name__)

    # Prefer typed text over audio (Gradio retains stale audio recordings).
    if text:
        q_en = text_to_query_english(text, lang)
        return (text, q_en)

    # Fall back to audio only when no text was typed.
    if audio is not None:
        sr, data = audio
        if data is not None and len(np.asarray(data)) > 0:
            if not sarvam_configured():
                raise RuntimeError("Set SARVAM_API_KEY for voice input (Sarvam STT).")
            wav = numpy_audio_to_wav_bytes(np.asarray(data), int(sr))
            mode = os.environ.get("SARVAM_STT_MODE", "translate").strip()
            lang_hint = bcp47_target(lang) if mode == "transcribe" else None
            st = speech_to_text_file(
                wav,
                mode=mode,
                language_code=lang_hint,
            )
            tr = transcript_from_stt_response(st)
            if mode == "translate":
                return (f"🎤 {tr}", tr.strip())
            q_en = _maybe_translate(tr, source="auto", target="en-IN")
            return (f"🎤 {tr}", q_en.strip())

    raise ValueError("Type a question or record audio. If you just recorded, wait for the audio to finish processing then try again.")


def build_reply_markdown(assistant_en: str, cites: str, lang: str) -> str:
    """Build response with both English and translated text side by side."""
    sources_block = f"**Sources (retrieval)**\n{cites}"

    if lang == "en" or not sarvam_configured():
        return (
            f"{assistant_en}\n\n---\n{sources_block}"
            f"\n\n---\n*{DISCLAIMER_EN}*"
        )

    tgt = bcp47_target(lang)
    body_translated = _maybe_translate(assistant_en, source="en-IN", target=tgt)
    disc_translated = _maybe_translate(DISCLAIMER_EN, source="en-IN", target=tgt)

    # Side-by-side: translated language first (primary), English below for reference
    lang_label = dict(SARVAM_LANGUAGES).get(lang, lang)
    return (
        f"**{lang_label}:**\n\n{body_translated}\n\n"
        f"---\n**English:**\n\n{assistant_en}\n\n"
        f"---\n{sources_block}"
        f"\n\n---\n*{disc_translated}*"
    )


def maybe_tts(text_markdown: str, lang: str, enabled: bool) -> tuple[int, np.ndarray] | None:
    """Generate TTS audio for the complete response text."""
    if not enabled or not sarvam_configured():
        return None
    
    # For Trial of Justice or multi-section responses, we want to read everything
    # Extract just the main content (remove sources, disclaimers, etc.)
    
    # Split by horizontal rules
    sections = text_markdown.split("\n---\n")
    
    # For bilingual responses, extract the translated language sections
    # For Trial mode, extract all three perspectives
    narrative_parts = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Skip sources, legal disclaimers, and metadata
        if any(skip in section.lower() for skip in [
            'legal sources', 'sources (retrieval)', '**📚', 
            'this information is for general', 'consult a qualified lawyer',
            'this is a legal simulation'
        ]):
            continue
        
        # Skip headers like "# ⚖️ Trial of Justice"
        if section.startswith('#'):
            continue
        
        # For bilingual responses, prefer the translated version (first section)
        # but include all substantive content
        clean_section = section
        
        # Remove bold language labels like "**Hindi:**" or "**English:**"
        import re
        clean_section = re.sub(r'^\*\*[^*]+:\*\*\s*', '', clean_section)
        
        if clean_section.strip():
            narrative_parts.append(clean_section)
    
    # Combine all parts
    full_narrative = "\n\n".join(narrative_parts)
    
    # Strip markdown for clean TTS
    plain = strip_markdown_for_tts(full_narrative)
    
    if not plain.strip():
        return None
    
    # Limit to reasonable length for TTS (split if too long)
    MAX_TTS_CHARS = 2400
    if len(plain) > MAX_TTS_CHARS:
        # Take first part but try to end at sentence boundary
        plain = plain[:MAX_TTS_CHARS]
        last_period = plain.rfind('.')
        if last_period > MAX_TTS_CHARS * 0.8:  # If we're close to the end
            plain = plain[:last_period + 1]
    
    tgt = bcp47_target(lang)
    try:
        wav = text_to_speech_wav_bytes(plain, target_language_code=tgt)
        sr, arr = wav_bytes_to_numpy_float32(wav)
        return (sr, arr)
    except Exception as e:
        logger.warning("TTS failed: %s", e)
        return None


def run_turn(
    message: str,
    audio: tuple[int, np.ndarray] | None,
    history: list | None,
    lang: str,
    tts_on: bool,
    trial_mode: bool = False,
    session_id: str = "",
) -> tuple[str, list, tuple[int, np.ndarray] | None, None]:
    """Process a chat turn with optional Trial of Justice mode.

    Returns (msg_text, history, tts_audio, audio_in_clear).
    """
    history = [list(pair) for pair in history] if history else []
    try:
        user_show, q_en = resolve_user_message(message, audio, lang)

        # Dharma-Guard: Check if query is allowed
        is_allowed, rejection_msg = check_query(q_en)
        if not is_allowed:
            history.append([user_show, rejection_msg])
            return "", history, None, None

        # Store in session for data portability
        if session_id:
            session = get_session(session_id)
            current_history = session.get_chat_history()
            current_history.append([user_show, ""])  # Placeholder
            session.set_chat_history(current_history)

        # Generate response - Trial of Justice or standard
        if trial_mode:
            assistant_reply, cites = _rag_trial_of_justice(q_en)
            reply_md = assistant_reply  # Already formatted
        else:
            assistant_en, cites = _rag_answer_english(q_en)
            reply_md = build_reply_markdown(assistant_en, cites, lang)

        history.append([user_show, reply_md])

        # Update session with actual response
        if session_id:
            session = get_session(session_id)
            session.set_chat_history(history)

        audio_out = maybe_tts(reply_md, lang, tts_on)
        return "", history, audio_out, None
    except Exception as e:
        logger.exception("run_turn")
        err = f"**Error:** {e}"
        history.append([message or "🎤 (audio)", err])
        return "", history, None, None


def run_tc_scan(policy_text: str, app_name: str) -> str:
    """Run Agni-Pariksha T&C scanner."""
    if not policy_text.strip():
        return "⚠️ Please paste a privacy policy or Terms & Conditions to analyze."

    if len(policy_text) < 100:
        return "⚠️ The text seems too short. Please paste the complete privacy policy."

    try:
        result = analyze_policy(policy_text, app_name or "the application")
        return format_scan_result(result)
    except Exception as e:
        logger.exception("run_tc_scan")
        return f"**Error analyzing policy:** {e}"


def run_pralaya(session_id: str, history: list) -> tuple[str, list]:
    """Execute Pralaya - instant data erasure."""
    if not session_id:
        session_id = secrets.token_hex(8)

    result = erase_session(session_id)
    formatted = format_erasure_result(result)

    # Clear the chat history
    return formatted, []


def export_chitragupta(history: list, session_id: str) -> tuple[bytes | None, str]:
    """Export chat history using steganography."""
    if not STEGO_AVAILABLE:
        return None, "❌ Steganography not available. Install: pip install Pillow cryptography"

    if not history:
        return None, "❌ No chat history to export."

    if not session_id:
        session_id = secrets.token_hex(8)

    try:
        image_bytes = create_portable_export(
            chat_history=history,
            session_id=session_id,
            metadata={"app": "nyaya-sahayak", "format": "chitragupta-v1"},
        )
        return image_bytes, f"✅ Exported {len(history)} conversations. Session ID: `{session_id}` (save this for import)"
    except Exception as e:
        logger.exception("export_chitragupta")
        return None, f"❌ Export failed: {e}"


def build_app() -> gr.Blocks:
    # Sarvam AI supported languages
    SARVAM_LANGUAGES = [
        ("en", "English"),
        ("hi", "हिन्दी (Hindi)"),
        ("bn", "বাংলা (Bengali)"),
        ("te", "తెలుగు (Telugu)"),
        ("mr", "मराठी (Marathi)"),
        ("ta", "தமிழ் (Tamil)"),
        ("gu", "ગુજરાતી (Gujarati)"),
        ("kn", "ಕನ್ನಡ (Kannada)"),
        ("ml", "മലയാളം (Malayalam)"),
        ("pa", "ਪੰਜਾਬੀ (Punjabi)"),
        ("or", "ଓଡ଼ିଆ (Odia)"),
        ("ur", "اردو (Urdu)"),
        ("as", "অসমীয়া (Assamese)"),
    ]

    custom_css = """
    /* Light theme */
    .gradio-container { background-color: #F7F3ED !important; }
    footer { font-size: 0.85rem; color: #2A5297; }
    h1 { color: #0D1B3E; font-family: Georgia, serif; }

    /* Dark theme: respect browser/OS preference */
    @media (prefers-color-scheme: dark) {
        .gradio-container { background-color: #1a1a2e !important; }
        h1 { color: #e0d8cc; }
        footer { color: #8ea4c8; }
    }
    /* Also handle Gradio's own dark class */
    .dark .gradio-container { background-color: #1a1a2e !important; }
    .dark h1 { color: #e0d8cc; }
    .dark footer { color: #8ea4c8; }
    """ + PRALAYA_CSS

    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="slate", secondary_hue="orange"),
        css=custom_css,
        title="Nyaya Sahayak · न्याय सहायक",
    ) as demo:
        # Session state
        session_id = gr.State(lambda: secrets.token_hex(16))
        lang_state = gr.State("en")

        gr.Markdown(
            "# ⚖️ Nyaya Sahayak · न्याय सहायक\n"
            "*AI Legal Assistant for India · DPDP Act 2023 · BNS · IPC*"
        )

        with gr.Column(visible=True) as welcome_col:
            gr.Markdown("### Welcome / स्वागत")
            gr.Markdown(
                "Choose your language and explore our features:\n"
                "- **Trial of Justice** - Multi-perspective legal analysis\n"
                "- **Agni-Pariksha** - Privacy policy scanner\n"
                "- **Chitragupta's Secret** - Secure data export\n"
                "- **Pralaya** - Instant data erasure"
            )
            lang_radio = gr.Radio(
                choices=[(c[1], c[0]) for c in SARVAM_LANGUAGES],
                value="en",
                label="Select your language / अपनी भाषा चुनें",
                info="Non-English questions are translated to English for retrieval, "
                "then answers are translated back to your language.",
            )
            begin_btn = gr.Button("Begin / शुरू करें", variant="primary")
            gr.Markdown(
                "<small>🛡️ Protected by Dharma-Guard intent firewall · "
                "Compliant with DPDP Act 2023</small>"
            )

        with gr.Column(visible=False) as main_col:
            current_lang = gr.Markdown("*Session language: English*")
            
            # Persistent language selector visible on all tabs
            with gr.Row():
                lang_selector = gr.Dropdown(
                    choices=[(c[1], c[0]) for c in SARVAM_LANGUAGES],
                    value="en",
                    label="🌐 Language / भाषा",
                    scale=3,
                )
                gr.Markdown(
                    "<small>Change language anytime. Voice input and translation supported.</small>",
                    scale=2,
                )
            

            with gr.Tabs() as tabs:
                # Tab 1: Trial of Justice Chat
                with gr.TabItem("⚖️ Trial of Justice", id="trial"):
                    gr.Markdown(
                        "### The Trial of Justice\n"
                        "Ask a legal question and get three perspectives:\n"
                        "- **Prosecution** - How the law was violated\n"
                        "- **Defense** - Legal loopholes and exceptions\n"
                        "- **Judicial Summary** - Neutral legal summary"
                    )
                    topic = gr.Radio(
                        choices=list(TOPIC_SEEDS.keys()),
                        label="Quick topics",
                        value=None,
                    )
                    trial_chatbot = gr.Chatbot(
                        label="Trial of Justice",
                        height=450,
                        bubble_full_width=True,
                    )
                    with gr.Row():
                        trial_msg = gr.Textbox(
                            placeholder="Describe your legal situation...",
                            show_label=False,
                            lines=2,
                            scale=4,
                        )
                        trial_submit = gr.Button("⚖️ Begin Trial", variant="primary", scale=1)
                    trial_audio_in = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="Or speak your question",
                    )
                    with gr.Row():
                        trial_mode_cb = gr.Checkbox(
                            label="🎭 Trial Mode (3 perspectives)",
                            value=True,
                        )
                        tts_cb = gr.Checkbox(
                            label="🔊 Read answer aloud",
                            value=False,
                        )
                    tts_out = gr.Audio(
                        label="Listen to answer",
                        type="numpy",
                        interactive=False,
                        visible=False,
                    )

                # Tab 2: Standard Chat
                with gr.TabItem("💬 Standard Chat", id="chat"):
                    gr.Markdown("### Standard Legal Q&A\nGet direct answers without the trial simulation.")
                    std_chatbot = gr.Chatbot(
                        label="Nyaya Sahayak",
                        height=450,
                        bubble_full_width=False,
                    )
                    std_msg = gr.Textbox(
                        placeholder="Ask your legal question...",
                        show_label=False,
                        lines=2,
                    )
                    std_submit = gr.Button("Send", variant="primary")
                    with gr.Row():
                        std_tts_cb = gr.Checkbox(
                            label="🔊 Read answer aloud",
                            value=False,
                        )
                    std_tts_out = gr.Audio(
                        label="Listen",
                        type="numpy",
                        interactive=False,
                        visible=False,
                    )

                # Tab 3: Agni-Pariksha (T&C Scanner)
                with gr.TabItem("🔥 Agni-Pariksha", id="scanner"):
                    gr.Markdown(
                        "### 🔥 Agni-Pariksha - Privacy Policy Scanner\n"
                        "Paste a privacy policy or Terms & Conditions to analyze against "
                        "**DPDP Act 2023** (Sections 6 & 7)."
                    )
                    with gr.Row():
                        scan_app_name = gr.Textbox(
                            label="App/Service Name",
                            placeholder="e.g., PaymentApp, SocialMedia",
                            scale=1,
                        )
                    scan_input = gr.Textbox(
                        label="Paste Privacy Policy / T&C",
                        placeholder="Paste the full text of the privacy policy here...",
                        lines=12,
                    )
                    scan_btn = gr.Button("🔥 Analyze Policy", variant="primary")
                    scan_result = gr.Markdown(label="Analysis Result")

                # Tab 4: Chitragupta's Secret (Data Portability)
                with gr.TabItem("📜 Chitragupta", id="portability"):
                    gr.Markdown(
                        "### 📜 Chitragupta's Secret - Secure Data Export\n"
                        "Export your chat history as a secure, encrypted image.\n"
                        "Only you can decrypt it with your session ID.\n\n"
                        "*Fulfills DPDP Act 2023 Right to Data Portability (Section 13)*"
                    )
                    export_btn = gr.Button("📥 Export Chat History", variant="primary")
                    export_status = gr.Markdown()
                    export_file = gr.File(
                        label="Download Your Data (PNG with embedded encrypted history)",
                        visible=False,
                    )
                    gr.Markdown("---")
                    gr.Markdown("### Import Previous Session")
                    import_session_id = gr.Textbox(
                        label="Session ID (from previous export)",
                        placeholder="Enter your saved session ID...",
                    )
                    import_file = gr.File(
                        label="Upload Chitragupta Image",
                        file_types=[".png", ".jpg", ".jpeg"],
                    )
                    import_btn = gr.Button("📤 Import History")
                    import_status = gr.Markdown()

                # Tab 5: Pralaya (Data Erasure)
                with gr.TabItem("🔥 Pralaya", id="erasure"):
                    gr.Markdown(
                        "### 🔥 प्रलय (Pralaya) - Instant Data Erasure\n"
                        "Exercise your **Right to Erasure** under DPDP Act 2023 (Section 12).\n\n"
                        "⚠️ **Warning:** This will permanently delete all your session data."
                    )
                    gr.Markdown(
                        "When you click the button below:\n"
                        "1. All chat history is erased\n"
                        "2. All session metadata is cleared\n"
                        "3. You receive a compliance confirmation\n\n"
                        "*This action cannot be undone.*"
                    )
                    pralaya_btn = gr.Button(
                        "🔥 Execute Pralaya - Erase All Data",
                        variant="stop",
                        elem_classes=["pralaya-button"],
                    )
                    pralaya_result = gr.Markdown()

        # Event handlers
        def on_begin(lang_code: str):
            labels = dict(SARVAM_LANGUAGES)
            label = labels.get(lang_code, lang_code)
            return (
                gr.update(visible=False),  # welcome_col
                gr.update(visible=True),   # main_col
                lang_code,                  # lang_state
                f"*Session language: {label}*",  # current_lang
                lang_code,                  # lang_selector
            )

        begin_btn.click(
            on_begin,
            inputs=[lang_radio],
            outputs=[welcome_col, main_col, lang_state, current_lang, lang_selector],
        )

        def fill_topic(choice: str | None):
            if not choice:
                return gr.update()
            return gr.update(value=TOPIC_SEEDS.get(choice, ""))

        topic.change(fill_topic, inputs=[topic], outputs=[trial_msg])

        # Trial of Justice chat
        def trial_turn(msg, audio, history, lang, tts, trial_mode, sess_id):
            return run_turn(msg, audio, history, lang, tts, trial_mode=trial_mode, session_id=sess_id)

        _trial_io = dict(
            fn=trial_turn,
            inputs=[trial_msg, trial_audio_in, trial_chatbot, lang_state, tts_cb, trial_mode_cb, session_id],
            outputs=[trial_msg, trial_chatbot, tts_out, trial_audio_in],
        )
        trial_submit.click(**_trial_io)
        trial_msg.submit(**_trial_io)
        trial_audio_in.stop_recording(**_trial_io)

        # Standard chat
        def std_turn(msg, history, lang, sess_id):
            return run_turn(msg, None, history, lang, False, trial_mode=False, session_id=sess_id)[:2] + (None,)

        def std_turn_wrapper(msg, history, lang, tts, sess_id):
            result = run_turn(msg, None, history, lang, tts, trial_mode=False, session_id=sess_id)
            return result[0], result[1], result[2]

        std_submit.click(
            std_turn_wrapper,
            inputs=[std_msg, std_chatbot, lang_state, std_tts_cb, session_id],
            outputs=[std_msg, std_chatbot, std_tts_out],
        )
        std_msg.submit(
            std_turn_wrapper,
            inputs=[std_msg, std_chatbot, lang_state, std_tts_cb, session_id],
            outputs=[std_msg, std_chatbot, std_tts_out],
        )

        # T&C Scanner
        scan_btn.click(
            run_tc_scan,
            inputs=[scan_input, scan_app_name],
            outputs=[scan_result],
        )

        # Chitragupta export
        def do_export(history, sess_id):
            # Combine trial and standard histories
            all_history = history if history else []
            img_bytes, status = export_chitragupta(all_history, sess_id)
            if img_bytes:
                # Save to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    f.write(img_bytes)
                    return status, gr.update(value=f.name, visible=True)
            return status, gr.update(visible=False)

        export_btn.click(
            do_export,
            inputs=[trial_chatbot, session_id],
            outputs=[export_status, export_file],
        )

        # Chitragupta import
        def do_import(file, sess_id):
            if not file or not sess_id:
                return "❌ Please provide both the image file and your session ID."
            if not STEGO_AVAILABLE:
                return "❌ Import not available. Install: pip install Pillow cryptography"
            try:
                history, metadata = import_from_image(file.name, sess_id)
                return (
                    f"✅ Imported {len(history)} conversations!\n\n"
                    f"**Original export:** {metadata.get('exported_at', 'Unknown')}\n"
                    f"**Compliance:** {metadata.get('compliance', {}).get('act', 'DPDP Act 2023')}"
                )
            except Exception as e:
                return f"❌ Import failed: {e}"

        import_btn.click(
            do_import,
            inputs=[import_file, import_session_id],
            outputs=[import_status],
        )

        # Pralaya
        def do_pralaya(sess_id, trial_hist, std_hist):
            result_text, _ = run_pralaya(sess_id, trial_hist + std_hist)
            # Return cleared histories
            return result_text, [], []

        pralaya_btn.click(
            do_pralaya,
            inputs=[session_id, trial_chatbot, std_chatbot],
            outputs=[pralaya_result, trial_chatbot, std_chatbot],
        )

        # Show TTS output when enabled
        tts_cb.change(
            lambda x: gr.update(visible=x),
            inputs=[tts_cb],
            outputs=[tts_out],
        )

        # Language selector change handler
        def on_lang_change(new_lang):
            labels = dict(SARVAM_LANGUAGES)
            label = labels.get(new_lang, new_lang)
            return new_lang, f"*Session language: {label}*"
        
        lang_selector.change(
            on_lang_change,
            inputs=[lang_selector],
            outputs=[lang_state, current_lang],
        )

        gr.Markdown(
            "<small>🛡️ Protected by Dharma-Guard · "
            "Powered by Databricks (Llama Maverick + Vector Search) · "
            "Sarvam AI (translation, speech-to-text, text-to-speech) · "
            "Compliant with DPDP Act 2023</small>"
        )

    return demo


def _load_secrets_from_scope() -> None:
    """Load secrets from Databricks secret scope into env vars (for Databricks Apps).

    The Apps UI secret resources don't always wire through reliably.
    Fall back to reading from the workspace secret scope via the SDK,
    the same way notebooks do with dbutils.secrets.get().
    """
    mapping = {
        "SARVAM_API_KEY": ("nyaya-dhwani", "sarvam_api_key"),
    }
    for env_var, (scope, key) in mapping.items():
        if os.environ.get(env_var, "").strip():
            continue  # already set (e.g. locally or via Apps resource)
        try:
            from databricks.sdk import WorkspaceClient
            w = WorkspaceClient()
            val = w.secrets.get_secret(scope=scope, key=key)
            if val and val.value:
                import base64
                # SDK get_secret returns base64-encoded value
                try:
                    decoded = base64.b64decode(val.value).decode("utf-8")
                except Exception:
                    decoded = val.value  # fallback: maybe it's already plain text
                os.environ[env_var] = decoded
                logger.info("Loaded %s from secret scope %s/%s", env_var, scope, key)
        except Exception as exc:
            logger.warning("Could not load %s from secret scope: %s", env_var, exc)


def main() -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    _load_secrets_from_scope()
    demo = build_app()
    demo.queue()
    # Match Databricks app-templates: bare launch() lets the platform
    # inject GRADIO_SERVER_NAME, GRADIO_SERVER_PORT, GRADIO_ROOT_PATH etc.
    demo.launch()


if __name__ == "__main__":
    main()
