"""
PDF Report Generator für EI-Assessment
Erstellt 2-seitige Reports mit Radar Chart
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from pathlib import Path
from datetime import datetime
import io

# Dimensionen nach Goleman
DIMENSIONS = ["Selbstwahrnehmung", "Selbststeuerung", "Motivation", "Empathie", "Soziale Kompetenz"]


def create_radar_chart(session_data: dict, output_path: str) -> str:
    """
    Erstellt Radar Chart für alle getesteten Dimensionen.
    
    Args:
        session_data: Session mit assessments
        output_path: Pfad für Chart-Image
    
    Returns:
        Pfad zum gespeicherten Chart
    """
    # Sammle Scores
    scores = {dim: 0 for dim in DIMENSIONS}
    
    for assessment in session_data["assessments"]:
        skill_name = assessment["skill_name"]
        agent_score = assessment["agent_score"]
        scores[skill_name] = agent_score
    
    # Radar Chart Setup
    angles = np.linspace(0, 2 * np.pi, len(DIMENSIONS), endpoint=False).tolist()
    values = [scores[dim] for dim in DIMENSIONS]
    
    # Schließe den Kreis
    angles += angles[:1]
    values += values[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB', label='Agent-Score')
    ax.fill(angles, values, alpha=0.25, color='#2E86AB')
    ax.set_ylim(0, 5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(DIMENSIONS, size=12)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_pdf_report(
    session_data: dict,
    participant_name: str,
    output_dir: Path
) -> str:
    """
    Generiert kompletten 2-seitigen PDF-Report.
    
    Args:
        session_data: Session mit allen assessments
        participant_name: Name des Teilnehmers
        output_dir: Output-Verzeichnis
    
    Returns:
        Pfad zum generierten PDF
    """
    # Erstelle Output-Verzeichnis
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Dateinamen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = output_dir / f"EI_Report_{participant_name}_{timestamp}.pdf"
    chart_path = output_dir / f"radar_chart_{timestamp}.png"
    
    # Erstelle Radar Chart
    create_radar_chart(session_data, str(chart_path))
    
    # PDF erstellen
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
# ============ SEITE 1: INTRO ============
    
    # Farbiger Header-Bereich
    c.setFillColor(colors.HexColor("#2E86AB"))
    c.rect(0, height - 5.5*cm, width, 3*cm, fill=1, stroke=0)
    
    # Icon-Kreise (Gehirn-Symbol links, Herz-Symbol rechts)
    # Gehirn (Blau-Lila)
    c.setFillColor(colors.HexColor("#A23B72"))
    c.circle(5*cm, height - 3.8*cm, 0.9*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(5*cm, height - 4.1*cm, "EI")
    
    # Herz (Orange-Gold)
    c.setFillColor(colors.HexColor("#F18F01"))
    c.circle(width - 5*cm, height - 3.8*cm, 0.9*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width - 5*cm, height - 4.2*cm, "♥")
    
    # Title in weiß (zentriert)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 3.3*cm, "EMOTIONAL INTELLIGENCE")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 4.3*cm, "Assessment Report")
    
    # Zurück zu schwarz für Rest
    c.setFillColor(colors.black)
    
    # Teilnehmer Name
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 7*cm, participant_name)
    
    # Datum
    c.setFont("Helvetica", 12)
    date_str = datetime.now().strftime("%d. %B %Y")
    c.drawCentredString(width/2, height - 8*cm, f"Assessment durchgeführt am: {date_str}")
    
    # Linie
    c.setStrokeColor(colors.HexColor("#2E86AB"))
    c.setLineWidth(2)
    c.line(4*cm, height - 9*cm, width - 4*cm, height - 9*cm)
    
    # Warum EI wichtig ist
    c.setFont("Helvetica-Bold", 14)
    c.drawString(3*cm, height - 10.5*cm, "WARUM EMOTIONALE INTELLIGENZ?")
    
    c.setFont("Helvetica", 10)
    text_y = height - 11.8*cm
    lines = [
        "In der modernen Arbeitswelt sind technische Fähigkeiten nur die Basis.",
        "Studien zeigen: 90% erfolgreicher Leader haben hohe emotionale Intelligenz",
        "(u.a. Goleman, 1998).",
        "",
        "Moderne KI-Agenten sind mittlerweile in der Lage, menschliche Entscheidungs-",
        "prozesse zu simulieren und emotional intelligentes Verhalten objektiv zu",
        "bewerten. Dieser Report nutzt ein Multi-Agent-System, das deine Antworten",
        "nach der STAR-Methode analysiert und mit psychologischen Frameworks",
        "abgleicht - präzise, transparent und wissenschaftlich fundiert."
    ]
    for line in lines:
        c.drawString(3*cm, text_y, line)
        text_y -= 0.55*cm
    
    # Die 5 Dimensionen
    c.setFont("Helvetica-Bold", 13)
    c.drawString(3*cm, height - 17.5*cm, "DIE 5 DIMENSIONEN NACH GOLEMAN (1995)")
    
    c.setFont("Helvetica-Bold", 10)
    dimensions_y = height - 18.8*cm
    
    dimension_texts = [
        ("1. SELBSTWAHRNEHMUNG", "Eigene Emotionen erkennen und verstehen"),
        ("2. SELBSTSTEUERUNG", "Impulse kontrollieren, ruhig unter Druck bleiben"),
        ("3. MOTIVATION", "Intrinsischer Antrieb, hohe Standards setzen"),
        ("4. EMPATHIE", "Emotionen anderer verstehen und darauf eingehen"),
        ("5. SOZIALE KOMPETENZ", "Beziehungen managen, Teams führen")
    ]
    
    for title, desc in dimension_texts:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(3*cm, dimensions_y, title)
        c.setFont("Helvetica", 8)
        c.drawString(3.5*cm, dimensions_y - 0.45*cm, desc)
        dimensions_y -= 1.1*cm
    
    # Dunning-Kruger Erklärung
    c.setFont("Helvetica-Bold", 11)
    c.drawString(3*cm, dimensions_y - 0.7*cm, "DER DUNNING-KRUGER EFFEKT")
    
    c.setFont("Helvetica", 8.5)
    dk_y = dimensions_y - 1.3*cm
    dk_lines = [
        "Selbsteinschätzung ist schwierig: Wir neigen dazu, uns in Bereichen zu",
        "überschätzen, die wir noch lernen, und in Bereichen zu unterschätzen, in",
        "denen wir bereits kompetent sind (Kruger & Dunning, 1999). Dieser Report",
        "vergleicht deine Selbsteinschätzung mit deinem tatsächlichen Verhalten im",
        "STAR-Interview - für ein objektiveres, realistischeres Selbstbild."
    ]
    for line in dk_lines:
        c.drawString(3*cm, dk_y, line)
        dk_y -= 0.45*cm
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.grey)
    c.drawString(3*cm, 2*cm, "Powered by Multi-Agent AI System | Basierend auf STAR-Interview & Goleman Framework")
    c.drawRightString(width - 3*cm, 2*cm, "Seite 1/2")
    
    # Neue Seite
    c.showPage()
    
    # ============ SEITE 2: ERGEBNISSE ============
    
    # Header
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 2.5*cm, "DEINE ERGEBNISSE")
    
    # Getestete Dimensionen
    num_tested = len(session_data["assessments"])
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 3.5*cm, f"Getestete Dimensionen: {num_tested}/5")
    
    # Radar Chart
    c.drawImage(str(chart_path), 4*cm, height - 14*cm, width=13*cm, height=9*cm, preserveAspectRatio=True)
    
    # Detaillierte Scores
    c.setFont("Helvetica-Bold", 14)
    c.drawString(3*cm, height - 16*cm, "DETAILLIERTE SCORES")
    
    detail_y = height - 17.5*cm
    
    for assessment in session_data["assessments"]:
        skill_name = assessment["skill_name"]
        self_report = assessment["self_report"]
        agent_score = assessment["agent_score"]
        gap = assessment["gap"]
        classification = assessment["classification"]
        
        # Skill Name
        c.setFont("Helvetica-Bold", 12)
        c.drawString(3*cm, detail_y, f"📊 {skill_name.upper()}")
        detail_y -= 0.7*cm
        
        # Scores
        c.setFont("Helvetica", 10)
        c.drawString(3.5*cm, detail_y, f"Self-Report:  {self_report}/5")
        c.drawString(9*cm, detail_y, f"Agent-Score:  {agent_score}/5")
        detail_y -= 0.6*cm
        
        # Gap & Classification
        gap_text = f"Gap: {gap:+.1f}"
        if classification == "overconfident":
            classification_text = "⚠️ Selbstüberschätzung"
        elif classification == "underconfident":
            classification_text = "💪 Selbstunterschätzung"
        else:
            classification_text = "✓ Gut kalibriert"
        
        c.drawString(3.5*cm, detail_y, gap_text)
        c.drawString(6*cm, detail_y, classification_text)
        detail_y -= 1.2*cm
        
        # Check ob Platz für nächsten
        if detail_y < 5*cm:
            break
    
    # Footer - Stärkste/Schwächste Dimension
    if num_tested > 0:
        sorted_assessments = sorted(session_data["assessments"], key=lambda x: x["agent_score"], reverse=True)
        strongest = sorted_assessments[0]
        weakest = sorted_assessments[-1]
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(3*cm, 4*cm, "💪 STÄRKSTE DIMENSION")
        c.setFont("Helvetica", 10)
        c.drawString(3.5*cm, 3.5*cm, f"→ {strongest['skill_name']} ({strongest['agent_score']}/5)")
        
        if num_tested > 1:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(11*cm, 4*cm, "📈 ENTWICKLUNGSPOTENZIAL")
            c.setFont("Helvetica", 10)
            c.drawString(11.5*cm, 3.5*cm, f"→ {weakest['skill_name']} ({weakest['agent_score']}/5)")
    
    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawString(3*cm, 2*cm, f"Validiert durch Multi-Agent System | N={num_tested} behavioral assessments")
    c.drawRightString(width - 3*cm, 2*cm, "Seite 2/2")
    
    # Save PDF
    c.save()
    
    # Cleanup Chart
    chart_path.unlink()
    
    return str(pdf_path)