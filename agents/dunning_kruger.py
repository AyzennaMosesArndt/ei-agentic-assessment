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
    
    def get_interpretation(
        self, 
        classification: str,
        gap: float,
        skill_name: str
    ) -> str:
        """
        Generiert psychologisch fundierte Interpretation.
        """
        interpretations = {
            "overconfident": f"""**Selbstüberschätzung erkannt** (Gap: +{abs(gap):.1f})

Du schätzt deine **{skill_name}** höher ein als dein gezeigtes Verhalten nahelegt. 
Das ist ein häufiges Phänomen (Dunning-Kruger Effekt), besonders bei Kompetenzen 
die schwer objektiv zu messen sind.

💡 **Was bedeutet das?**
- Du bist dir deiner Fähigkeiten bewusst, aber möglicherweise nicht aller Nuancen
- Es gibt Raum für Entwicklung, den du vielleicht noch nicht siehst
- Das ist normal und kein Grund zur Sorge!

📈 **Empfehlung:**
Achte besonders auf die Entwicklungsfelder im Feedback und hole dir externes 
Feedback von Kollegen/Freunden ein.""",
            
            "underconfident": f"""**Selbstunterschätzung erkannt** (Gap: {gap:.1f})

Du unterschätzt deine **{skill_name}**! Dein gezeigtes Verhalten in den Beispielen 
war stärker als deine Selbsteinschätzung vermuten lässt.

💡 **Was bedeutet das?**
- Du bist kompetenter als du denkst
- Möglicherweise zu selbstkritisch oder vergleichst dich mit unrealistischen Standards
- Das nennt man auch "Impostor Syndrome"

📈 **Empfehlung:**
Erkenne deine Stärken bewusst an! Du machst das besser als du glaubst.""",
            
            "calibrated": f"""**Gut kalibriert!** (Gap: {gap:+.1f})

Deine Selbsteinschätzung stimmt sehr gut mit deinem tatsächlichen Verhalten überein. 
Das zeigt hohe Selbstwahrnehmung - eine Kernkompetenz emotionaler Intelligenz!

💡 **Was bedeutet das?**
- Du hast ein realistisches Bild deiner **{skill_name}**
- Du kannst dich selbst gut reflektieren
- Das ist eine wichtige Basis für persönliche Entwicklung

📈 **Empfehlung:**
Nutze diese Selbstkenntnis um gezielt an den Entwicklungsfeldern zu arbeiten."""
        }
        
        return interpretations[classification].strip()
    
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