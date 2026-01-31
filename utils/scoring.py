"""
Utility functions für Score-Berechnung und Validation.
"""
from typing import List
from agents.state import ResponseAnalysis


def calculate_indicator_coverage(analyses: List[ResponseAnalysis]) -> dict:
    """
    Berechnet wie viele Indicators über alle Antworten gefunden wurden.
    
    Returns:
        Dict mit Statistiken
    """
    all_indicators = set()
    found_indicators = set()
    
    for analysis in analyses:
        for ind in analysis.indicators_found:
            all_indicators.add(ind.indicator)
            if ind.found:
                found_indicators.add(ind.indicator)
        
        for missing in analysis.indicators_missing:
            all_indicators.add(missing)
    
    coverage = len(found_indicators) / len(all_indicators) if all_indicators else 0
    
    return {
        "total_indicators": len(all_indicators),
        "found_count": len(found_indicators),
        "coverage_percentage": round(coverage * 100, 1),
        "found_indicators": list(found_indicators),
        "missing_indicators": list(all_indicators - found_indicators)
    }


def get_strength_and_weaknesses(
    analyses: List[ResponseAnalysis],
    behavioral_indicators: List[str]
) -> dict:
    """
    Identifiziert Stärken und Schwächen basierend auf Indicator-Häufigkeit.
    """
    indicator_frequency = {ind: 0 for ind in behavioral_indicators}
    
    for analysis in analyses:
        for ind_score in analysis.indicators_found:
            if ind_score.found:
                indicator_frequency[ind_score.indicator] += 1
    
    # Sortiere nach Häufigkeit
    sorted_indicators = sorted(
        indicator_frequency.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Top 3 = Stärken, Bottom 2 = Schwächen
    strengths = [ind for ind, freq in sorted_indicators[:3] if freq > 0]
    weaknesses = [ind for ind, freq in sorted_indicators[-2:] if freq < 2]
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "indicator_frequency": indicator_frequency
    }