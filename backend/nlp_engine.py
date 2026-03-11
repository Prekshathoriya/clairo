import re
import math
from collections import Counter
from typing import List, Dict, Tuple

# ── NLTK bootstrap ──────────────────────────────────────────────────────────
import nltk

def _ensure_nltk():
    for pkg in ("punkt", "punkt_tab", "stopwords", "averaged_perceptron_tagger"):
        try:
            nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)

_ensure_nltk()

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words("english"))

# ── Helpers ──────────────────────────────────────────────────────────────────

ACTION_VERBS = {
    "will", "shall", "should", "need", "must", "going to",
    "prepare", "create", "build", "review", "send", "schedule",
    "follow up", "complete", "finish", "start", "begin", "ensure",
    "coordinate", "assign", "draft", "update", "check", "test",
    "deploy", "present", "deliver", "write", "set up", "look into"
}

DECISION_PHRASES = [
    "decided", "agreed", "confirmed", "approved", "will launch",
    "we will", "the team will", "it was decided", "we agreed",
    "plan to", "going to launch", "going to release", "set for",
    "next week", "by friday", "by monday", "deadline is"
]


def parse_speakers(transcript: str) -> List[Tuple[str, str]]:
    """Return list of (speaker, utterance) from 'Speaker: text' format."""
    lines = []
    for line in transcript.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^([A-Za-z][A-Za-z\s]{0,30}):\s*(.+)$", line)
        if match:
            speaker = match.group(1).strip().title()
            text = match.group(2).strip()
            lines.append((speaker, text))
        else:
            # Attach to last speaker or tag as General
            if lines:
                last_sp, last_txt = lines[-1]
                lines[-1] = (last_sp, last_txt + " " + line)
            else:
                lines.append(("General", line))
    return lines


def speaker_stats(lines: List[Tuple[str, str]]) -> Dict[str, float]:
    """Word-count based participation share per speaker."""
    word_counts: Dict[str, int] = Counter()
    for speaker, text in lines:
        word_counts[speaker] += len(text.split())
    total = sum(word_counts.values()) or 1
    return {sp: round(count / total * 100, 1) for sp, count in word_counts.most_common()}


# ── TF-IDF summary ─────────────────────────────────────────────────────────

def _tfidf_summarize(text: str, n: int = 5) -> str:
    sentences = sent_tokenize(text)
    if len(sentences) <= n:
        return text

    # Build tf-idf scores
    word_freq: Counter = Counter()
    doc_freq: Counter = Counter()

    tokenized = []
    for sent in sentences:
        tokens = [w.lower() for w in word_tokenize(sent)
                  if w.isalpha() and w.lower() not in STOP_WORDS]
        tokenized.append(tokens)
        word_freq.update(tokens)
        doc_freq.update(set(tokens))

    num_docs = len(sentences)
    tfidf: Dict[str, float] = {}
    for word, freq in word_freq.items():
        tf = freq / (sum(word_freq.values()) or 1)
        idf = math.log((num_docs + 1) / (doc_freq[word] + 1)) + 1
        tfidf[word] = tf * idf

    scores = []
    for idx, tokens in enumerate(tokenized):
        score = sum(tfidf.get(t, 0) for t in tokens) / (len(tokens) or 1)
        scores.append((score, idx))

    top_indices = sorted([i for _, i in sorted(scores, reverse=True)[:n]])
    summary_sents = [sentences[i] for i in top_indices]
    return " ".join(summary_sents)


def generate_summary(lines: List[Tuple[str, str]]) -> str:
    full_text = " ".join(text for _, text in lines)
    raw = _tfidf_summarize(full_text, n=4)
    # Clean & capitalise
    sentences = sent_tokenize(raw)
    cleaned = [s.strip().capitalize() for s in sentences if len(s.split()) > 3]
    return " ".join(cleaned) if cleaned else "No summary could be generated."


# ── Action items ────────────────────────────────────────────────────────────

def extract_action_items(lines: List[Tuple[str, str]]) -> List[Dict]:
    items = []
    seen = set()
    for speaker, text in lines:
        sents = sent_tokenize(text)
        for sent in sents:
            lower = sent.lower()
            if any(verb in lower for verb in ACTION_VERBS):
                # Extract a clean short form
                short = sent.strip()
                key = short.lower()[:60]
                if key not in seen:
                    seen.add(key)
                    items.append({
                        "owner": speaker,
                        "task": short
                    })
    return items[:12]  # cap


# ── Key decisions ───────────────────────────────────────────────────────────

def extract_decisions(lines: List[Tuple[str, str]]) -> List[str]:
    decisions = []
    seen = set()
    for _, text in lines:
        sents = sent_tokenize(text)
        for sent in sents:
            lower = sent.lower()
            if any(phrase in lower for phrase in DECISION_PHRASES):
                key = lower[:60]
                if key not in seen:
                    seen.add(key)
                    decisions.append(sent.strip())
    return decisions[:8]


# ── Main entry ───────────────────────────────────────────────────────────────

def analyze_transcript(transcript: str) -> Dict:
    lines = parse_speakers(transcript)
    if not lines:
        return {
            "summary": "No valid transcript content found.",
            "action_items": [],
            "decisions": [],
            "speaker_stats": {}
        }

    return {
        "summary": generate_summary(lines),
        "action_items": extract_action_items(lines),
        "decisions": extract_decisions(lines),
        "speaker_stats": speaker_stats(lines)
    }
