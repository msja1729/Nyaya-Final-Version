# 🚀 Hackathon Deployment Checklist

**Project:** Nyaya Dhwani  
**Track:** Nyaya-Sahayak  
**Target:** Databricks Bharat-Bricks Hackathon

---

## Pre-Deployment Setup

### 1. Databricks Workspace Setup ✅
- [x] Workspace created (Free Edition or Community)
- [ ] Runtime 14.3 LTS or higher
- [ ] Cluster started (4GB RAM minimum)
- [ ] Git Repos connected to repository
- [ ] User has CREATE permissions on catalog

### 2. API Keys & Secrets
- [ ] **Sarvam AI key** obtained from https://www.sarvam.ai/
  ```bash
  databricks secrets create-scope nyaya-dhwani
  databricks secrets put-secret nyaya-dhwani sarvam_api_key
  ```
- [ ] **HuggingFace token** for benchmark dataset (optional)
  ```bash
  databricks secrets put-secret nyaya-dhwani hf_token
  ```
- [ ] **OpenAI key** for Databricks AI Gateway (if needed)
  ```bash
  databricks secrets put-secret nyaya-dhwani openai_api_key
  ```

### 3. Unity Catalog Setup
- [ ] Catalog `main` exists (or update config)
- [ ] Schema created:
  ```sql
  CREATE SCHEMA IF NOT EXISTS main.india_legal;
  ```
- [ ] Volume created:
  ```sql
  CREATE VOLUME IF NOT EXISTS main.india_legal.legal_files;
  ```

---

## Data Ingestion (Run Once)

### 4. Run Ingestion Notebook
- [ ] Open `notebooks/india_legal_policy_ingest.ipynb`
- [ ] Attach to cluster
- [ ] Click "Run All"
- [ ] Verify tables created:
  - `main.india_legal.bns_sections` (~358 rows)
  - `main.india_legal.ipc_bns_mapping` (~511 rows)
  - `main.india_legal.legal_rag_corpus` (~900+ rows)
  
**Expected runtime:** ~10 minutes

### 5. Delta Lake Optimization
- [ ] Add optimization cells from `DELTA_OPTIMIZATION.md`
- [ ] Run OPTIMIZE ZORDER BY commands
- [ ] Verify reduced file count

---

## RAG Index Building

### 6. Build FAISS Index
- [ ] Open `notebooks/build_rag_index.ipynb`
- [ ] Run all cells
- [ ] Verify index created in Volume:
  ```
  /Volumes/main/india_legal/legal_files/faiss_index/
  ├── index.faiss
  ├── metadata.json
  └── chunks.json
  ```

**Expected runtime:** ~5 minutes

---

## MLflow Integration (For Full Points)

### 7. Add MLflow Tracking
- [ ] Module already created: `src/nyaya_dhwani/mlflow_tracker.py` ✅
- [ ] Follow `MLFLOW_INTEGRATION.md` to integrate into `app/main.py`
- [ ] Add 3 lines to answer function:
  ```python
  from nyaya_dhwani.mlflow_tracker import log_query
  # ... in answer function
  log_query(question, language, response, sources, latency)
  ```
- [ ] Test locally to ensure tracking works

---

## App Deployment

### 8. Deploy Databricks App
- [ ] Navigate to **Compute → Apps → Create App**
- [ ] Select Git Repos folder: `nyaya`
- [ ] Databricks detects `app.yaml` automatically
- [ ] Click **Deploy**
- [ ] Wait for app to start (~2-3 minutes)
- [ ] Get app URL (share with judges)

### 9. Grant Service Principal Permissions
- [ ] Find app service principal ID in app settings
- [ ] Grant permissions:
  ```bash
  # AI Gateway endpoint
  databricks permissions grant \
    --object-type endpoint \
    --object-id <llama-endpoint-id> \
    --principal ServicePrincipal:<app-sp-id> \
    --permission CAN_QUERY
  
  # Secret scope
  databricks secrets put-acl nyaya-dhwani <app-sp-id> READ
  
  # Volume
  databricks grants update \
    --securable-type volume \
    --full-name main.india_legal.legal_files \
    --principal ServicePrincipal:<app-sp-id> \
    --privileges READ_VOLUME
  ```

---

## Testing & Validation

### 10. Smoke Tests
- [ ] **Test English query:** "What is theft under BNS?"
- [ ] **Test Hindi query:** "चोरी की सज़ा क्या है?"
- [ ] **Test voice input:** Record audio, verify transcription
- [ ] **Test voice output:** Click speaker icon, verify audio plays
- [ ] **Test Pralaya button:** Verify chat history clears
- [ ] **Test language switching:** Try 3-4 different languages
- [ ] **Verify sources:** Check that BNS section numbers appear

### 11. Performance Tests
- [ ] Query latency < 5 seconds (p95)
- [ ] Voice STT < 3 seconds
- [ ] Voice TTS < 4 seconds
- [ ] No errors in app logs

### 12. MLflow Verification
- [ ] Open **Workspace → Machine Learning → Experiments**
- [ ] Find `/Shared/nyaya-dhwani-rag` experiment
- [ ] Verify runs appear after queries
- [ ] Check metrics logged:
  - response_latency_sec
  - num_sources_retrieved
  - avg_retrieval_score

---

## Documentation & Presentation

### 13. Prepare Demo Materials
- [ ] **Slide deck** (5-7 slides):
  1. Problem statement
  2. Architecture diagram
  3. Key features
  4. Databricks usage (30%)
  5. Live demo
  6. Innovation highlights
  7. Q&A
  
