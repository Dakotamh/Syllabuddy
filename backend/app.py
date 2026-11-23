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

DEADLINE_RE = re.compile(
    r"\b(exam|midterm|final|quiz|due|project|paper|assignment|lab|homework|essay|presentation|test)\b",
    re.I,
)
SKIP_RE = re.compile(r"\b(holiday|labor day|no class|break|past due|late)\b", re.I)

POLICY_PHRASES = {
    "late work": "Late work",
    "late submission": "Late work",
    "late assignment": "Late work",
    "late penalty": "Late work",
    "make-up": "Makeup work",
    "makeup": "Makeup work",
    "attendance": "Attendance",
    "office hours": "Office hours",
    "academic integrity": "Academic integrity",
    "plagiarism": "Academic integrity",
    "respond to email": "Email",
    "email response": "Email",
}


def clean_title(line):
    t = DATE_RE.sub("", line)                 # remove every date
    t = re.sub(r"\(\s*\)", "", t)             # empty parentheses
    t = re.sub(r"^\W*\d+\s*[-–]\s*", "", t)   # leading "2 - "
    t = re.sub(r"\s+", " ", t)
    return t.strip(" -–:|,.")


def find_info(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    course = re.search(r"\b([A-Z]{2,4})\s?-?(\d{3,4})\b(.*)", text)
    instructor = re.search(r"(?:Instructor|Professor|Prof\.|Taught by)\s*:?\s*([^\n]+)", text, re.I)
    term = re.search(r"\b(Fall|Spring|Summer|Winter)\s+(\d{4})", text, re.I)

    course_name = None
    if course:
        rest = re.split(r"Instructor|Professor|Prof\.", course.group(3))[0]
        rest = rest.split("\n")[0].strip(" -–:|")
        course_name = f"{course.group(1)} {course.group(2)} {rest}".strip()[:80]
    elif lines:
        course_name = lines[0][:80]

    deadlines, seen = [], set()
    for line in lines:
        d = DATE_RE.search(line)
        if not d or not DEADLINE_RE.search(line) or SKIP_RE.search(line):
            continue
        title = clean_title(line)
        key = (d.group(0), title.lower())
        if title and key not in seen and len(deadlines) < 40:
            seen.add(key)
            deadlines.append({"date": d.group(0), "title": title[:100]})

    grading, cats = [], set()
    for line in lines:
        p = re.search(r"(\d{1,3})\s*%", line)
        if p and len(line) < 60 and int(p.group(1)) <= 100:
            name = re.sub(r"\d{1,3}\s*%", "", line)
            name = re.sub(r"[^A-Za-z &/]", " ", name).strip()
            if 2 <= len(name) <= 40 and not name.lower().startswith("total") and name not in cats:
                cats.add(name)
                grading.append({"category": name, "percent": int(p.group(1))})

    policies, labels = [], set()
    for i, line in enumerate(lines):
        low = line.lower()
        for phrase, label in POLICY_PHRASES.items():
            if phrase in low and label not in labels:
                labels.add(label)
                detail = line
                if len(line) < 30 and i + 1 < len(lines):   # info is on the next line
                    detail = line + " " + lines[i + 1]
                policies.append({"label": label, "detail": detail[:160]})
                break

    return {
        "course_name": course_name,
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