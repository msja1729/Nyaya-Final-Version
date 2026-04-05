# ⚖️ Nyaya Sahayak (न्याय सहायक)

**Your AI-Powered Legal Assistant for Indian Law**

A comprehensive multilingual legal information system that makes Indian law accessible to everyone — from citizens seeking quick legal guidance to lawyers researching case precedents. Built with cutting-edge AI technologies including RAG (Retrieval-Augmented Generation), advanced speech recognition, and neural machine translation.

> **⚠️ Important Disclaimer:** This is an information tool, not a substitute for professional legal advice. Always consult a qualified lawyer for specific legal situations.

---

## 📖 Table of Contents

- [What is Nyaya Sahayak?](#what-is-nyaya-sahayak)
- [Quick Start Demo](#quick-start-demo)
- [Key Features](#key-features)
- [How It Works (For Everyone)](#how-it-works-for-everyone)
- [Technical Architecture (For Developers)](#technical-architecture-for-developers)
- [Technology Stack](#technology-stack)
- [Setup & Reproduction Guide](#setup--reproduction-guide)
- [Feature Guide](#feature-guide)
- [Development](#development)
- [Repository Structure](#repository-structure)

---

## 🎯 What is Nyaya Sahayak?

**For Everyone:**
Nyaya Sahayak is like having a knowledgeable legal assistant available 24/7. You can ask questions about Indian law in your own language (13 Indian languages supported!), and get easy-to-understand answers with references to actual legal documents. Whether you want to know your rights, understand a law, or get clarification on legal procedures, Nyaya Sahayak is here to help.

**For Developers:**
A production-grade Gradio application deployed on Databricks, leveraging RAG architecture with FAISS vector search, Llama 4 Maverick LLM, and Sarvam AI's multilingual capabilities. Implements advanced features including conversational memory, multi-turn dialogue, encrypted chat export/import, and real-time audio processing with neural speech synthesis.

---

## 🚀 Quick Start Demo

Once deployed, try these example prompts to see Nyaya Sahayak in action!

### **Trial of Justice Mode** (⚖️ Adversarial Analysis)

Try asking complex legal questions where multiple perspectives exist:

1. **English:** 
   ```
   "Can I be arrested without a warrant? What are my rights?"
   ```

2. **Hindi (हिन्दी):** 
   ```
   "क्या मुझे बिना वारंट के गिरफ्तार किया जा सकता है?"
   ```
   *(Can I be arrested without a warrant?)*

3. **Tamil (தமிழ்):**
   ```
   "வீட்டில் சோதனை நடத்த வாரண்ட் தேவையா?"
   ```
   *(Is a warrant required to search my house?)*

**Expected Output:**
- **PROSECUTION:** Arguments for why arrest/search may be lawful (with BNS sections)
- **DEFENSE:** Counter-arguments for citizen rights (with constitutional references)
- **JUDICIAL SUMMARY:** Balanced analysis of both perspectives

---

### **Standard Chat Mode** (💬 Direct Q&A)

Try these quick legal lookups:

4. **Section Lookup:**
   ```
   "What is Section 302 BNS? What is the punishment?"
   ```

5. **Procedure Question:**
   ```
   "How do I file an FIR online in India?"
   ```

6. **Rights Question:**
   ```
   "What are my rights if I'm called for police interrogation?"
   ```

**Expected Output:**
- Direct answer with citations to relevant BNS/IPC/CrPC sections
- References to court judgments (if applicable)
- Practical guidance

---

### **Voice Demo** (🎤 Speech + 🔊 TTS)

1. **Select Language:** Choose Hindi, Tamil, or any of 13 supported languages
2. **Click Microphone 🎤**
3. **Speak Your Question:** "मुझे गिरफ्तार करने के लिए वारंट की आवश्यकता है क्या?"
4. **Stop Recording ⏹️** → Watch automatic transcription and translation!
5. **Enable TTS 🔊** → Listen to the answer in your language

**Processing Flow You'll See:**
```
🟣 Processing audio... (Purple animation)
   ↓
🟢 Translated: "Is a warrant required to arrest me?" (Green animation)
   ↓
💬 Answer appears in chat with legal references
   ↓
🔊 Audio response plays in your language
```

---

### **Chitragupta Export/Import Demo** (📜 Encrypted Chat History)

**Export Your Chats:**
```
1. Go to "Chitragupta" tab
2. Note your Session ID: e.g., "a7f3e9c2b1d4..."
3. Click "Export Chat History"
4. Download the PNG image (looks like a normal image, but contains hidden encrypted data!)
```

**Import on Another Device:**
```
1. Upload the PNG image
2. Enter Session ID: "a7f3e9c2b1d4..."
3. Click "Import History"
4. Download auto-generated PDF with conversation history
```

**Try This:** Export, close the app, reopen, and import — your entire conversation is restored!

---

### **Architecture Diagram** (For Understanding Data Flow)

```
USER QUESTION (any of 13 languages)
   ↓
[Sarvam Mayura] → Translate to English
   ↓
[FAISS Vector Search] → Find relevant BNS/IPC sections
   ↓
[Llama 4 Maverick on Databricks AI Gateway] → Generate answer with RAG context
   ↓
[Sarvam Mayura] → Translate back to user's language
   ↓
[Sarvam Bulbul (optional)] → Speak answer aloud
   ↓
ANSWER WITH LEGAL CITATIONS
```

---

## ✨ Key Features

### 1. **⚖️ Trial of Justice** (Adversarial Legal Analysis)

**What it does (Simple):** 
Presents legal arguments from two different perspectives — like having two lawyers debate your question. One side argues FOR, the other AGAINST, and then a judge summarizes both viewpoints. This helps you see all angles of a legal issue.

**Technical Details:**
- **Technology:** Structured prompt engineering with role-based LLM generation
- **LLM:** Databricks Llama 4 Maverick via AI Gateway
- **RAG Integration:** Retrieves relevant BNS/IPC sections using FAISS cosine similarity search
- **Output Format:** Markdown-formatted adversarial dialogue with:
  - `PROSECUTION` section: Arguments in favor/legal position A
  - `DEFENSE` section: Counter-arguments/legal position B
  - `JUDICIAL SUMMARY`: Balanced synthesis of both perspectives
- **Use Case:** Complex legal questions where multiple interpretations exist

**Example:**
```
User: "Can I be arrested for a social media post?"

PROSECUTION: Under BNS Section 505, if your post promotes enmity between groups...
DEFENSE: However, freedom of speech under Article 19(1)(a) protects...
JUDICIAL SUMMARY: The legality depends on content nature and intent...
```

### 2. **💬 Standard Chat** (Direct Q&A)

**What it does (Simple):**
Ask any legal question and get a straight answer with references to laws and court judgments. Like chatting with a legal expert.

**Technical Details:**
- **RAG Pipeline:** 
  1. Query embedding using `sentence-transformers/all-MiniLM-L6-v2`
  2. FAISS IndexFlatIP search (top-k=5) over 900+ legal text chunks
  3. Context injection into Llama prompt
  4. Citation extraction and source attribution
- **Response Format:** Plain text with inline citations
- **Optimization:** Cosine similarity threshold = 0.3 for relevance filtering

### 3. **🌍 13-Language Support**

**What it does (Simple):**
Speak or type in ANY of these languages:
- English, हिन्दी (Hindi), বাংলা (Bengali), తెలుగు (Telugu)
- मराठी (Marathi), தமிழ் (Tamil), ગુજરાતી (Gujarati), ಕನ್ನಡ (Kannada)
- മലയാളം (Malayalam), ਪੰਜਾਬੀ (Punjabi), ଓଡ଼ିଆ (Odia), اردو (Urdu), অসমীয়া (Assamese)

The system automatically translates your question to English, processes it, and translates the answer back to your language!

**Technical Details:**
- **Neural Machine Translation:** Sarvam Mayura API (transformer-based seq2seq model)
- **Translation Pipeline:**
  ```
  User Language → Mayura Translate → English
  ↓
  RAG + LLM Processing (English)
  ↓
  English Response → Mayura Translate → User Language
  ```
- **BCP-47 Language Codes:** Proper locale mapping (e.g., `hi-IN`, `ta-IN`)
- **Fallback:** If translation fails, defaults to English processing
- **Quality:** Bilingual display (English + translated response side-by-side)

### 4. **🎤 Voice Input & Output**

**What it does (Simple):**
Too lazy to type? Just speak! Click the microphone, ask your question in any supported language, and the system will:
1. Understand your speech
2. Translate it to English
3. Find the answer
4. Speak it back to you in your language!

**Technical Details:**

**Speech-to-Text (STT):**
- **Model:** Sarvam Saaras (multilingual ASR - Automatic Speech Recognition)
- **Mode:** `translate` (auto-translates to English) or `transcribe` (preserves original language)
- **Audio Processing:**
  - Input: NumPy array from Gradio microphone
  - Conversion: WAV format (16kHz, mono)
  - API: Sarvam STT REST endpoint
- **Auto-submit:** On recording stop, audio is automatically:
  1. Transcribed by Saaras
  2. Translated to English
  3. Submitted to the chat (no button click needed!)

**Text-to-Speech (TTS):**
- **Model:** Sarvam Bulbul (neural voice synthesis)
- **Voice Quality:** Natural-sounding, language-specific voices
- **Modes:** 
  - Full response TTS
  - Smart truncation (up to 4000 chars, prioritizes verdict/judicial summary)
- **Output:** MP3/WAV audio playback in Gradio interface

**Loading Animations:**
- **Processing State:** Purple gradient with pulse animation
- **Success State:** Green gradient with translated text display
- **Error State:** Red gradient with troubleshooting hints
- **CSS Keyframes:** Smooth fade-in (0.3s), pulse (1.5s), mic icon pulse (1s)

### 5. **📜 Chitragupta** (Export/Import with Encryption)

**What it does (Simple):**
Named after the Hindu deity who records all deeds, Chitragupta lets you save your entire conversation history securely. Your chats are encrypted and hidden inside an image (steganography!). Only you can unlock them with your secret Session ID.

**Why it matters:** Your legal questions are private. This complies with India's Digital Personal Data Protection (DPDP) Act 2023 — you own your data and can take it anywhere.

**Technical Details:**
- **Steganography:** LSB (Least Significant Bit) embedding in PNG images
- **Encryption:** AES-256-CBC with PBKDF2 key derivation
- **Key:** Session ID (unique per user session, 32-hex token)
- **Data Structure:**
  ```json
  {
    "chat_history": [[user_msg, assistant_msg], ...],
    "metadata": {
      "exported_at": "ISO timestamp",
      "session_id": "encrypted_hash",
      "compliance": {"act": "DPDP Act 2023", "right": "Data Portability"}
    }
  }
  ```
- **Security:** No server-side storage, end-to-end encrypted
- **Import:** Decrypts image using Session ID, restores full chat history

**Export Flow:**
```
Chat History → JSON serialization → AES encryption → LSB embedding → PNG image
```

**Import Flow:**
```
PNG image → LSB extraction → AES decryption → JSON parsing → Chat restoration
```

### 6. **📄 PDF Export** (Professional Documentation)

**What it does (Simple):**
When you import your chat history, the system automatically generates a beautiful PDF document with:
- Your questions and answers
- Separate sections for Trial of Justice and Standard Chat
- Timestamps and session info
- Professional formatting for printing or sharing

**Technical Details:**
- **Library:** ReportLab (Python PDF generation)
- **Page Layout:** A4 with 0.75" margins
- **Smart Segregation:**
  - Detects chat type by keywords (`PROSECUTION`, `DEFENSE`, `JUDICIAL SUMMARY`)
  - Section 1: ⚖️ Trial of Justice conversations
  - Section 2: 💬 Standard Chat conversations
- **Styling:**
  - Title: 24pt Helvetica-Bold, centered
  - Headings: 16pt blue (#0066cc)
  - Questions: 10pt bold, indented
  - Answers: 10pt justified, indented
  - Metadata: 9pt gray, compliance footer
- **Content Processing:**
  - Markdown stripping (removes `**`, `*`, `__`, etc.)
  - Auto-truncation for very long responses (3000 char limit)
  - Q&A numbering for easy reference

**PDF Structure:**
```
┌─────────────────────────────────┐
│ ⚖️ Nyaya Sahayak · न्याय सहायक  │
│ Chat History Export              │
│─────────────────────────────────│
│ Metadata (Session ID, Date)     │
│─────────────────────────────────│
│ ⚖️ Trial of Justice              │
│   Q1: [question]                │
│   A1: [adversarial analysis]    │
│─────────────────────────────────│
│ 💬 Standard Chat                 │
│   Q1: [question]                │
│   A1: [direct answer]           │
│─────────────────────────────────│
│ DPDP Act 2023 Compliance Note   │
└─────────────────────────────────┘
```

### 7. **🗑️ Pralaya** (Right to be Forgotten)

**What it does (Simple):**
Named after the Hindu concept of cosmic dissolution, Pralaya lets you permanently delete your entire chat history. It's your right under DPDP Act 2023 to erase your data.

**Technical Details:**
- **DPDP Act 2023 Compliance:** Implements "Right to Erasure" (Section 12)
- **Session-based:** Each user has a unique session_id
- **Scope:** Deletes all conversations (both Trial and Standard chat)
- **Irreversible:** No recovery possible after deletion
- **Confirmation:** Requires explicit user action
- **Server-side:** Clears Gradio state components

**Implementation:**
```python
def run_pralaya(session_id, history):
    # Confirm deletion
    # Clear all history from session state
    # Return confirmation message
    return "✅ All chat history deleted", []
```

---

## 🔄 How It Works (For Everyone)

### Simple Flow:

```
1. YOU ask a question (in Hindi, Tamil, English, etc.)
   ↓
2. SARVAM SAARAS (if voice) converts speech to text
   ↓
3. SARVAM MAYURA translates to English
   ↓
4. FAISS SEARCH finds relevant laws (like Google for legal documents)
   ↓
5. LLAMA AI reads those laws and writes an answer
   ↓
6. SARVAM MAYURA translates answer back to your language
   ↓
7. SARVAM BULBUL (if enabled) speaks the answer
   ↓
8. YOU see the answer with references to actual laws!
```

### Example Journey:

**You (in Hindi):** *"मुझे गिरफ्तार करने के लिए वारंट की आवश्यकता है क्या?"*

**System Processing:**
1. Speech recognized: "मुझे गिरफ्तार करने के लिए वारंट की आवश्यकता है क्या?"
2. Translated to English: "Is a warrant required to arrest me?"
3. FAISS finds relevant sections: BNS Section 43, IPC Section 41, CrPC Section 155
4. Llama analyzes: "Under BNS Section 43, police can arrest without warrant for cognizable offences..."
5. Translated back to Hindi
6. Displayed with both Hindi and English versions

---

## 🏗️ Technical Architecture (For Developers)

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Gradio)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Trial Mode  │  │ Standard     │  │  Chitragupta     │  │
│  │   ⚖️        │  │ Chat 💬      │  │  (Export/Import) │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              MULTILINGUAL PROCESSING LAYER                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SARVAM AI APIs (Neural Seq2Seq Models)              │  │
│  │  • Mayura (NMT): Translation (13 langs ↔ English)    │  │
│  │  • Saaras (ASR): Speech-to-Text (multilingual)       │  │
│  │  • Bulbul (TTS): Text-to-Speech (neural voices)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE (Core)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. EMBEDDING: sentence-transformers/all-MiniLM-L6-v2│  │
│  │     • Input: User query (English)                    │  │
│  │     • Output: 384-dim dense vector                   │  │
│  │                                                        │  │
│  │  2. RETRIEVAL: FAISS (IndexFlatIP)                   │  │
│  │     • Corpus: 900+ legal chunks (BNS, IPC, IEA, etc.)│  │
│  │     • Similarity: Cosine (dot product on normalized) │  │
│  │     • Top-k: 5 most relevant passages                │  │
│  │     • Threshold: 0.3 minimum similarity              │  │
│  │                                                        │  │
│  │  3. AUGMENTATION: Context injection                  │  │
│  │     • Prompt template with retrieved passages        │  │
│  │     • Citation markers preserved                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                LLM GENERATION (Llama 4 Maverick)            │
│  • Model: Llama 4 Maverick (via Databricks AI Gateway)     │
│  • Context: RAG passages + system prompt                    │
│  • Temperature: 0.7 (balanced creativity)                   │
│  • Max tokens: 2048                                          │
│  • Output: Markdown-formatted response with citations       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             DATA PERSISTENCE & SECURITY                     │
│  • Unity Catalog: Vector index storage (Volumes)            │
│  • Session State: In-memory chat history (Gradio)           │
│  • Steganography: LSB-embedded encrypted exports (PNG)      │
│  • No database: Privacy-first, no server-side logs          │
└─────────────────────────────────────────────────────────────┘
```

### RAG Architecture Deep Dive

**1. Document Ingestion Pipeline:**
```python
Legal Documents (PDF/Text)
  ↓ [pdf_to_text]
Text Extraction
  ↓ [chunking: 500 chars, overlap=50]
Text Chunks (900+)
  ↓ [sentence-transformers/all-MiniLM-L6-v2]
Embeddings (384-dim vectors)
  ↓ [FAISS IndexFlatIP]
Vector Index (stored in UC Volume)
```

**2. Query Processing:**
```python
User Query (English)
  ↓ [same embedder]
Query Vector (384-dim)
  ↓ [FAISS similarity search]
Top-5 Relevant Chunks
  ↓ [prompt template]
Augmented Context
  ↓ [Llama 4 Maverick]
Generated Response
```

**3. FAISS Index Details:**
- **Index Type:** `IndexFlatIP` (Inner Product = Cosine Similarity on L2-normalized vectors)
- **Why not IVF/HNSW?** Dataset size (900 chunks) is small enough for exact search
- **Normalization:** All vectors L2-normalized before indexing
- **Search Complexity:** O(n) — acceptable for ~900 vectors

### Seq2Seq Models Used

**1. Sarvam Mayura (Translation):**
- **Architecture:** Transformer-based encoder-decoder
- **Training:** Multilingual parallel corpus (Indian languages ↔ English)
- **Tokenization:** Subword (BPE or SentencePiece)
- **Inference:** Beam search (beam_width=4)
- **Latency:** ~500-800ms per request

**2. Sarvam Saaras (ASR):**
- **Architecture:** Wav2Vec 2.0 / Conformer-based
- **Training:** Code-mixed Indian English + regional languages
- **Input:** 16kHz WAV audio
- **Output:** Transcribed text + confidence scores
- **Mode:** `translate` (output in English) or `transcribe` (output in source language)

**3. Sarvam Bulbul (TTS):**
- **Architecture:** Tacotron 2 / FastSpeech 2 + WaveGlow/HiFi-GAN vocoder
- **Training:** Language-specific voice models
- **Input:** Text + language code
- **Output:** Natural-sounding speech (MP3/WAV)

---

## 🛠️ Technology Stack

| Component | Technology | Why We Use It |
|-----------|-----------|---------------|
| **LLM** | Databricks Llama 4 Maverick | State-of-the-art reasoning, free tier access via AI Gateway |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Fast, lightweight, good for legal text (balanced precision/speed) |
| **Vector Search** | FAISS (IndexFlatIP) | Exact cosine similarity, no need for approximate methods at 900 docs |
| **Translation** | Sarvam Mayura | Best-in-class for Indian languages, handles legal terminology |
| **STT** | Sarvam Saaras | Multilingual ASR with code-mixing support |
| **TTS** | Sarvam Bulbul | Natural voices for Indian languages |
| **Web Framework** | Gradio 4.44 | Rapid prototyping, built-in audio/chat components |
| **Hosting** | Databricks Apps | Integrated with UC, AI Gateway, secrets management |
| **Storage** | Databricks Unity Catalog Volumes | Persistent storage for FAISS index |
| **Encryption** | AES-256-CBC + PBKDF2 | Industry-standard for data export security |
| **PDF Generation** | ReportLab | Professional PDF creation with full styling control |

### Why These Specific Choices?

**RAG over Fine-tuning:**
- **Flexibility:** Update legal knowledge without retraining
- **Explainability:** Can show exact sources (BNS sections, court judgments)
- **Cost:** No GPU-intensive training required
- **Compliance:** Easier to audit retrieved documents vs. model internals

**FAISS over Pinecone/Weaviate:**
- **Free:** No API costs, runs locally
- **Privacy:** No data leaves Databricks environment
- **Performance:** Sufficient for <10K documents
- **Integration:** Easy UC Volume storage

**Llama 4 Maverick over GPT-4:**
- **Access:** Available on Databricks Free Tier
- **Compliance:** Data stays within controlled environment
- **Performance:** Comparable quality for RAG tasks

---

## 🚀 Setup & Reproduction Guide

### Prerequisites

**Required:**
- Databricks Account (Free Tier works!)
- Sarvam AI API Key (sign up at sarvam.ai)
- Python 3.10+
- Git

**Optional:**
- HuggingFace account (for benchmark datasets)

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/nyaya-sahayak.git
cd nyaya-sahayak
```

#### 2. Databricks Authentication

```bash
# Install Databricks CLI
pip install databricks-cli

# Authenticate
databricks auth login --host https://your-workspace.cloud.databricks.com
export DATABRICKS_CONFIG_PROFILE=your-profile
```

#### 3. Create Secret Scope & Store Keys

```bash
# Create secret scope
databricks secrets create-scope nyaya-dhwani

# Store Sarvam API key
databricks secrets put-secret nyaya-dhwani sarvam_api_key
# Paste your key when prompted

# (Optional) Store HuggingFace token
databricks secrets put-secret nyaya-dhwani hf_token
```

#### 4. Prepare the Data

**Option A: Use Pre-built Index (Recommended)**
```bash
# Download pre-built FAISS index
databricks fs cp dbfs:/mnt/india-legal/nyaya_faiss.index ./models/
```

**Option B: Build from Scratch**
```bash
# Upload the notebooks to Databricks workspace
databricks workspace import-dir notebooks /Workspace/Users/your-email/nyaya-sahayak/

# Run data ingestion notebook
# This ingests BNS, IPC, IEA PDFs into legal_rag_corpus table

# Run FAISS index building notebook
# This creates nyaya_faiss.index and uploads to UC Volume
```

#### 5. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env
```

Required env vars:
```bash
SARVAM_API_KEY=your_sarvam_key
LLM_OPENAI_BASE_URL=https://your-workspace.cloud.databricks.com/serving-endpoints
LLM_MODEL_NAME=databricks-llama-4-maverick
NYAYA_INDEX_DIR=/Volumes/workspace/india_legal/legal_files/nyaya_index
```

#### 6. Install Dependencies

```bash
# Install in development mode
pip install -e ".[dev,rag,rag_embed,app]"
```

#### 7. Local Testing (Optional)

```bash
# Export env vars
export $(grep -v '^#' .env | xargs)

# Run the app locally
python app/main.py

# Access at http://localhost:7860
```

#### 8. Deploy to Databricks Apps

<<<<<<< Updated upstream
| Component | Technology |
|-----------|-----------|
| LLM | Databricks Llama 4 Maverick (AI Gateway) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector search | FAISS (IndexFlatIP, cosine similarity) |
| Translation | Sarvam Mayura |
| Speech-to-text | Sarvam Saaras |
| Text-to-speech | Sarvam Bulbul |
| App framework | Gradio 4.44 on Databricks Apps |
| Data platform | Databricks (Unity Catalog, Volumes, Apps) |


## Presentation Slides Link : https://drive.google.com/file/d/1gG_evWi67ySjcERPTlIjS774Q16t3br8/view?usp=sharing
=======
**Option A: Via Databricks UI**
1. Go to Workspace → Compute → Apps
2. Click "Create App"
3. Connect to this Git repository
4. Set resource profile: Small (2 GB RAM, 1 vCPU sufficient)
5. Click "Deploy"

**Option B: Via CLI**
```bash
databricks apps deploy   --name nyaya-sahayak   --source-dir .   --env-vars app.yaml
```

#### 9. Grant Permissions

The app service principal needs:
```bash
# AI Gateway endpoint access
databricks permissions grant endpoint databricks-llama-4-maverick   --service-principal your-app-sp   --permission CAN_QUERY

# UC Volume read access
databricks grants update volume main.india_legal.legal_files   --service-principal your-app-sp   --privilege READ

# Secret scope access
databricks secrets put-acl nyaya-dhwani   --service-principal your-app-sp   --permission READ
```

#### 10. Verify Deployment

```bash
# Check app logs
databricks apps logs nyaya-sahayak --follow

# Get app URL
databricks apps get nyaya-sahayak --output json | jq -r '.url'
```

### Troubleshooting

**Issue:** "401 Unauthorized" from AI Gateway
- **Fix:** Verify service principal has `CAN_QUERY` on the endpoint

**Issue:** "FAISS index not found"
- **Fix:** Check `NYAYA_INDEX_DIR` points to correct UC Volume path

**Issue:** "Sarvam API key invalid"
- **Fix:** Verify key in secret scope: `databricks secrets get nyaya-dhwani sarvam_api_key`

**Issue:** App crashes on startup
- **Fix:** Check logs for syntax errors or missing dependencies

---

## 📚 Feature Guide

### How to Use Trial of Justice

1. Open the app
2. Select your language from the dropdown
3. Click on the **"Trial of Justice"** tab
4. Type or speak your legal question
5. Click "Submit" or stop recording (audio auto-submits)
6. See the response in three sections:
   - ⚖️ **PROSECUTION:** One perspective
   - ⚖️ **DEFENSE:** Counter-perspective
   - 📜 **JUDICIAL SUMMARY:** Balanced overview
7. Read sources at the bottom (actual BNS/IPC sections)

**Best for:** Complex questions like "Is X legal?" or "What are my rights in Y situation?"

### How to Use Standard Chat

1. Open the app
2. Select your language
3. Click on the **"Standard Chat"** tab
4. Ask your question
5. Get a direct answer with legal references

**Best for:** Quick lookups like "What is Section 302 BNS?" or "What is the punishment for theft?"

### How to Use Voice Features

**Voice Input:**
1. Click the 🎤 microphone icon
2. Speak your question clearly
3. Click stop ⏹️
4. Watch the magic:
   - Purple animation: "Processing audio..."
   - Green animation: "Translated: [your question]"
   - Chat automatically updates with answer!

**Voice Output:**
1. Enable "🔊 Read Response Aloud" checkbox
2. Ask any question
3. Listen to the answer in your language
4. Adjust volume/pause as needed

### How to Export & Import Your Chats (Chitragupta)

**Export:**
1. Click on **"Chitragupta"** tab
2. Note your **Session ID** (save it securely!)
3. Click **"Export Chat History"**
4. Download the PNG image
5. Save both the image and Session ID

**Import:**
1. Click **"Chitragupta"** tab
2. Upload the PNG image
3. Enter your Session ID
4. Click **"Import History"**
5. Your chats are restored!
6. **Bonus:** A PDF is automatically generated — click to download!

**Security Note:** Without the Session ID, the image is useless. Keep your Session ID private!

### How to Delete Everything (Pralaya)

1. Click **"Chitragupta"** tab
2. Scroll to **"Pralaya"** section
3. Enter your Session ID (confirmation)
4. Click **"Delete All History"**
5. ⚠️ This is **irreversible** — all chats are permanently erased

---

## 👨‍💻 Development

### Project Structure

```
nyaya-sahayak/
├── app/
│   ├── main.py              # Gradio UI + orchestration
│   └── app.yaml             # Databricks Apps config
├── src/nyaya_dhwani/
│   ├── embedder.py          # Sentence-transformers wrapper
│   ├── retrieval.py         # FAISS search logic
│   ├── llm_client.py        # Llama AI Gateway client
│   ├── sarvam_client.py     # Sarvam API (Mayura, Saaras, Bulbul)
│   ├── steganography.py     # LSB embedding + AES encryption
│   └── trial_of_justice.py  # Adversarial prompt templates
├── notebooks/
│   ├── india_legal_policy_ingest.ipynb  # PDF → UC table
│   └── build_rag_index.ipynb            # Embeddings → FAISS
├── tests/
│   ├── test_retrieval.py
│   ├── test_sarvam.py
│   └── test_llm.py
├── docs/                    # Detailed documentation
├── requirements.txt         # Python dependencies
└── README.md               # You are here!
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev,rag]"

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_retrieval.py::test_faiss_search -v

# Coverage report
pytest --cov=src/nyaya_dhwani tests/
```

### Adding a New Language

1. Check if Sarvam supports it (check their API docs)
2. Add BCP-47 code to `SARVAM_LANGUAGES` in `app/main.py`:
   ```python
   ("mr", "मराठी (Marathi)"),
   ```
3. Update `bcp47_target()` function if custom mapping needed
4. Test translation: `python -m src.nyaya_dhwani.sarvam_client`

### Adding New Legal Documents

1. Place PDF in `data/raw/`
2. Run `notebooks/india_legal_policy_ingest.ipynb`
3. Rebuild FAISS index: `notebooks/build_rag_index.ipynb`
4. Update app to point to new index

### Customizing Trial of Justice Format

Edit `src/nyaya_dhwani/trial_of_justice.py`:
```python
TRIAL_SYSTEM_PROMPT = """
You are a legal AI presenting arguments in adversarial format.
[Your custom instructions here]
"""
```

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Databricks** for free tier access and AI Gateway
- **Sarvam AI** for multilingual APIs
- **Hugging Face** for embeddings model
- **Meta** for Llama foundation models
- **Government of India** for making BNS/IPC publicly available

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/nyaya-sahayak/issues)
- **Documentation:** [docs/](docs/)
- **Email:** your-email@example.com

---

## 🔮 Future Roadmap

- [ ] Support for more Indian languages (22 scheduled languages)
- [ ] Integration with live court judgment databases
- [ ] Lawyer consultation booking feature
- [ ] Mobile app (Android/iOS)
- [ ] WhatsApp bot integration
- [ ] Voice-first interface for feature phones
- [ ] Regional legal variations (state-specific laws)

---

**Made with ❤️ for India's legal accessibility**

*"Justice delayed is justice denied" — Let's make legal information instant and accessible to all.*
>>>>>>> Stashed changes
