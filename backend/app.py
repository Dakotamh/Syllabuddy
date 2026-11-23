import re
import pdfplumber
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MONTHS = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
DATE_RE = re.compile(
    rf"\b({MONTHS}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,\s*\d{{4}})?|\d{{1,2}}/\d{{1,2}}(?:/\d{{2,4}})?)",
    re.I,
)
DEADLINE_WORDS = ("exam", "midterm", "final", "quiz", "due", "project", "paper",
                  "assignment", "lab", "homework", "essay", "presentation", "test")
POLICY_WORDS = {
    "late": "Late work",
    "attendance": "Attendance",
    "office hours": "Office hours",
    "academic integrity": "Academic integrity",
    "plagiarism": "Academic integrity",
    "email": "Email",
}


def find_info(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    course = re.search(r"\b([A-Z]{2,4})\s?-?(\d{3,4})\b([^\n]*)", text)
    instructor = re.search(r"(?:Instructor|Professor|Prof\.|Taught by)\s*:?\s*([^\n]+)", text, re.I)
    term = re.search(r"\b(Fall|Spring|Summer|Winter)\s+(\d{4})", text, re.I)

    deadlines, seen = [], set()
    for line in lines:
        d = DATE_RE.search(line)
        if d and any(w in line.lower() for w in DEADLINE_WORDS):
            title = line.replace(d.group(0), "").strip(" -:|,.")
            key = (d.group(0), title.lower())
            if key not in seen and len(deadlines) < 40:
                seen.add(key)
                deadlines.append({"date": d.group(0), "title": title[:100] or line[:100]})

    grading = []
    for line in lines:
        p = re.search(r"(\d{1,3})\s*%", line)
        if p and len(line) < 60 and int(p.group(1)) <= 100:
            name = re.sub(r"\d{1,3}\s*%", "", line)
            name = re.sub(r"[^A-Za-z &/]", " ", name).strip()
            if 2 <= len(name) <= 40:
                grading.append({"category": name, "percent": int(p.group(1))})

    policies, labels = [], set()
    for line in lines:
        low = line.lower()
        for word, label in POLICY_WORDS.items():
            if word in low and label not in labels:
                labels.add(label)
                policies.append({"label": label, "detail": line[:160]})
                break

    return {
        "course_name": (f"{course.group(1)} {course.group(2)}{course.group(3)}".strip()[:80]
                        if course else lines[0][:80] if lines else None),
        "instructor": instructor.group(1).strip()[:60] if instructor else None,
        "term": f"{term.group(1).title()} {term.group(2)}" if term else None,
        "deadlines": deadlines,
        "grading": grading,
        "policies": policies,
    }


@app.post("/upload")
def upload():
    file = request.files["file"]
    with pdfplumber.open(file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    if not text.strip():
        return jsonify(error="No text found. Is this a scanned PDF?"), 400
    return jsonify(find_info(text))


if __name__ == "__main__":
    app.run(port=5000, debug=True)