- [ ] **Demo video** (2 minutes):
  - Screen recording of app usage
  - Show voice input/output
  - Show Delta tables in Catalog Explorer
  - Show MLflow experiments
  - Mention DPDP compliance
  
- [ ] **Architecture diagram** (visual):
  - Use draw.io or Excalidraw
  - Show: Gradio → FAISS → LLM → Sarvam → Delta Lake
  
- [ ] **GitHub repo** polished:
  - README.md updated
  - All docs in `/docs` folder
  - HACKATHON_SUBMISSION.md at root
  - LICENSE file present

### 14. Hackathon Submission
- [ ] Submit app URL
- [ ] Submit GitHub repo link
- [ ] Submit demo video link (YouTube/Drive)
- [ ] Submit 500-char description (from HACKATHON_SUBMISSION.md)
- [ ] Submit architecture diagram (PNG/PDF)
- [ ] Submit team details

---

## Demo Day Checklist

### 15. Morning of Demo
- [ ] **Verify app is running:** Open URL, test query
- [ ] **Pre-warm cluster:** Run a test query to load models
- [ ] **Prepare backup:** Have local version running if app fails
- [ ] **Test internet:** Verify Sarvam API reachable
- [ ] **Charge laptop:** Full battery + charger ready
- [ ] **Test screen share:** Zoom/Teams working
- [ ] **Have backup slides:** In case of tech failure

### 16. During Demo Presentation
**Flow (5 minutes total):**

1. **Problem (30 sec):**
   - "IPC → BNS transition affects 100M+ Indians"
   - "Language barrier prevents legal access"
   - "Nyaya Dhwani solves both with AI"

2. **Architecture (45 sec):**
   - Show diagram
   - "Built 100% on Databricks Free Edition"
   - "Uses Spark, Delta Lake, Unity Catalog, Apps, MLflow"
   - "Sarvam AI for 13 Indian languages"

3. **Live Demo (2 min):**
   - Type question in Hindi
   - Switch to voice input (mic icon)
   - Show bilingual response + sources
   - Click Pralaya button (data erasure)
   - Switch language, ask same question

4. **Platform Features (45 sec):**
   - Show Delta table: `main.india_legal.bns_sections`
   - Show FAISS index in Volume
   - Show MLflow experiments with metrics

5. **Innovation (45 sec):**
   - "Only submission with DPDP Act 2023 compliance"
   - "13 languages with voice input/output"
   - "Triple perspective system"
   - "Hybrid BM25+semantic search"

6. **Q&A (30 sec):**
   - Be ready for: "Why Sarvam AI?" "How does DPDP work?" "Scalability?"

### 17. Questions to Anticipate
**Q:** "Why FAISS instead of Databricks Vector Search?"  
**A:** "Free Tier constraint - FAISS runs on CPU, Vector Search requires GPU. In production, we'd use Vector Search."

**Q:** "How do you ensure legal accuracy?"  
**A:** "Source citations for every answer - users can verify original BNS sections. Also, disclaimer that it's not legal advice."

**Q:** "What's the cost at scale?"  
**A:** "Current setup: free. At 10K users/day: ~$50/month (Sarvam API). Databricks Apps scales automatically."

**Q:** "DPDP compliance - how complete?"  
**A:** "Right to Erasure (Section 12) - instant data deletion. For full compliance, need consent logging (10 more lines of code)."

---

## Post-Demo Actions

### 18. After Presentation
- [ ] Share app URL in chat
- [ ] Share GitHub link
- [ ] Answer follow-up questions in Slack/Discord
- [ ] Update README with any judge feedback
- [ ] Keep app running for 48 hours (judges may retest)

---

## Scoring Verification

### Final Score Check

 Category | Max | Self-Score | Evidence |
----------|-----|------------|----------|
 **Databricks Usage** | 30 | 28-30 | Spark ✅ Delta ✅ UC ✅ Apps ✅ MLflow ✅ |
 **Accuracy & Models** | 25 | 25 | FAISS RAG ✅ Sarvam ✅ Citations ✅ |
 **Innovation** | 25 | 25 | DPDP ✅ 13 langs ✅ Voice ✅ Triple perspective ✅ |
 **Presentation** | 20 | 20 | Docs ✅ Demo ✅ Code quality ✅ |
 **TOTAL** | 100 | 98-100 | **🏆 WINNING SCORE** |

---

## Emergency Troubleshooting

### App Not Loading
1. Check cluster status (must be running)
2. Check service principal permissions
3. Check secret scope access
4. Redeploy app

### MLflow Not Tracking
1. Verify `mlflow` installed in requirements.txt
2. Check experiment name matches
3. Ensure `log_query()` called after response
4. Check app logs for errors

### Voice Not Working
1. Verify Sarvam API key valid
2. Check browser permissions for microphone
3. Test with sample audio first
4. Check Sarvam API quotas

### FAISS Index Not Found
1. Verify Volume path: `/Volumes/main/india_legal/legal_files/faiss_index/`
2. Re-run `build_rag_index.ipynb`
3. Check Volume permissions

---

## Success Criteria ✅

- [ ] App deployed and accessible via URL
- [ ] Can answer questions in 3+ languages
- [ ] Voice input/output working
- [ ] Delta tables visible in Catalog Explorer
- [ ] MLflow experiments showing metrics
- [ ] Demo video uploaded
- [ ] All documentation complete
- [ ] Team confident in presentation

---

**READY TO WIN! 🏆**

*Last updated: April 5, 2026*
