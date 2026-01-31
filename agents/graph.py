"""
LangGraph Workflow - Hierarchical Multi-Agent System
Orchestriert Coordinator, Reflection und Assessment Agents.
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.coordinator import CoordinatorAgent
from agents.reflection_agent import ReflectionAgent
from agents.assessment_agent import AssessmentAgent
from agents.dunning_kruger import DunningKrugerAnalyzer
import json
from pathlib import Path

# Load Framework für DK-Analyzer
FRAMEWORK_PATH = Path("data/frameworks/goleman_framework.json")
with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
    GOLEMAN_FRAMEWORK = json.load(f)

# Initialize Agents
coordinator = CoordinatorAgent()
reflection_agent = ReflectionAgent()
assessment_agent = AssessmentAgent()
dk_analyzer = DunningKrugerAnalyzer(goleman_framework=GOLEMAN_FRAMEWORK)


def framework_loading_node(state: AgentState) -> AgentState:
    """Lädt Goleman Framework für gewählten Skill."""
    state["next_step"] = "self_report"
    return state


def self_report_node(state: AgentState) -> AgentState:
    """Sammelt Self-Report Score vom User."""
    state["next_step"] = "interview"
    return state


def interview_node(state: AgentState) -> AgentState:
    """Führt STAR-Interview durch (3 Fragen)."""
    if len(state.get("user_responses", [])) >= 3:
        state["next_step"] = "reflection"
    return state


def reflection_node(state: AgentState) -> AgentState:
    """Reflection Agent analysiert alle 3 User-Antworten."""
    analyses = []
    
    for idx, response in enumerate(state["user_responses"]):
        analysis = reflection_agent.analyze_response(
            user_response=response,
            question=state["star_questions"][idx],
            behavioral_indicators=state["behavioral_indicators"],
            question_index=idx
        )
        analyses.append(analysis)
    
    state["response_analyses"] = analyses
    
    # Decision: Trigger Assessment?
    avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
    
    if avg_confidence < 0.8:
        state["next_step"] = "assessment"
        state.setdefault("agent_decisions", []).append({
            "agent": "Reflection",
            "decision": "low_confidence_trigger_assessment",
            "reasoning": f"Average confidence {avg_confidence:.2f} < 0.8",
            "value": avg_confidence
        })
    else:
        state["next_step"] = "assessment"
    
    return state


def assessment_node(state: AgentState) -> AgentState:
    """Assessment Agent berechnet finalen Score."""
    final_score = assessment_agent.calculate_final_score(state)
    state["agent_score"] = final_score
    
    # Validate with Reflection
    validation = assessment_agent.validate_with_reflection(
        agent_score=final_score,
        reflection_analyses=state.get("response_analyses", [])
    )
    
    state.setdefault("agent_decisions", []).append({
        "agent": "Assessment",
        "decision": "validation_check",
        "validated": validation["validated"],
        "gap": validation.get("gap"),
        "reasoning": validation["reasoning"]
    })
    
    # Check if Feedback Loop needed
    if not validation["validated"] and validation.get("gap", 0) > 1.0:
        reflection_score = validation["alternative_score"]
        
        # Weight by confidence
        reflection_conf = sum(a.confidence for a in state["response_analyses"]) / len(state["response_analyses"])
        assessment_conf = 0.85
        
        weighted_score = (
            final_score * assessment_conf + 
            reflection_score * reflection_conf
        ) / (assessment_conf + reflection_conf)
        
        state["agent_score"] = round(weighted_score, 1)
        
        state["agent_decisions"].append({
            "agent": "Coordinator",
            "decision": "weighted_consensus",
            "original_assessment": final_score,
            "original_reflection": reflection_score,
            "final_score": state["agent_score"],
            "reasoning": "Large divergence detected. Applied weighted consensus."
        })
    
    state["next_step"] = "dunning_kruger"
    return state


def dunning_kruger_node(state: AgentState) -> AgentState:
    """Dunning-Kruger Analyse."""
    dk_result = dk_analyzer.analyze(state)
    
    state["dunning_kruger_gap"] = dk_result["gap"]
    state["classification"] = dk_result["classification"]
    state["dk_interpretation"] = dk_result["interpretation"]
    
    state["next_step"] = "feedback"
    return state


def feedback_node(state: AgentState) -> AgentState:
    """Finales Feedback generieren."""
    state["next_step"] = "end"
    return state


def router(state: AgentState) -> Literal[
    "framework_loading",
    "self_report",
    "interview",
    "reflection",
    "assessment",
    "dunning_kruger",
    "feedback",
    "__end__"
]:
    """Coordinator entscheidet nächsten Schritt."""
    next_step = state.get("next_step", "framework_loading")
    
    if next_step == "end":
        return "__end__"
    
    return next_step


# Build Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("framework_loading", framework_loading_node)
workflow.add_node("self_report", self_report_node)
workflow.add_node("interview", interview_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("assessment", assessment_node)
workflow.add_node("dunning_kruger", dunning_kruger_node)
workflow.add_node("feedback", feedback_node)

# Set Entry Point
workflow.set_entry_point("framework_loading")

# Add Conditional Edges
workflow.add_conditional_edges(
    "framework_loading",
    router,
    {
        "self_report": "self_report",
        "__end__": END
    }
)

workflow.add_conditional_edges(
    "self_report",
    router,
    {
        "interview": "interview",
        "__end__": END
    }
)

workflow.add_conditional_edges(
    "interview",
    router,
    {
        "interview": "interview",
        "reflection": "reflection",
        "__end__": END
    }
)

workflow.add_conditional_edges(
    "reflection",
    router,
    {
        "assessment": "assessment",
        "__end__": END
    }
)

workflow.add_conditional_edges(
    "assessment",
    router,
    {
        "dunning_kruger": "dunning_kruger",
        "__end__": END
    }
)

workflow.add_conditional_edges(
    "dunning_kruger",
    router,
    {
        "feedback": "feedback",
        "__end__": END
    }
)

workflow.add_conditional_edges(
    "feedback",
    router,
    {
        "__end__": END
    }
)

# Compile
app = workflow.compile()