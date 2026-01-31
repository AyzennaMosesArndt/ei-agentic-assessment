"""
EI-Mentor Agent - Chainlit UI
Multi-Agent System für Emotional Intelligence Assessment mit XAI.
"""
import chainlit as cl
import json
from pathlib import Path
from agents.graph import app as agent_graph
from agents.state import AgentState
from utils.scoring import calculate_indicator_coverage, get_strength_and_weaknesses
from utils.session_manager import SessionManager
import uuid
from datetime import datetime

# Load Goleman Framework
FRAMEWORK_PATH = Path("data/frameworks/goleman_framework.json")
with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
    GOLEMAN_FRAMEWORK = json.load(f)

session_manager = SessionManager()


@cl.on_chat_start
async def start():
    """Chat Start - Welcome Message"""
    session_id = str(uuid.uuid4())[:8]
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("onboarding_step", "welcome")
    
    await cl.Message(
        content="""# 🧠 Emotional Intelligence Mentor Agent

Willkommen zum **Emotional Intelligence Assessment** basierend auf Daniel Goleman's Forschung (1995)!

**Warum ist das wichtig?** - Studien zeigen: Emotionale Intelligenz korreliert signifikant mit Führungserfolg, Job-Zufriedenheit und  Unternehmensidentifikation (Miao et al., 2017, 2018). Während KI technische und standardisierbare Aufgaben übernimmt, steigt die Nachfrage nach emotional-sozialen Kompetenzen (World Economic Forum Future of Jobs Report, 2023). Goleman's Forschung bleibt top-aktuell. Vielleicht sogar aktueller denn je!

<details>
<summary>📚 Quellen</summary>

<small>
Miao, C., Humphrey, R. H., & Qian, S. (2017). A meta-analysis of emotional intelligence and work attitudes. *Journal of Occupational and Organizational Psychology, 90*(2), 177–202. https://doi.org/10.1111/joop.12167

Miao, C., Humphrey, R. H., & Qian, S. (2018). Emotional intelligence and authentic leadership: a meta-analysis. *Leadership and Organization Development Journal, 39*(5), 679–690. https://doi.org/10.1108/LODJ-02-2018-0066

World Economic Forum. (2023). Future of Jobs Report 2023. https://www.weforum.org/publications/the-future-of-jobs-report-2023/
</small>

</details>

---

## 📋 Ablauf (ca. 10-15 Minuten)

**1. Skill-Auswahl** - Du wählst eine der 5 Emotional Intelligence Dimensionen  
**2. Self-Report** - Du schätzt dich selbst ein (Skala 1-5)  
**3. STAR-Interview** - Du beantwortest je Dimension 3 verhaltensbezogene Fragen zu konkreten Beispielen aus deinem Leben
**4. Agentic Analyse** - Unser Agent System analysiert deine Antworten und zeigt Unterschiede zu deiner Selbstwahrnehmung (Dunning-Kruger-Effekt)
**5. Transparente Analyse** - Du siehst jeden Reasoning-Step des Agents (XAI)  

🎁 **Bonus:** Teste **3+ Dimensionen** → Erhalte **kostenlosen PDF-Report** mit Radar Chart!

---

**Bereit?** Schreib **"Ja"** oder **"Los"** und ich präsentiere dir die 5 Dimensionen!"""
    ).send()


