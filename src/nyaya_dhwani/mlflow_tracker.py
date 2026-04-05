"""MLflow experiment tracking for Nyaya Dhwani RAG quality.

Tracks:
- Query parameters (language, question length)
- Response metrics (latency, length, sources)
- RAG quality (retrieval relevance, translation accuracy)
- System performance (memory, tokens)

Complements the existing RAG pipeline with experiment tracking for
continuous improvement and A/B testing.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import MLflow, but don't fail if not available
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.warning("MLflow not installed - tracking disabled")


class RAGExperimentTracker:
    """Tracks RAG query experiments with MLflow."""

    def __init__(self, experiment_name: str = "/Shared/nyaya-dhwani-rag"):
        """Initialize tracker.

        Args:
            experiment_name: MLflow experiment name/path
        """
        self.enabled = MLFLOW_AVAILABLE
        if self.enabled:
            try:
                mlflow.set_experiment(experiment_name)
                logger.info(f"MLflow tracking enabled: {experiment_name}")
            except Exception as e:
                logger.warning(f"MLflow setup failed: {e}")
                self.enabled = False
        else:
            logger.info("MLflow tracking disabled (not installed)")

    def log_query(
        self,
        question: str,
        language: str,
        response: str,
        sources: list[dict[str, Any]],
        latency: float,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a single RAG query with metrics.

        Args:
            question: User question text
            language: Selected language code
            response: Generated response text
            sources: Retrieved source documents
            latency: Response time in seconds
            metadata: Additional tracking data
        """
        if not self.enabled:
            return

        try:
            with mlflow.start_run():
                # Query parameters
                mlflow.log_param("language", language)
                mlflow.log_param("question_length", len(question))
                mlflow.log_param("question_words", len(question.split()))

                # Response metrics
                mlflow.log_metric("response_latency_sec", latency)
                mlflow.log_metric("response_length", len(response))
                mlflow.log_metric("response_words", len(response.split()))
                mlflow.log_metric("num_sources_retrieved", len(sources))

                # Retrieval quality
                if sources:
                    avg_score = sum(s.get('score', 0) for s in sources) / len(sources)
                    mlflow.log_metric("avg_retrieval_score", avg_score)
                    mlflow.log_metric("top_source_score", max(
                        s.get('score', 0) for s in sources
                    ))

                # Additional metadata
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (int, float)):
                            mlflow.log_metric(key, value)
                        else:
                            mlflow.log_param(key, str(value))

                # Log artifacts
                mlflow.log_text(question, "question.txt")
                mlflow.log_text(response, "response.txt")
                if sources:
                    sources_text = "\n\n".join(
                        f"Source {i+1} (score={s.get('score', 0):.3f}):\n{s.get('text', '')}"
                        for i, s in enumerate(sources[:3])
                    )
                    mlflow.log_text(sources_text, "sources.txt")

        except Exception as e:
            logger.error(f"MLflow logging failed: {e}")

    def log_translation(
        self,
        source_text: str,
        target_text: str,
        source_lang: str,
        target_lang: str,
        latency: float,
    ) -> None:
        """Log translation quality metrics.

        Args:
            source_text: Original text
            target_text: Translated text
            source_lang: Source language code
            target_lang: Target language code
            latency: Translation time in seconds
        """
        if not self.enabled:
            return

        try:
            with mlflow.start_run(run_name=f"translation_{source_lang}_to_{target_lang}"):
                mlflow.log_param("source_lang", source_lang)
                mlflow.log_param("target_lang", target_lang)
                mlflow.log_param("source_length", len(source_text))
                mlflow.log_metric("translation_latency_sec", latency)
                mlflow.log_metric("target_length", len(target_text))
                mlflow.log_metric("length_ratio", len(target_text) / max(1, len(source_text)))

        except Exception as e:
            logger.error(f"MLflow translation logging failed: {e}")

    def log_voice_interaction(
        self,
        stt_latency: float,
        tts_latency: float,
        audio_duration_sec: float,
        language: str,
    ) -> None:
        """Log voice interaction metrics.

        Args:
            stt_latency: Speech-to-text time
            tts_latency: Text-to-speech time
            audio_duration_sec: Input audio duration
            language: Language code
        """
        if not self.enabled:
            return

        try:
            with mlflow.start_run(run_name=f"voice_{language}"):
                mlflow.log_param("language", language)
                mlflow.log_metric("stt_latency_sec", stt_latency)
                mlflow.log_metric("tts_latency_sec", tts_latency)
                mlflow.log_metric("audio_duration_sec", audio_duration_sec)
                mlflow.log_metric("total_voice_latency_sec", stt_latency + tts_latency)
                if audio_duration_sec > 0:
                    mlflow.log_metric("realtime_factor", 
                                     (stt_latency + tts_latency) / audio_duration_sec)

        except Exception as e:
            logger.error(f"MLflow voice logging failed: {e}")


# Global tracker instance
_tracker: Optional[RAGExperimentTracker] = None


def get_tracker() -> RAGExperimentTracker:
    """Get or create global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = RAGExperimentTracker()
    return _tracker


def log_query(*args, **kwargs) -> None:
    """Convenience function for logging queries."""
    get_tracker().log_query(*args, **kwargs)


def log_translation(*args, **kwargs) -> None:
    """Convenience function for logging translations."""
    get_tracker().log_translation(*args, **kwargs)


def log_voice_interaction(*args, **kwargs) -> None:
    """Convenience function for logging voice interactions."""
    get_tracker().log_voice_interaction(*args, **kwargs)
