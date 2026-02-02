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
                        - Evidence: Konkrete Zitate aus der Antwort
                        - Confidence: 0.0-1.0

                        WICHTIG - BEWERTUNGSPRINZIPIEN:
                        - Sei wohlwollend: Wenn ein Indicator auch nur teilweise demonstriert wird → found=true
                        - Implizite Hinweise zählen: "hab das Team zusammengebracht" → zeigt soziale Kompetenz
                        - Benefit of the doubt: Im Zweifel für den User
                        - Fokus auf Stärken: Suche aktiv nach positiven Signalen

                        SCHRITT 3: Scoring (1-5 Skala)
                        - 5 = Alle 5 Indicators demonstriert (auch implizit)
                        - 4 = 4 Indicators ODER 3 sehr stark
                        - 3 = 3 Indicators klar vorhanden
                        - 2 = 1-2 Indicators
                        - 1 = Keine klaren Indicators

                        SCHRITT 4: Reasoning
                        Erkläre deine Bewertung evidence-based, fokussiere auf Stärken.

                        OUTPUT FORMAT (nur JSON, keine Markdown):
                        {{
                        "star_analysis": {{...}},
                        "indicators_found": [...],
                        "indicators_missing": [...],
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
            
            # Ensure evidence is always a list
            for ind in result.get("indicators_found", []):
                if isinstance(ind.get("evidence"), str):
                    # Convert single string to list
                    ind["evidence"] = [ind["evidence"]] if ind["evidence"] else []
                elif not isinstance(ind.get("evidence"), list):
                    ind["evidence"] = []
            
            # Convert to ResponseAnalysis
            return ResponseAnalysis(
                question_id=question_index,
                star_analysis=STARAnalysis(**result["star_analysis"]),
                indicators_found=[
                    IndicatorScore(**ind) for ind in result["indicators_found"]
                ],
                indicators_missing=result["indicators_missing"],
                score=result["score"],
                reasoning=result["reasoning"],
                confidence=result["confidence"]
            )
        
        except json.JSONDecodeError as e:
            # Fallback bei Parse-Error
            print(f"JSON Parse Error: {e}")
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
            # Catch any other errors
            print(f"Error creating ResponseAnalysis: {e}")
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