async def show_dimensions(session_id: str):
    """Zeigt die 5 EI-Dimensionen mit Progress"""
    progress = session_manager.get_progress(session_id)
    
    msg = """## 🎯 Die 5 EI-Dimensionen nach Goleman

**1️⃣ Selbstwahrnehmung** (Self-Awareness)  
Die Fähigkeit, eigene Emotionen zu erkennen und zu verstehen. Du weißt, wann du wütend, traurig oder gestresst bist und verstehst *warum*.

**2️⃣ Selbststeuerung** (Self-Regulation)  
Die Fähigkeit, störende Emotionen und Impulse zu kontrollieren. Du bleibst ruhig unter Druck und reagierst nicht impulsiv.

**3️⃣ Motivation** (Motivation)  
Intrinsische Leistungsorientierung und Optimismus. Du setzt dir hohe Ziele und bleibst dran, auch wenn's schwierig wird.

**4️⃣ Empathie** (Empathy)  
Die Fähigkeit, Emotionen anderer zu verstehen und darauf einzugehen. Du merkst, wenn jemand Hilfe braucht, auch ohne dass es gesagt wird.

**5️⃣ Soziale Kompetenz** (Social Skills)  
Die Fähigkeit, Beziehungen zu managen und andere zu beeinflussen. Du kommunizierst klar, löst Konflikte konstruktiv und arbeitest gut im Team.

---

"""
    
    # Progress Tracking
    if progress["count"] > 0:
        msg += f"✅ **Bereits getestet:** {progress['count']}/5\n"
        tested_names = [GOLEMAN_FRAMEWORK["skills"][sid]["name"] for sid in progress["tested"]]
        msg += f"   ({', '.join(tested_names)})\n\n"
        
        if not progress["can_download_pdf"]:
            remaining = 3 - progress["count"]
            msg += f"📊 **Noch {remaining} Dimension{'en' if remaining > 1 else ''} bis zum PDF-Report!**\n\n"
        else:
            if progress["count"] < 5:
                msg += f"🎉 **PDF-Report verfügbar!** Noch {5 - progress['count']} für vollständige Analyse.\n\n"
            else:
                msg += "🏆 **VOLLSTÄNDIG!** Alle 5 Dimensionen getestet!\n\n"
    
    msg += "**Für welche Dimension interessierst du dich am meisten?**\n\nAntworte mit **1-5** oder dem **Namen** (z.B. 'Empathie'):"
    
    await cl.Message(content=msg).send()
    cl.user_session.set("onboarding_step", "dimension_selection")


async def show_quality_tips():
    """Zeigt Tipps für gute Antworten"""
    await cl.Message(
        content="""## 💡 Wichtig für beste Ergebnisse

**Je ausführlicher deine Antworten, desto genauer die Analyse!**

Beschreibe:
- ✅ **Konkrete Situationen** (nicht "ich bin immer empathisch")
- ✅ **Was du *getan* hast** (Aktionen, nicht nur Gedanken)
- ✅ **Das Ergebnis** (was ist passiert?)

---

**Schlechtes Beispiel:**  
> "Ich bin gut im Umgang mit Stress."

**Gutes Beispiel:**  
> "Letzte Woche hatte ich 3 Deadlines gleichzeitig. Ich hab mir eine Prio-Liste gemacht, tief durchgeatmet und nacheinander abgearbeitet. Alle Deadlines geschafft ohne auszuflippen."

---

**So, jetzt aber wirklich... los geht's!** 🚀

Schreib **"Bereit"** oder **"Start"** um mit dem Self-Report zu beginnen!"""
    ).send()
    
    cl.user_session.set("onboarding_step", "quality_tips_shown")


async def ask_self_report(skill_name: str):
    """Fragt nach Self-Report Score"""
    res = await cl.AskUserMessage(
        content=f"""## 📊 Self-Report: {skill_name}

Wie schätzt du deine **{skill_name}** selbst ein?

**Gib eine Zahl zwischen 1 und 5 ein:**

- **1** = Sehr niedrig (habe damit große Schwierigkeiten)
- **2** = Niedrig (ausbaufähig)
- **3** = Mittel (manchmal gut, manchmal nicht)
- **4** = Gut (meistens kompetent)
- **5** = Sehr gut (ist eine meiner Stärken)

Deine Einschätzung:""",
        timeout=300
    ).send()
    
    try:
        score = float(res['output'].strip())
        if not 1 <= score <= 5:
            raise ValueError
    except:
        await cl.Message(
            content="❌ Ungültige Eingabe. Bitte gib eine Zahl zwischen 1 und 5 ein."
        ).send()
        return await ask_self_report(skill_name)
    
    # Update State
    state = cl.user_session.get("state")
    state["self_report_score"] = score
    cl.user_session.set("state", state)
    
    async with cl.Step(name="✅ Self-Report gespeichert") as step:
        step.output = f"Deine Selbsteinschätzung: **{score}/5**"
    
    await cl.Message(
        content=f"""Danke! Du schätzt dich bei **{score}/5** ein.

---

## 🎤 STAR-Interview (3 Fragen)

Jetzt stelle ich dir **3 Fragen** nach der **STAR-Methode**:

- **S**ituation - Was war der Kontext?
- **T**ask - Welche Herausforderung hattest du?
- **A**ction - Was hast du konkret gemacht?
- **R**esult - Was war das Ergebnis?

**Nimm dir Zeit** für deine Antworten (3-5 Sätze pro Frage sind ideal).

Bereit? Schreib **"Los"** um zu starten!"""
    ).send()
    
    cl.user_session.set("awaiting_interview_start", True)


