# Syllabuddy

Upload a course syllabus and get every deadline, exam, grading weight, and policy in one place, with no digging through Canvas.

Built as a class project for [COURSE NAME] at [SCHOOL].

## Features

- Upload a syllabus PDF
- Automatically extracts course name, instructor, and term
- Pulls out deadlines and exam dates
- Shows the grading breakdown
- Finds key policies (late work, attendance, office hours)

## Screenshots

<img width="1920" height="1080" alt="Upload png" src="https://github.com/user-attachments/assets/b0901450-9f4a-41f0-8145-b001c7e0957e" />
<img width="1920" height="1080" alt="Results png" src="https://github.com/user-attachments/assets/e125d824-77b7-4225-a2cb-5087d4e51f63" />


## Tech stack

- **Frontend:** React + Vite
- **Backend:** Python, Flask
- **PDF parsing:** pdfplumber
- **Extraction:** rule-based pattern matching (regular expressions)

## How to run it

You need Node.js (v22 or newer) and Python 3.

**1. Start the backend**
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install flask flask-cors pdfplumber
python app.py
```

**2. Start the frontend** (in a second terminal)
```
cd frontend
npm install
npm run dev
```

Open the link Vite prints (usually http://localhost:5173) and upload a syllabus PDF.

## How it works

1. The frontend sends the PDF to the Flask backend.
2. The backend extracts the text with pdfplumber.
3. Pattern matching finds dates, percentages, and policy keywords.
4. The results come back as JSON and display on the Results screen.

## Limitations

- Scanned (image-only) PDFs aren't supported because they have no text to read.
- Extraction depends on each syllabus's format, so tables and unusual layouts may be missed.

## Future improvements

- Dashboard combining deadlines from all courses
- Calendar export
- AI-based extraction for more accurate results
- Support for DOCX files
