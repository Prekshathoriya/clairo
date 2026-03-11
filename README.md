# 🎙 Clairo – AI Meeting Assistant

> Turn meetings into structured summaries instantly — powered by local NLP, no API keys required.

![Clairo Dashboard](https://via.placeholder.com/900x500/4F46E5/FFFFFF?text=Clairo+Dashboard+Screenshot)

---

## ✨ Features

| Feature | Description |
|---|---|
| **AI Meeting Summary** | TF-IDF extractive summarization of full transcripts |
| **Action Item Detection** | Identifies tasks & owners from speaker utterances |
| **Key Decisions** | Extracts decision statements from the conversation |
| **Speaker Insights** | Participation breakdown with animated bar chart |
| **Meeting History** | All meetings saved to local SQLite database |
| **Export TXT / PDF** | One-click export of formatted meeting notes |

---

## 🛠 Tech Stack

- **Backend**: Python · FastAPI · NLTK · SQLite · ReportLab
- **Frontend**: HTML · CSS · Vanilla JavaScript (zero frameworks)
- **NLP**: Local-only (no OpenAI, no Groq, no paid APIs)
- **Storage**: SQLite (`data/meetings.db`)

---

## 🚀 Quick Start

### 1. Clone or download the project

```bash
git clone https://github.com/yourusername/clairo.git
cd clairo
```

### 2. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Download NLTK data (auto-runs on first start, but you can pre-download)

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 4. Run the server

```bash
uvicorn app:app --reload
```

### 5. Open in browser

```
http://localhost:8000
```

---

## 📁 Project Structure

```
clairo/
├── backend/
│   ├── app.py            # FastAPI routes & server
│   ├── nlp_engine.py     # All NLP logic (summary, actions, decisions)
│   ├── database.py       # SQLite CRUD helpers
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Landing page
│   ├── dashboard.html    # Upload & analyze
│   ├── analysis.html     # View single meeting result
│   ├── history.html      # Browse all meetings
│   ├── css/
│   │   └── style.css     # Full design system
│   └── js/
│       └── app.js        # Shared JS utilities
├── data/
│   └── meetings.db       # Auto-created SQLite database
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze-meeting` | Analyze transcript (form-data: title, transcript/file, save) |
| `GET` | `/meetings` | List all saved meetings |
| `GET` | `/meetings/{id}` | Get single meeting |
| `DELETE` | `/meetings/{id}` | Delete a meeting |
| `GET` | `/export/{id}/txt` | Download TXT notes |
| `GET` | `/export/{id}/pdf` | Download PDF notes |

---

## 📝 Sample Transcript

Paste this into the Dashboard to try it out:

```
John: We should launch the marketing campaign next week.
Sara: I will prepare the creatives by Thursday.
John: Great. We also need to finalize the budget.
Sara: Agreed, I will send the budget breakdown by tomorrow.
Mike: I will schedule a review call for Friday to align everyone.
John: Perfect. Let's also confirm the target audience segments.
Sara: I can take that. I will draft the audience brief.
Mike: Decided – we launch on Monday the 15th.
```

---

## 🌐 Deployment

### Render (free tier)
1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

---

## 📸 Screenshots

| Landing Page | Dashboard | Analysis | History |
|---|---|---|---|
| ![](https://via.placeholder.com/200x130/4F46E5/FFF?text=Landing) | ![](https://via.placeholder.com/200x130/4F46E5/FFF?text=Dashboard) | ![](https://via.placeholder.com/200x130/4F46E5/FFF?text=Analysis) | ![](https://via.placeholder.com/200x130/4F46E5/FFF?text=History) |

---

## 👤 Author

Built as a portfolio demo project · [Your Name](https://github.com/yourusername)

---

## 📄 License

MIT
