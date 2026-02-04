# 🧠 Multi-Agent System for Emotional Intelligence Assessment

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Chainlit](https://img.shields.io/badge/UI-Chainlit-green.svg)](https://chainlit.io)

> Multi-Agent System for Emotional Intelligence Assessment with Explainable AI

A conversational AI agent that evaluates emotional intelligence based on **Goleman's 5-component model (1995)** using structured behavioral interviews (STAR method) and transparent reasoning chains.

## 🎯 Features

- **Multi-Agent Architecture**: Hierarchical orchestration with Reflection, Assessment, and Coordinator agents (LangGraph)
- **STAR-Based Interviews**: Behavioral questions following Situation-Task-Action-Result methodology
- **Explainable AI (XAI)**: Every reasoning step is transparent and visible to the user
- **Dunning-Kruger Detection**: Compares self-report with agent assessment to identify cognitive bias
- **Chain-of-Thought Analysis**: GPT-4 powered behavioral indicator extraction

## 🏗️ Architecture
```
User Input
    ↓
Coordinator Agent (Supervisor)
    ↓
    ├─→ Reflection Agent (Episodic Memory)
    │   - STAR Extraction
    │   - Behavioral Indicator Mapping
    │   - Confidence Scoring
    │
    ├─→ Assessment Agent (Validation)
    │   - Score Calculation
    │   - Inter-Agent Validation
    │   - Evidence Summary
    │
    └─→ Dunning-Kruger Analyzer
        - Gap Calculation
        - Bias Classification
        - Interpretation
```

## 📊 Goleman's EI Framework

The agent evaluates 5 core competencies:

1. **Self-Awareness** - Recognizing own emotions
2. **Self-Regulation** - Controlling impulses
3. **Motivation** - Intrinsic drive
4. **Empathy** - Understanding others' emotions
5. **Social Skills** - Managing relationships

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key

### Installation
```bash
# Clone repository
git clone https://github.com/AyzennaMosesArndt/ei-mentor-agent.git
cd ei-mentor-agent

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # MacOS: venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Add your OpenAI API key to .env
```

### Run
```bash
chainlit run app.py -w
```

Open browser at `http://localhost:8000`

## 🧪 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Orchestration** | LangGraph |
| **LLM** | OpenAI GPT-4o |
| **UI Framework** | Chainlit |
| **State Management** | LangGraph StateGraph |
| **Prompting** | Chain-of-Thought + Few-Shot |

## 📁 Project Structure
```
ei-mentor-agent/
├── agents/
│   ├── state.py              # Shared state definitions
│   ├── coordinator.py        # Hierarchical supervisor
│   ├── reflection_agent.py   # CoT-based analysis
│   ├── assessment_agent.py   # Score calculation
│   ├── dunning_kruger.py     # Bias detection
│   └── graph.py              # LangGraph workflow
├── data/
│   └── frameworks/
│       └── goleman_framework.json  # EI definitions
├── utils/
│   └── scoring.py            # Helper functions
├── app.py                    # Chainlit main
├── chainlit.md               # Welcome screen
└── requirements.txt
```

## 🔬 Research Foundation

Based on:

- **Goleman, D. (1995).** *Emotional Intelligence: Why It Can Matter More Than IQ*
- **Kruger, J., & Dunning, D. (1999).** *Unskilled and unaware of it: How difficulties in recognizing one's own incompetence lead to inflated self-assessments*
- **STAR Method** - Behavioral interviewing technique

## 🌐 Live Demo & Prototyp

- **🚀 Funktionale Demo**: [Hugging Face Spaces](https://huggingface.co/spaces/magic-moses/ei-agentic-assessment)
- **🎨 UI-Prototyp (v2.0)**: [Lovable Mockup](https://agentic-ei-assessment.lovable.app)
- **📊 UX-Evaluation**: [Google Forms](https://docs.google.com/forms/d/e/1FAIpQLSd-K3jSb_vl7bLJP7jsi-l7CvkSJXRedc7kqwxuakkueZyfNg/viewform?usp=dialog)

## 🎓 Academic Context

- Agentic AI systems
- Explainable AI (XAI)
- Human-AI interaction
- Soft skill assessment

## 📈 Evaluation Results

**System Usability:**
- ✅ **SUS Score: 96.4/100** 
- ✅ **100% Would Recommend**
- ✅ Ease of Use: 5.0/5
- ✅ PDF Report: 5.0/5 

**Dunning-Kruger Awareness:**
- ✅ **71% reflected on their self-perception**
- ✅ 71% were surprised by the gap

**XAI Comprehensibility:**
- ⚠️ Understanding score calculation: 2.43/5
- → **Solution**: [UI Prototype v2.0](https://agentic-ei-assessment.lovable.app) with Score Breakdown + Inline Highlighting

## 🎨 Prototype v2.0 (Lovable)

The [interactive prototype](https://agentic-ei-assessment.lovable.app) addresses the XAI transparency issues identified in the evaluation:

1. **Score Breakdown Card**: Shows calculation from 3 individual questions
2. **Inline Highlighting**: Marks text passages → indicators
3. **Transparent Progress Bar**: Real-time visualization of all agent steps

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@AyzennaMosesArndt](https://github.com/AyzennaMosesArndt)
- LinkedIn: [Ayzenna Moses Arndt](https://linkedin.com/in/AyzennaMosesArndt)
- Live Demo: [Hugging Face Spaces](https://huggingface.co/spaces/magic-moses/ei-agentic-assessment)

## 🙏 Acknowledgments

- Daniel Goleman for the EI framework
- Anthropic/OpenAI for LLM capabilities
- LangChain team for LangGraph

---

⭐ If you found this project helpful, please consider giving it a star!
