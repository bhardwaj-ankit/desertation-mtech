# Getting Started Guide

Welcome! Your dissertation project is now fully organized and ready for development.

## 📍 You Are Here

```
/Users/ankitbhardwaj/Documents/dissertaion-abstract/
├── GETTING_STARTED.md     ← You're reading this
├── README.md              ← Project overview
├── TOOLS.md               ← Technology stack & installation
├── research/              ← All your research documents & slides
└── src/                   ← Where you'll write code
```

## 🚀 Quick Start (5 minutes)

### 1. Read These First (in order)
- [ ] **TOOLS.md** - Understand the tech stack (15 min read)
- [ ] **README.md** - Understand the project architecture (10 min read)
- [ ] **PROJECT_STRUCTURE.txt** - See what was organized (5 min read)

### 2. Setup Environment (if starting fresh)
```bash
cd /Users/ankitbhardwaj/Documents/dissertaion-abstract

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure Your System
```bash
# Copy configuration template
cp .env.example .env

# Edit .env with your settings
# nano .env  (or open in your editor)
```

## 📚 What's Where

| Location | Contains | Purpose |
|----------|----------|---------|
| **research/** | PDF, docx, MD, PPTX | All your abstract, slides, references |
| **TOOLS.md** | Tech stack, setup | Complete tooling guide |
| **README.md** | Overview, architecture | Project context |
| **src/** | (empty, ready) | Where you write Python code |
| **data/** | (empty, ready) | Datasets go here |
| **models/** | (empty) | Trained model checkpoints |
| **tests/** | (empty) | Unit tests go here |

## 🎯 Your Viva (Outline Phase)

**Status:** ✅ Abstract submitted (May 10, 2026)  
**Presentation:** 15 slides ready in `research/Outline_Viva_Slides.pptx`  
**Focus Areas to Explain:**
- Problem context & industry motivation
- Multimodal + RAG + agentic architecture
- Literature review findings
- Design decisions (why RAG + fine-tuning together)
- Training approach on historical defects
- Safety layer & compliance

**See TOOLS.md for technical viva Q&A answers** ← Use for exam prep!

## 💻 Before Next Phase (Design & Development)

### Must Do:
- ✅ Read TOOLS.md (complete)
- ✅ Read README.md (complete)
- ✅ Understand architecture in README
- ✅ Review viva slides in research/
- ✅ Understand why each tool is chosen (from TOOLS.md)

### Should Do:
- Download sample datasets (FAA SDR, NASA ASRS, C-MAPSS)
- Place in `data/raw/`
- Skim transformation papers from research/
- Start implementing `src/embeddings.py`

### Nice To Have:
- Read through all research documents for deep background
- Check TOOLS.md alternatives section for your preferences

## 🔧 Implementation Roadmap

Once Design & Development phase starts (May 17):

1. **Week 1:** Core infrastructure
   - [ ] src/embeddings.py (load pre-trained models)
   - [ ] src/vector_store.py (Chroma integration)
   - [ ] src/rag_pipeline.py (retrieval + context building)

2. **Week 2-3:** Agents
   - [ ] src/agents/orchestrator.py (LangGraph)
   - [ ] src/agents/triage_agent.py
   - [ ] src/agents/recurrence_agent.py
   - [ ] src/agents/reasoning_agent.py

3. **Week 3-4:** Models
   - [ ] src/models/triage_classifier.py (PyTorch)
   - [ ] src/models/recurrence_predictor.py (LSTM)
   - [ ] Training pipelines

4. **Week 5:** Fine-tuning
   - [ ] src/models/fine_tuning.py (LoRA)
   - [ ] Training on maintenance data

5. **Week 6:** UI & API
   - [ ] src/api.py (FastAPI)
   - [ ] src/ui.py (Streamlit)

6. **Week 7:** Testing & Evaluation
   - [ ] tests/
   - [ ] src/utils/evaluation.py
   - [ ] Metrics collection

7. **Week 8:** Polish & Submission
   - [ ] Documentation
   - [ ] Final testing
   - [ ] Prepare for viva

## 🎓 For Viva Preparation

All technical viva Q&A answers are in **TOOLS.md**:
- "Why both RAG and fine-tuning?" → [See TOOLS.md](TOOLS.md#why-both-rag-and-fine-tuning)
- "How will you implement evidence-grounding?" → [See TOOLS.md](TOOLS.md#simple-viva-answer-how-will-you-implement-evidence-grounding)
- "What's the multimodal architecture?" → [See TOOLS.md](TOOLS.md#technical-architecture-agentic-multimodal-rag-system)
- "How will you train on defects?" → [See TOOLS.md](TOOLS.md#complete-training-pipeline-for-defect-models)

**Use TOOLS.md as your viva study guide!**

## 📞 Useful Commands

```bash
# Activate environment
source venv/bin/activate

# Run Streamlit UI
streamlit run src/ui.py

# Run FastAPI
uvicorn src.api:app --reload

# Run tests
pytest tests/ -v --cov=src

# Format code
black src/

# Check style
flake8 src/

# View requirements
cat requirements.txt
```

## ❓ Common Questions

**Q: Where are my slides?**  
A: `research/Outline_Viva_Slides.pptx` (15 slides, fully prepared)

**Q: Where's my abstract?**  
A: `research/Abstract report submitted.pdf`

**Q: What's in TOOLS.md?**  
A: Complete technology stack, installation guide, troubleshooting, and viva Q&A answers

**Q: Should I start coding now?**  
A: Read TOOLS.md and README.md first. Coding starts May 17 in Design & Development phase.

**Q: Can I change the tech stack?**  
A: Yes! TOOLS.md lists alternatives for every component. Choose what you prefer.

**Q: How do I prepare for viva?**  
A: Study TOOLS.md technical details + review README.md architecture + practice slides.

## 🎯 Next Action

**Right now:**
1. Open `TOOLS.md` in your editor
2. Read the "Architecture Overview" section
3. Read "Complete Technology Stack" section
4. Come back when ready to code

**Then:**
1. Read `README.md`
2. Review `research/Outline_Viva_Slides.pptx`
3. Start implementing `src/embeddings.py`

---

**Happy coding! Your project structure is ready. Now build the system! 🚀**
