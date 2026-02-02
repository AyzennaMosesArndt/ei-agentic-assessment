"""
Dunning-Kruger Analysis Module
Vergleicht Self-Report mit Agent-Assessment und klassifiziert Bias.
"""
from typing import Literal
from agents.state import AgentState

class DunningKrugerAnalyzer:
    """
    Analysiert Diskrepanz zwischen Selbsteinschätzung und tatsächlicher Leistung.
    """
    
    # Thresholds basierend auf Standardabweichung
    THRESHOLD_SIGNIFICANT = 1.0  # 1 Punkt auf 5er Skala
    THRESHOLD_EXTREME = 1.5
    
    def __init__(self, goleman_framework: dict = None):
        """
        Args:
            goleman_framework: Framework-Daten für Skill-Namen
        """
        self.framework = goleman_framework
    
    def calculate_gap(
        self, 
        self_report: float, 
        agent_score: float
    ) -> float:
        """
        Berechnet Gap zwischen Self-Report und Agent-Score.
        
        Returns:
            Positive = Overconfidence, Negative = Underconfidence
        """
        return round(self_report - agent_score, 2)
    
    def classify_bias(
        self, 
        gap: float
    ) -> Literal["overconfident", "calibrated", "underconfident"]:
        """
        Klassifiziert Bias-Typ basierend auf Gap.
        """
        if gap > self.THRESHOLD_SIGNIFICANT:
            return "overconfident"
        elif gap < -self.THRESHOLD_SIGNIFICANT:
            return "underconfident"
        else:
            return "calibrated"
    
    def get_interpretation(self, classification: str, gap: float, skill_name: str) -> str:
        """Generiert Interpretation (1-2 Sätze max)."""
        interpretations = {
            "overconfident": f"Du schätzt dich bei **{skill_name}** etwas höher ein als dein Verhalten zeigt (Gap: +{abs(gap):.1f}). Das ist normal und bietet Raum für Entwicklung.",
            
            "underconfident": f"Du unterschätzt deine **{skill_name}** (Gap: {gap:.1f}). Dein Verhalten zeigt mehr Kompetenz als du dir selbst zugestehst.",
            
            "calibrated": f"Deine Selbsteinschätzung bei **{skill_name}** stimmt gut mit deinem Verhalten überein (Gap: {gap:+.1f}). Das zeigt gute Selbstreflexion."
        }
        return interpretations[classification]
    
    def analyze(self, state: AgentState) -> dict:
        """
        Führt komplette Dunning-Kruger Analyse durch.
        
        Returns:
            Dict mit gap, classification, interpretation
        """
        self_report = state["self_report_score"]
        agent_score = state["agent_score"]
        
        # FIX: Hole den richtigen Skill-Namen
        skill_id = state.get("selected_skill", "empathy")
        
        # Wenn Framework verfügbar, hole echten Namen
        if self.framework and skill_id in self.framework.get("skills", {}):
            skill_name = self.framework["skills"][skill_id]["name"]
        else:
            # Fallback
            skill_name = "diese Kompetenz"
        
        gap = self.calculate_gap(self_report, agent_score)
        classification = self.classify_bias(gap)
        interpretation = self.get_interpretation(classification, gap, skill_name)
        
        return {
            "gap": gap,
            "classification": classification,
            "interpretation": interpretation,
            "is_extreme": abs(gap) > self.THRESHOLD_EXTREME
        }