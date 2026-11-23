import { useState } from "react";
import "./App.css";

export default function App() {
  const [stage, setStage] = useState("upload");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function handleFile(file) {
    if (!file) return;
    setError("");
    setStage("processing");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: form,
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Upload failed");
      setData(json);
      setStage("results");
    } catch (e) {
      setError(e.message + " (is the backend running?)");
      setStage("upload");
    }
  }

  return (
    <div className="app">
      <header>
        <div className="logo"><span className="dot" />Syllabuddy</div>
      </header>

      {stage === "upload" && (
        <main className="center">
          <h1>Upload your syllabus</h1>
          <p className="sub">
            Get every deadline, exam, and policy in one place, without digging through Canvas.
          </p>
          <div className="drop">
            <p>PDF files only</p>
            <label className="btn">
              Choose file
              <input
                type="file"
                accept=".pdf"
                hidden
                onChange={(e) => handleFile(e.target.files[0])}
              />
            </label>
          </div>
          {error && <p className="error">{error}</p>}
        </main>
      )}

      {stage === "processing" && (
        <main className="center">
          <div className="card">
            <h2>Reading your syllabus...</h2>
            <div className="bar"><div className="fill" /></div>
          </div>
        </main>
      )}

      {stage === "results" && data && (
        <main className="wide">
          <div className="top">
            <div>
              <h1>{data.course_name || "Your course"}</h1>
              <p className="sub">
                {[data.instructor, data.term].filter(Boolean).join(" · ")}
              </p>
            </div>
            <button className="btn" onClick={() => setStage("upload")}>
              Upload another
            </button>
          </div>

          <div className="grid">
            <section className="card">
              <h2>Deadlines</h2>
              {data.deadlines.length === 0 && <p className="sub">None found.</p>}
              {data.deadlines.map((d, i) => (
                <div className="row" key={i}>
                  <span>{d.title}</span>
                  <span className="muted">{d.date}</span>
                </div>
              ))}
            </section>

            <div className="stack">
              <section className="card">
                <h2>Grading</h2>
                {data.grading.length === 0 && <p className="sub">None found.</p>}
                <div className="stats">
                  {data.grading.map((g, i) => (
                    <div className="stat" key={i}>
                      <div className="muted">{g.category}</div>
                      <strong>{g.percent}%</strong>
                    </div>
                  ))}
                </div>
              </section>

              <section className="card">
                <h2>Policies</h2>
                {data.policies.length === 0 && <p className="sub">None found.</p>}
                {data.policies.map((p, i) => (
                  <div className="row" key={i}>
                    <span>{p.label}</span>
                    <span className="muted small">{p.detail}</span>
                  </div>
                ))}
              </section>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}