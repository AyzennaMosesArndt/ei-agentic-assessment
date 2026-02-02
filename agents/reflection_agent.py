"""
Reflection Agent - Episodic Memory Specialist
Analysiert User-Antworten mit Chain-of-Thought
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState, ResponseAnalysis, STARAnalysis, IndicatorScore
from dotenv import load_dotenv
import json
import os

load_dotenv()


class ReflectionAgent:
    """
    Verarbeitet narrative User-Antworten → episodisches Gedächtnis
    Nutzt Chain-of-Thought Prompting für STAR + EI Indicator Extraction
    """
    
    def __init__(self):
        self.name = "Reflection"
        self.llm = ChatOpenAI(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            temperature=float(os.getenv("TEMPERATURE", "0.7"))
        )
    
    def analyze_response(
        self, 
        user_response: str,
        question: str,
        behavioral_indicators: list[str],
        question_index: int
    ) -> ResponseAnalysis:
        """
        Analysiert eine User-Antwort mit CoT.
        
        Args:
            user_response: Die Antwort des Users
            question: Die gestellte STAR-Frage
            behavioral_indicators: Liste der zu prüfenden Indicators
            question_index: Index der Frage (0-2)
        
        Returns:
            ResponseAnalysis Objekt mit strukturierten Ergebnissen
        """
        
        system_prompt = f"""Du bist ein Reflection Agent für EI-Assessment.

Analysiere User-Antworten schrittweise mit Chain-of-Thought:

WICHTIG - BEWERTUNGSPRINZIPIEN:
- Sei wohlwollend: Wenn ein Indicator auch nur ansatzweise erkennbar ist → found=true
- Implizite Hinweise zählen: "hab das gelöst" → zeigt Problemlösungskompetenz
- Kurze Antworten: Extrahiere das Maximum aus wenigen Worten
- Benefit of the doubt: Im Zweifel für den User
- Fokus auf Stärken: Suche aktiv nach positiven Signalen

SCHRITT 1: STAR Extraction
- Situation: Was war der Kontext?
- Task: Welche Herausforderung?
- Action: Was hat User gemacht?
- Result: Was war das Ergebnis?

SCHRITT 2: EI Indicator Mapping
Prüfe jeden dieser Behavioral Indicators:
{json.dumps(behavioral_indicators, indent=2, ensure_ascii=False)}

Für jeden Indicator:
- Gefunden? (true/false)
- Evidence: Konkrete Zitate aus der Antwort (als Liste)
- Confidence: 0.0-1.0

SCHRITT 3: Scoring (1-5 Skala)
- 5 = Alle 5 Indicators demonstriert (auch implizit)
- 4 = 4 Indicators ODER 3 sehr stark
- 3 = 3 Indicators klar vorhanden
- 2 = 1-2 Indicators
- 1 = Keine klaren Indicators

SCHRITT 4: Reasoning
Erkläre deine Bewertung evidence-based, fokussiere auf Stärken.

OUTPUT FORMAT (nur JSON, keine Markdown, lowercase keys):
{{
  "star_analysis": {{
    "situation": "...",
    "task": "...",
    "action": "...",
    "result": "..."
  }},
  "indicators_found": [
    {{
      "indicator": "Indicator Name",
      "found": true,
      "evidence": ["Zitat 1", "Zitat 2"],
      "confidence": 0.85
    }}
  ],
  "indicators_missing": ["Indicator Name 1", "Indicator Name 2"],
  "score": 3.5,
  "reasoning": "Detaillierte Begründung...",
  "confidence": 0.80
}}
"""
        
        user_prompt = f"""Frage: {question}

User-Antwort:
{user_response}

Analysiere diese Antwort Schritt für Schritt."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON Response
        try:
            result = json.loads(response.content)
            
            # FIX 1: Normalize STAR keys (LLM gibt manchmal Capitalized zurück)
            star_raw = result.get("star_analysis", {})
            star_normalized = {
                "situation": star_raw.get("Situation") or star_raw.get("situation", ""),
                "task": star_raw.get("Task") or star_raw.get("task", ""),
                "action": star_raw.get("Action") or star_raw.get("action", ""),
                "result": star_raw.get("Result") or star_raw.get("result", "")
            }
            
            # FIX 2: Ensure evidence is always a list
            for ind in result.get("indicators_found", []):
                if isinstance(ind.get("evidence"), str):
                    ind["evidence"] = [ind["evidence"]] if ind["evidence"] else []
                elif not isinstance(ind.get("evidence"), list):
                    ind["evidence"] = []
            
            # FIX 3: Ensure indicators_missing is list of strings (not dicts)
            indicators_missing = result.get("indicators_missing", [])
            if indicators_missing and isinstance(indicators_missing[0], dict):
                indicators_missing = [ind.get("indicator", "") for ind in indicators_missing]
            
            # Convert to ResponseAnalysis
            return ResponseAnalysis(
                question_id=question_index,
                star_analysis=STARAnalysis(**star_normalized),
                indicators_found=[
                    IndicatorScore(**ind) for ind in result["indicators_found"]
                ],
                indicators_missing=indicators_missing,
                score=result["score"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw response: {response.content[:500]}")
            return ResponseAnalysis(
                question_id=question_index,
                star_analysis=STARAnalysis(
                    situation="Parse Error",
                    task="",
                    action="",
                    result=""
                ),
                indicators_found=[],
                indicators_missing=behavioral_indicators,
                score=1.0,
                reasoning="LLM Response konnte nicht geparst werden",
                confidence=0.0
            )
        
        except Exception as e:
            print(f"❌ Error creating ResponseAnalysis: {e}")
            print(f"Result: {result if 'result' in locals() else 'N/A'}")
            return ResponseAnalysis(
                question_id=question_index,
                star_analysis=STARAnalysis(
                    situation="Error",
                    task="",
                    action="",
                    result=""
                ),
                indicators_found=[],
                indicators_missing=behavioral_indicators,
                score=1.0,
                reasoning=f"Error: {str(e)}",
                confidence=0.0
            )