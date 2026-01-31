"""
Shared State für das Multi-Agent System.
Alle Agents greifen auf diesen State zu.
"""
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class STARAnalysis(BaseModel):
    """Struktur für STAR-Method Extraction"""
    situation: str = Field(description="Beschreibung der Situation/Kontext")
    task: str = Field(description="Die Aufgabe/Herausforderung")
    action: str = Field(description="Was der User gemacht hat")
    result: str = Field(description="Das Ergebnis/Outcome")


class IndicatorScore(BaseModel):
    """Bewertung eines einzelnen Behavioral Indicators"""
    indicator: str
    found: bool
    evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class ResponseAnalysis(BaseModel):
    """Analyse einer einzelnen User-Antwort"""
    question_id: int
    star_analysis: STARAnalysis
    indicators_found: List[IndicatorScore]
    indicators_missing: List[str]
    score: float = Field(ge=1.0, le=5.0)
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)


class AgentState(TypedDict):
    """Globaler State für alle Agents"""
    
    # Chat History
    messages: Annotated[List, add_messages]
    
    # User Input
    selected_skill: Optional[str]
    self_report_score: Optional[float]
    
    # Framework Data
    skill_definition: Optional[str]
    behavioral_indicators: Optional[List[str]]
    star_questions: Optional[List[str]]
    
    # Interview Data
    current_question_index: int
    user_responses: List[str]
    
    # Analysis Results
    response_analyses: List[ResponseAnalysis]
    
    # Final Assessment
    agent_score: Optional[float]
    dunning_kruger_gap: Optional[float]
    classification: Optional[str]  # "overconfident", "calibrated", "underconfident"
    
    # Agent Decision Tracking (für XAI)
    agent_decisions: List[dict]
    
    # Control Flow
    next_step: str  # "framework_loading", "self_report", "interview", etc.