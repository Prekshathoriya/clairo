import os
import json
import io
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from nlp_engine import analyze_transcript
from database import init_db, save_meeting, get_all_meetings, get_meeting_by_id, delete_meeting

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="Clairo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.on_event("startup")
def startup():
    init_db()

# ── Models ────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    transcript: str
    title: Optional[str] = "Untitled Meeting"
    save: Optional[bool] = True

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/dashboard")
def dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/analysis")
def analysis_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "analysis.html"))

@app.get("/history")
def history_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))

@app.post("/analyze-meeting")
async def analyze_meeting(
    transcript: str = Form(None),
    title: str = Form("Untitled Meeting"),
    save: bool = Form(True),
    file: UploadFile = File(None)
):
    if file:
        content = await file.read()
        transcript = content.decode("utf-8", errors="ignore")
        if not title or title == "Untitled Meeting":
            title = file.filename.replace(".txt", "").replace("_", " ").title()

    if not transcript or not transcript.strip():
        raise HTTPException(status_code=400, detail="No transcript provided.")

    result = analyze_transcript(transcript)

    meeting_id = None
    if save:
        meeting_id = save_meeting(title, transcript, result)

    result["meeting_id"] = meeting_id
    result["title"] = title
    return result

@app.get("/meetings")
def list_meetings():
    return get_all_meetings()

@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: int):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return meeting

@app.delete("/meetings/{meeting_id}")
def remove_meeting(meeting_id: int):
    delete_meeting(meeting_id)
    return {"status": "deleted"}

@app.get("/export/{meeting_id}/txt")
def export_txt(meeting_id: int):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    lines = [
        f"CLAIRO – MEETING NOTES",
        f"{'='*50}",
        f"Title: {meeting['title']}",
        f"Date:  {meeting['created_at'][:10]}",
        f"",
        f"SUMMARY",
        f"-------",
        meeting['summary'],
        f"",
        f"KEY DECISIONS",
        f"-------------",
    ]
    for d in meeting['decisions']:
        lines.append(f"  • {d}")
    lines += ["", "ACTION ITEMS", "------------"]
    for item in meeting['action_items']:
        lines.append(f"  [{item['owner']}] {item['task']}")
    lines += ["", "SPEAKER PARTICIPATION", "---------------------"]
    for speaker, pct in meeting['speaker_stats'].items():
        lines.append(f"  {speaker}: {pct}%")

    content = "\n".join(lines)
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=clairo_{meeting_id}.txt"}
    )

@app.get("/export/{meeting_id}/pdf")
def export_pdf(meeting_id: int):
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_LEFT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2.5*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        PRIMARY = colors.HexColor("#4F46E5")

        title_style = ParagraphStyle("Title", parent=styles["Title"],
                                     textColor=PRIMARY, fontSize=20, spaceAfter=4)
        h2 = ParagraphStyle("H2", parent=styles["Heading2"],
                             textColor=PRIMARY, fontSize=13, spaceBefore=14, spaceAfter=4)
        body = styles["BodyText"]
        body.fontSize = 10

        story = [
            Paragraph("Clairo – Meeting Notes", title_style),
            Paragraph(f"<b>{meeting['title']}</b>", styles["Heading2"]),
            Paragraph(f"Date: {meeting['created_at'][:10]}", body),
            HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=10),
            Paragraph("Summary", h2),
            Paragraph(meeting['summary'] or "—", body),
        ]

        if meeting['decisions']:
            story.append(Paragraph("Key Decisions", h2))
            for d in meeting['decisions']:
                story.append(Paragraph(f"• {d}", body))

        if meeting['action_items']:
            story.append(Paragraph("Action Items", h2))
            for item in meeting['action_items']:
                story.append(Paragraph(f"<b>[{item['owner']}]</b> {item['task']}", body))

        if meeting['speaker_stats']:
            story.append(Paragraph("Speaker Participation", h2))
            for sp, pct in meeting['speaker_stats'].items():
                story.append(Paragraph(f"• {sp}: {pct}%", body))

        doc.build(story)
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=clairo_{meeting_id}.pdf"}
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab not installed for PDF export.")