@cl.on_message
async def main(message: cl.Message):
    """Message Handler - Onboarding + Interview + Analysis"""
    user_input = message.content.strip().lower()
    onboarding_step = cl.user_session.get("onboarding_step")
    state = cl.user_session.get("state")
    session_id = cl.user_session.get("session_id")
    
    # ONBOARDING FLOW
    if onboarding_step == "welcome":
        if user_input in ["ja", "los", "yes", "weiter", "ok", "bereit", "start"]:
            await show_dimensions(session_id)
        else:
            await cl.Message(content="Schreib **'Ja'** oder **'Los'** um fortzufahren!").send()
        return
    
    if onboarding_step == "dimension_selection":
        # SKILL SELECTION
        skill_map = {
            "1": "self_awareness",
            "2": "self_regulation", 
            "3": "motivation",
            "4": "empathy",
            "5": "social_skills",
            "selbstwahrnehmung": "self_awareness",
            "self awareness": "self_awareness",
            "selbststeuerung": "self_regulation",
            "self regulation": "self_regulation",
            "motivation": "motivation",
            "empathie": "empathy",
            "empathy": "empathy",
            "soziale kompetenz": "social_skills",
            "social skills": "social_skills"
        }
        
        skill_id = skill_map.get(user_input)
        
        # Check if already tested
        progress = session_manager.get_progress(session_id)
        if skill_id and skill_id in progress["tested"]:
            skill_name = GOLEMAN_FRAMEWORK["skills"][skill_id]["name"]
            await cl.Message(
                content=f"❌ **{skill_name}** hast du bereits getestet! Wähle eine andere Dimension."
            ).send()
            return
        
        if not skill_id:
            await cl.Message(
                content="❌ Ungültige Auswahl. Bitte wähle **1-5** oder schreib den Namen (z.B. 'Empathie')."
            ).send()
            return
        
        skill_data = GOLEMAN_FRAMEWORK["skills"][skill_id]
        
        # Initialize State
        state = AgentState(
            messages=[],
            selected_skill=skill_id,
            self_report_score=None,
            skill_definition=skill_data["definition"],
            behavioral_indicators=skill_data["behavioral_indicators"],
            star_questions=skill_data["star_questions"],
            current_question_index=0,
            user_responses=[],
            response_analyses=[],
            agent_score=None,
            dunning_kruger_gap=None,
            classification=None,
            agent_decisions=[],
            next_step="self_report"
        )
        
        cl.user_session.set("state", state)
        
        # Show Framework
        async with cl.Step(name="📚 Framework Loading", type="tool") as step:
            framework_msg = f"""## {skill_data['name']} ({skill_data['name_en']})

**Definition:**  
{skill_data['definition']}

**Behavioral Indicators (worauf wir achten):**
"""
            for i, indicator in enumerate(skill_data['behavioral_indicators'], 1):
                framework_msg += f"\n{i}. {indicator}"
            
            step.output = framework_msg
        
        await cl.Message(
            content=f"✅ Perfekt! Du hast **{skill_data['name']}** gewählt."
        ).send()
        
        # Show Quality Tips
        await show_quality_tips()
        return
    
    if onboarding_step == "quality_tips_shown":
        if user_input in ["bereit", "start", "los", "ja", "ok", "weiter"]:
            cl.user_session.set("onboarding_step", "active_assessment")
            await ask_self_report(GOLEMAN_FRAMEWORK["skills"][state["selected_skill"]]["name"])
        else:
            await cl.Message(content="Schreib **'Bereit'** oder **'Start'** um fortzufahren!").send()
        return
    
    # ASSESSMENT COMPLETED - Next Action
    if cl.user_session.get("awaiting_next_action"):
        progress = session_manager.get_progress(session_id)
        
        if user_input in ["neu", "andere dimension", "andere", "nochmal", "weiter"]:
            # Restart flow
            cl.user_session.set("onboarding_step", "dimension_selection")
            cl.user_session.set("awaiting_next_action", False)
            await show_dimensions(session_id)
        elif user_input in ["fertig", "ende", "stop", "done"]:
            await cl.Message(
                content="""## 👋 Danke fürs Mitmachen!

Du kannst die Seite neu laden, um ein komplett neues Assessment zu starten.

Viel Erfolg bei der Weiterentwicklung deiner emotionalen Intelligenz! 🚀"""
            ).send()
        else:
            await cl.Message(
                content="Schreib **'Neu'** für eine andere Dimension oder **'Fertig'** zum Beenden."
            ).send()
        return
    
    # ACTIVE ASSESSMENT FLOW
    if not state:
        await cl.Message(content="⚠️ Bitte lade die Seite neu, um zu starten.").send()
        return
    
    # Check if waiting for interview start
    if cl.user_session.get("awaiting_interview_start"):
        if user_input in ["los", "start", "ja", "ok", "bereit", "go", "weiter"]:
            cl.user_session.set("awaiting_interview_start", False)
            await conduct_interview(state)
        return
    
    # Check if in interview mode
    if cl.user_session.get("in_interview"):
        await handle_interview_response(message.content, state)
        return
    
    # Default response
    await cl.Message(
        content="Bitte folge den Anweisungen oben. Falls etwas nicht funktioniert, lade die Seite neu."
    ).send()


