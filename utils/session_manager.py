"""Session Management für Multi-Dimension Assessments"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import uuid


class SessionManager:
    """Verwaltet Session History und JSON Export"""
    
    def __init__(self):
        self.assessments_dir = Path("data/assessments")
        self.assessments_dir.mkdir(parents=True, exist_ok=True)
    
    def add_assessment(self, session_id: str, assessment_data: dict) -> None:
        """Fügt Assessment zu Session hinzu"""
        session_file = self.assessments_dir / f"session_{session_id}.json"
        
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
        else:
            session = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "user_consented": False,
                "assessments": []
            }
        
        session["assessments"].append(assessment_data)
        session["updated_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
    
    def get_session(self, session_id: str) -> dict:
        """Lädt Session Data"""
        session_file = self.assessments_dir / f"session_{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"assessments": []}
    
    def update_consent(self, session_id: str, consented: bool) -> None:
        """Updated User Consent"""
        session_file = self.assessments_dir / f"session_{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
            session["user_consented"] = consented
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
    
    def get_progress(self, session_id: str) -> dict:
        """Berechnet Progress"""
        session = self.get_session(session_id)
        tested = [a["skill_id"] for a in session["assessments"]]
        return {
            "count": len(tested),
            "tested": tested,
            "remaining": [s for s in ["self_awareness", "self_regulation", "motivation", "empathy", "social_skills"] if s not in tested],
            "can_download_pdf": len(tested) >= 3
        }