"""
Coordinator Agent - Hierarchical Supervisor
Orchestriert Reflection + Assessment Agents
"""
from typing import Literal
from agents.state import AgentState
import json


class CoordinatorAgent:
    """
    Supervisor Agent der entscheidet:
    - Welcher Agent als nächstes aktiv wird
    - Wann Assessment getriggert wird
    - Wann Feedback Loops nötig sind
    """
    
    def __init__(self):
        self.name = "Coordinator"
    
    def decide_next_step(self, state: AgentState) -> Literal[
        "framework_loading",
        "self_report", 
        "interview",
        "reflection",
        "assessment",
        "dunning_kruger",
        "feedback",
        "end"
    ]:
        """
        Routing Logic basierend auf State.
        
        Returns:
            Name des nächsten Nodes/Agents
        """
        
        # Decision Tree
        if not state.get("selected_skill"):
            return "framework_loading"
        
        if state.get("self_report_score") is None:
            return "self_report"
        
        if len(state.get("user_responses", [])) < 3:
            return "interview"
        
        if not state.get("response_analyses"):
            return "reflection"
        
        # Reflection Analysis vorhanden, prüfe Confidence
        if state.get("response_analyses"):
            avg_confidence = sum(
                a.confidence for a in state["response_analyses"]
            ) / len(state["response_analyses"])
            
            # Low Confidence → Trigger Assessment für Validation
            if avg_confidence < 0.8:
                decision = {
                    "agent": "Coordinator",
                    "decision": "trigger_assessment",
                    "reasoning": f"Reflection confidence {avg_confidence:.2f} < 0.8",
                    "timestamp": "now"
                }
                state.setdefault("agent_decisions", []).append(decision)
                return "assessment"
        
        if state.get("agent_score") is None:
            return "assessment"
        
        if state.get("dunning_kruger_gap") is None:
            return "dunning_kruger"
        
        if state.get("classification"):
            return "feedback"
        
        return "end"
    
    def should_trigger_feedback_loop(self, state: AgentState) -> bool:
        """
        Prüft ob Reflection und Assessment stark divergieren.
        
        Returns:
            True wenn Weighted Consensus nötig ist
        """
        if not state.get("response_analyses") or not state.get("agent_score"):
            return False
        
        # Durchschnittlicher Reflection Score
        reflection_score = sum(
            a.score for a in state["response_analyses"]
        ) / len(state["response_analyses"])
        
        agent_score = state["agent_score"]
        gap = abs(reflection_score - agent_score)
        
        return gap > 1.0