async def conduct_interview(state: AgentState):
    """Startet das STAR-Interview"""
    cl.user_session.set("in_interview", True)
    
    question_idx = state["current_question_index"]
    question = state["star_questions"][question_idx]
    
    # STAR Examples hinzufügen
    examples = {
        0: """**Beispiel einer guten Antwort:**
> "Im letzten Projekt (Situation) musste ich ein konfliktgeladenes Meeting moderieren (Task). Ich hab zuerst alle Perspektiven gehört ohne zu unterbrechen, dann gemeinsam Prioritäten definiert (Action). Am Ende hatten wir einen Konsens und das Projekt lief weiter (Result)."
""",
        1: """**Beispiel einer guten Antwort:**
> "Bei einem spontanen Kunden-Complaint (Situation) war mein erster Impuls, defensiv zu reagieren (Task: ruhig bleiben). Ich hab tief durchgeatmet, aktiv zugehört und erst dann geantwortet (Action). Der Kunde hat sich beruhigt und wir konnten eine Lösung finden (Result)."
""",
        2: """**Beispiel einer guten Antwort:**
> "Nach einem Rückschlag im letzten Quartal (Situation) musste ich das Team neu motivieren (Task). Ich hab eine Retrospektive gemacht, Erfolge gefeiert und neue Ziele gesetzt (Action). Das Team war wieder motiviert und wir haben die Ziele im nächsten Quartal übertroffen (Result)."
"""
    }
    
    await cl.Message(
        content=f"""## 📝 Frage {question_idx + 1}/3

{question}

---

{examples.get(question_idx, "")}

**Deine Antwort (3-5 Sätze):**"""
    ).send()


async def handle_interview_response(response: str, state: AgentState):
    """Verarbeitet User-Antwort während Interview"""
    # Speichere Antwort
    state["user_responses"].append(response)
    
    question_idx = state["current_question_index"]
    
    # Quick Analysis Preview
    async with cl.Step(name=f"✅ Antwort {question_idx + 1}/3 gespeichert") as step:
        step.output = f"Deine Antwort ({len(response)} Zeichen) wurde gespeichert."
    
    # Next Question oder Analysis
    if len(state["user_responses"]) < 3:
        state["current_question_index"] += 1
        cl.user_session.set("state", state)
        await conduct_interview(state)
    else:
        # All 3 questions answered → Run Analysis
        cl.user_session.set("in_interview", False)
        await run_agent_analysis(state)


async def run_agent_analysis(state: AgentState):
    """Führt komplette Multi-Agent Analyse durch mit XAI Steps"""
    await cl.Message(
        content="""## 🔬 Starte Multi-Agent Analyse...

Das kann 20-30 Sekunden dauern. Du siehst gleich jeden Schritt transparent!"""
    ).send()
    
    # Run Reflection Agent
    async with cl.Step(name="🧠 Reflection Agent", type="llm") as step:
        step.output = "Analysiere alle 3 Antworten mit Chain-of-Thought Reasoning..."
        
        # Trigger graph
        result = agent_graph.invoke(state)
        
        # Show Reflection Results
        if result.get("response_analyses"):
            analyses_msg = "**Analyse pro Antwort:**\n\n"
            for i, analysis in enumerate(result["response_analyses"], 1):
                found_count = len([ind for ind in analysis.indicators_found if ind.found])
                analyses_msg += f"**Frage {i}:**\n"
                analyses_msg += f"- Preliminary Score: {analysis.score}/5\n"
                analyses_msg += f"- Confidence: {analysis.confidence:.0%}\n"
                analyses_msg += f"- Behavioral Indicators gefunden: {found_count}/{len(analysis.indicators_found)}\n\n"
            
            step.output = analyses_msg
        else:
            step.output = "Keine Analysen generiert (prüfe Logs)"
    
    # Assessment Agent
    async with cl.Step(name="📊 Assessment Agent", type="tool") as step:
        agent_score = result.get("agent_score", 0)
        step.output = f"""**Finaler Agent-Score:** {agent_score}/5

**Berechnungsmethode:** Gewichteter Durchschnitt aller 3 Antworten basierend auf Confidence-Levels der Reflection-Analysen."""
    
    # Dunning-Kruger
    async with cl.Step(name="🎯 Dunning-Kruger Analyse", type="tool") as step:
        dk_msg = f"""**Self-Report:** {result.get('self_report_score', 0)}/5  
**Agent-Score:** {result.get('agent_score', 0)}/5  
**Gap:** {result.get('dunning_kruger_gap', 0):+.1f}  
**Klassifikation:** {result.get('classification', 'unknown')}"""
        step.output = dk_msg
    
    # Final Feedback
    await show_final_feedback(result)


