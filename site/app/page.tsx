export default function Home() {
  return (
    <main style={{ padding: 24, maxWidth: 720 }}>
      <h1>Vocamate</h1>
      <p>
        Open-source voice/agent starter. Python core (ASR/TTS/LLM) +
        this minimal Next.js site for docs/demo on Vercel.
      </p>
      <ul>
        <li><a href="/api/ping">API health (site)</a></li>
        <li><a href="https://github.com/developerplugin/vocomate">GitHub Repo</a></li>
      </ul>
      <h2>Run the Python App</h2>
      <pre>
        pip install -r requirements.txt{'\n'}
        uvicorn vocomate_app.main:app --reload
      </pre>
      <p>Then open <code>http://localhost:8000/health</code></p>
    </main>
  );
}
