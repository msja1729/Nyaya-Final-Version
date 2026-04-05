# MLflow Integration Guide

## Add to app/main.py

### Step 1: Import the tracker

Add to the top of `app/main.py` after existing imports:

```python
from nyaya_dhwani.mlflow_tracker import log_query, log_translation, log_voice_interaction
import time
```

### Step 2: Wrap the answer function

Find the `answer_question()` function and wrap it with tracking:

```python
def answer_question(question: str, language: str, session_id: str = "") -> tuple[str, list]:
    """Answer question with MLflow tracking."""
    start_time = time.time()
    
    # Existing RAG logic here
    # ... (keep all existing code)
    
    # At the end, add tracking
    latency = time.time() - start_time
    
    try:
        log_query(
            question=question,
            language=language,
            response=response_text,
            sources=sources,
            latency=latency,
            metadata={
                "session_id": session_id[:8] if session_id else "anonymous",
                "used_voice": False,  # Set based on input method
            }
        )
    except Exception as e:
        logger.warning(f"MLflow tracking failed: {e}")
    
    return response_text, sources
```

### Step 3: Track translations (optional)

If you have a separate translation function:

```python
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    start_time = time.time()
    
    # Existing translation code
    translated = sarvam_client.translate(text, source_lang, target_lang)
    
    latency = time.time() - start_time
    log_translation(text, translated, source_lang, target_lang, latency)
    
    return translated
```

### Step 4: Track voice interactions (optional)

For voice input/output:

```python
def process_voice_query(audio_file, language: str) -> tuple[str, str]:
    stt_start = time.time()
    question = sarvam_client.speech_to_text(audio_file, language)
    stt_latency = time.time() - stt_start
    
    # Get answer
    response, sources = answer_question(question, language)
    
    tts_start = time.time()
    audio_response = sarvam_client.text_to_speech(response, language)
    tts_latency = time.time() - tts_start
    
    # Track voice metrics
    log_voice_interaction(
        stt_latency=stt_latency,
        tts_latency=tts_latency,
        audio_duration_sec=get_audio_duration(audio_file),
        language=language
    )
    
    return question, audio_response
```

## Requirements Update

Add MLflow to dependencies:

```bash
# In requirements.txt or pyproject.toml
mlflow>=2.8.0
```

## Testing Locally

```bash
# Set MLflow tracking URI (optional - defaults to local)
export MLFLOW_TRACKING_URI=databricks

# Run the app
python app/main.py

# View experiments
mlflow ui
# Then open http://localhost:5000
```

## On Databricks

MLflow is pre-installed. Experiments will automatically appear in:
- Workspace → Machine Learning → Experiments
- Look for `/Shared/nyaya-dhwani-rag`

## Viewing Results

```python
# In a notebook
import mlflow

mlflow.set_experiment("/Shared/nyaya-dhwani-rag")

# Get all runs
runs = mlflow.search_runs()

# Show metrics
display(runs[["params.language", "metrics.response_latency_sec", 
              "metrics.num_sources_retrieved", "metrics.avg_retrieval_score"]])

# Plot latency by language
import matplotlib.pyplot as plt
runs.groupby("params.language")["metrics.response_latency_sec"].mean().plot(kind="bar")
plt.title("Average Response Latency by Language")
plt.ylabel("Seconds")
plt.show()
```

## What Gets Tracked

### Per Query
- Language selected
- Question length (chars, words)
- Response length
- Number of sources retrieved
- Average retrieval score
- Response latency
- Question & response text (as artifacts)
- Top 3 sources (as artifact)

### Per Translation (if enabled)
- Source/target languages
- Text lengths
- Translation latency
- Length ratio (translation expansion)

### Per Voice Interaction (if enabled)
- STT latency
- TTS latency
- Audio duration
- Real-time factor (latency / duration)

## Benefits

1. **A/B Testing**: Compare different prompts, retrieval strategies
2. **Performance Monitoring**: Track latency over time
3. **Quality Metrics**: Measure retrieval relevance
4. **Language Analysis**: Which languages perform best
5. **Debugging**: Full query logs for error analysis

## Hackathon Impact

**Adds 5 points to Databricks Usage score (15% → 20%)**

Shows advanced platform usage:
- ✅ Experiment tracking
- ✅ Parameter logging
- ✅ Metric comparison
- ✅ Artifact storage
- ✅ Production monitoring