async def show_final_feedback(state: AgentState):
    """Zeigt finales Assessment mit Recommendations"""
    session_id = cl.user_session.get("session_id")
    
    # Save Assessment to Session
    assessment_data = {
        "skill_id": state.get("selected_skill"),
        "skill_name": GOLEMAN_FRAMEWORK["skills"][state.get("selected_skill")]["name"],
        "self_report": state.get("self_report_score"),
        "agent_score": state.get("agent_score"),
        "gap": state.get("dunning_kruger_gap"),
        "classification": state.get("classification"),
        "timestamp": datetime.now().isoformat(),
        "indicators_coverage": calculate_indicator_coverage(state.get("response_analyses", []))["coverage_percentage"]
    }
    
    session_manager.add_assessment(session_id, assessment_data)
    
    # Get Progress
    progress = session_manager.get_progress(session_id)
    
    # Coverage Stats
    coverage = calculate_indicator_coverage(state.get("response_analyses", []))
    strengths_weaknesses = get_strength_and_weaknesses(
        state.get("response_analyses", []),
        state.get("behavioral_indicators", [])
    )
    
    # Build Feedback Message
    skill_name = GOLEMAN_FRAMEWORK["skills"][state.get("selected_skill", "empathy")]["name"]
    
    feedback = f"""# 🎯 Assessment Ergebnis: {skill_name}

## 📊 Deine Scores

| Metrik | Wert |
|--------|------|
| Self-Report | {state.get('self_report_score', 0)}/5 |
| Agent-Score | {state.get('agent_score', 0)}/5 |
| Gap | {state.get('dunning_kruger_gap', 0):+.1f} |

---

{state.get('dk_interpretation', 'Keine Interpretation verfügbar.')}

---

## 💪 Deine Stärken

"""
    
    if strengths_weaknesses["strengths"]:
        for strength in strengths_weaknesses["strengths"]:
            feedback += f"✅ {strength}\n"
    else:
        feedback += "*(Noch keine klaren Stärken identifiziert - antworte ausführlicher für bessere Analyse)*\n"
    
    feedback += "\n## 📈 Entwicklungsfelder\n\n"
    
    if strengths_weaknesses["weaknesses"]:
        for weakness in strengths_weaknesses["weaknesses"]:
            feedback += f"⚠️ {weakness}\n"
    else:
        feedback += "*(Keine spezifischen Schwächen - du machst das gut!)*\n"
    
    feedback += f"""

---

## 💡 Empfehlungen

Basierend auf deinen Antworten:

1. **Stärke ausbauen:** Nutze deine {strengths_weaknesses['strengths'][0] if strengths_weaknesses['strengths'] else 'vorhandenen Fähigkeiten'} in herausfordernden Situationen
2. **Entwicklungsfeld:** Fokussiere dich auf {strengths_weaknesses['weaknesses'][0] if strengths_weaknesses['weaknesses'] else 'weitere Vertiefung'}
3. **Praxis:** Suche aktiv nach Situationen um diese Kompetenz zu üben

**Indicator Coverage:** {coverage['coverage_percentage']}% ({coverage['found_count']}/{coverage['total_indicators']})

---

## 📊 Session Progress: {progress['count']}/5 Dimensionen getestet
"""
    
    # Motivations-Messages basierend auf Progress
    if progress["count"] == 1:
        feedback += "\n🎯 **Noch 2 Dimensionen bis zum PDF-Report!** Weiter so!"
    elif progress["count"] == 2:
        feedback += "\n🎯 **Noch 1 Dimension bis zum PDF-Report!** Fast geschafft!"
    elif progress["count"] == 3:
        feedback += "\n🎉 **PDF-Report jetzt verfügbar!** Du kannst ihn gleich downloaden. Noch 2 Dimensionen für die vollständige Goleman-Analyse!"
    elif progress["count"] == 4:
        feedback += "\n🔥 **Nur noch 1 Dimension!** Hol dir die komplette Analyse nach Goleman. Kostenlos. Wissenschaftlich fundiert."
    elif progress["count"] == 5:
        feedback += "\n🏆 **GLÜCKWUNSCH!** Alle 5 Dimensionen nach Goleman getestet! Dein vollständiger Report wartet auf dich."
    
    feedback += "\n\n**Schreib 'Neu'** für eine andere Dimension oder **'Fertig'** zum Beenden."
    
    await cl.Message(content=feedback).send()
    
    # PDF Export anbieten (nur wenn ≥3 Dimensionen)
    if progress["can_download_pdf"]:
        # Frage ob User PDF will
        pdf_request = await cl.AskActionMessage(
            content="📄 **PDF-Report verfügbar!** Möchtest du ihn jetzt generieren?",
            actions=[
                cl.Action(name="pdf_yes", value="yes", label="✅ Ja, PDF erstellen"),
                cl.Action(name="pdf_no", value="no", label="❌ Nein, danke")
            ],
            timeout=60
        ).send()
        
        if pdf_request and pdf_request.get("value") == "yes":
            await offer_pdf_export(session_id)
    
    # Set flag for next action
    cl.user_session.set("awaiting_next_action", True)
    cl.user_session.set("state", None)


