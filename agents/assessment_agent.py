"""
Assessment Agent - Behavioral Indicator Extractor
Führt strukturierte STAR-Interviews durch und bewertet EI-Komponenten.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState
from dotenv import load_dotenv
import json
import os

load_dotenv()


class AssessmentAgent:
    """
    Führt STAR-basierte Interviews und bewertet alle 5 EI-Komponenten parallel.
    Nutzt Few-Shot Examples für konsistente Bewertung.
    """
    
    def __init__(self):
        self.name = "Assessment"
        self.llm = ChatOpenAI(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            temperature=0.3  # Niedriger für konsistentere Bewertung
        )
        
        # Few-Shot Example für bessere Calibration
        self.few_shot_example = {
            "question": "Beschreibe eine Situation, in der jemand verärgert war.",
            "response": """Letzte Woche war mein Teamkollege frustriert, weil sein 
            Feature nicht rechtzeitig fertig wurde. Ich hab gemerkt, dass er gestresst 
            wirkte und hab ihn gefragt 'Hey, wie geht's dir damit?'. Er meinte, er 
            fühlt sich überfordert. Ich hab erstmal nur zugehört ohne direkt Lösungen 
            anzubieten und hab gesagt 'Ich verstehe, das ist echt viel auf einmal'.""",
            "expected_score": 4.0,
            "reasoning": "Starke Empathie-Signale: Emotionserkennung, aktives Zuhören, Validierung. Punkt Abzug weil Antizipation fehlt."
        }
    
    def calculate_final_score(self, state: AgentState) -> float:
        """
        Aggregiert alle Response-Analysen zu einem finalen Score.
        
        Verwendet gewichteten Durchschnitt basierend auf Confidence.
        """
        if not state.get("response_analyses"):
            return 1.0
        
        analyses = state["response_analyses"]
        
        # Weighted average basierend auf Confidence
        total_weight = sum(a.confidence for a in analyses)
        if total_weight == 0:
            # Fallback: einfacher Durchschnitt
            return sum(a.score for a in analyses) / len(analyses)
        
        weighted_sum = sum(a.score * a.confidence for a in analyses)
        final_score = weighted_sum / total_weight
        
        # Round to 1 decimal
        return round(final_score, 1)
    
    def validate_with_reflection(
        self, 
        agent_score: float,
        reflection_analyses: list
    ) -> dict:
        """
        Inter-Agent Validation: Vergleicht Assessment mit Reflection.
        
        Returns:
            Dict mit validation results
        """
        if not reflection_analyses:
            return {
                "validated": True,
                "alternative_score": None,
                "reasoning": "No reflection data available"
            }
        
        # Durchschnittlicher Reflection Score
        reflection_score = sum(a.score for a in reflection_analyses) / len(reflection_analyses)
        gap = abs(agent_score - reflection_score)
        
        if gap > 1.0:
            # Significant divergence
            return {
                "validated": False,
                "alternative_score": reflection_score,
                "reasoning": f"Large gap detected ({gap:.1f}). Reflection suggests score of {reflection_score:.1f}",
                "gap": gap
            }
        
        return {
            "validated": True,
            "alternative_score": reflection_score,
            "reasoning": f"Scores aligned within acceptable range (gap: {gap:.1f})",
            "gap": gap
        }
    
    def generate_evidence_summary(self, state: AgentState) -> list[dict]:
        """
        Extrahiert die wichtigsten Evidence-Zitate aus allen Analysen.
        
        Returns:
            Liste von {indicator, evidence, frequency} Dicts
        """
        if not state.get("response_analyses"):
            return []
        
        evidence_map = {}
        
        for analysis in state["response_analyses"]:
            for ind in analysis.indicators_found:
                if ind.found and ind.evidence:
                    key = ind.indicator
                    if key not in evidence_map:
                        evidence_map[key] = {
                            "indicator": key,
                            "evidence": [],
                            "frequency": 0
                        }
                    evidence_map[key]["evidence"].extend(ind.evidence)
                    evidence_map[key]["frequency"] += 1
        
        # Sortiere nach Häufigkeit
        return sorted(
            evidence_map.values(), 
            key=lambda x: x["frequency"], 
            reverse=True
        )