async def offer_pdf_export(session_id: str):
    """Bietet PDF-Export an wenn ≥3 Dimensionen"""
    from utils.pdf_generator import generate_pdf_report
    import shutil
    
    progress = session_manager.get_progress(session_id)
    
    if not progress["can_download_pdf"]:
        return
    
    # Frage nach Namen
    name_response = await cl.AskUserMessage(
        content="""## 📄 PDF-Report verfügbar!

Du hast **{count}/5 Dimensionen** getestet.

Möchtest du deinen personalisierten PDF-Report?

**Gib deinen Namen ein** (erscheint im Zertifikat):""".format(count=progress["count"]),
        timeout=300
    ).send()
    
    participant_name = name_response['output'].strip()
    
    if not participant_name:
        await cl.Message(content="❌ Kein Name eingegeben. PDF-Export abgebrochen.").send()
        return
    
    # Consent für Analytics
    consent = await cl.AskActionMessage(
        content="""## 🔒 Datenschutz

Deine Daten sind sicher! 

Möchtest du deine Ergebnisse **(anonymisiert)** für wissenschaftliche Analytics freigeben?

Dies hilft, das Tool zu verbessern.""",
        actions=[
            cl.Action(name="consent_yes", value="yes", label="✅ Ja, freigeben"),
            cl.Action(name="consent_no", value="no", label="❌ Nein, privat halten")
        ],
        timeout=60
    ).send()
    
    if consent and consent.get("value") == "yes":
        session_manager.update_consent(session_id, True)
    
    # Generiere PDF
    async with cl.Step(name="📄 Generiere PDF-Report") as step:
        step.output = "Erstelle Report mit Radar Chart..."
        
        session_data = session_manager.get_session(session_id)
        output_dir = Path("data/reports")
        
        try:
            pdf_path = generate_pdf_report(
                session_data=session_data,
                participant_name=participant_name,
                output_dir=output_dir
            )
            
            # WICHTIG: Kopiere PDF in Chainlit's public directory
            public_dir = Path("public")
            public_dir.mkdir(exist_ok=True)
            
            pdf_filename = Path(pdf_path).name
            public_pdf_path = public_dir / pdf_filename
            shutil.copy(pdf_path, public_pdf_path)
            
            step.output = f"✅ PDF erstellt: {pdf_filename}"
            
        except Exception as e:
            step.output = f"❌ Fehler: {e}"
            await cl.Message(content=f"❌ PDF-Generierung fehlgeschlagen: {e}").send()
            return
    
    # Sende Download-Link
    await cl.Message(
        content=f"""## 🎉 Dein Report ist fertig, {participant_name}!

**Klicke hier zum Download:**

[📄 **EI-Assessment Report herunterladen**](/{pdf_filename})


Möchtest du weitere Dimensionen testen? **Schreib 'Neu'!**"""
    ).send()

if __name__ == "__main__":
    cl.run()