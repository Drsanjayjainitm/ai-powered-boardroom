# AI-Powered Boardroom

**Interactive Management Strategy and Decision-Making Simulator**

Developed by Dr. Sanjay Jain, Professor, Department of Computer Science & Applications, ITM University Gwalior, India.

## What it does

- CEO Strategy Studio: one-decision sandbox, five advisor perspectives, follow-up dialogue, comparisons, formative feedback.
- CEO Decision Lab: three cumulative revisions of the **same year-one scenario**, financial evidence, five advisors, CEO Mentor, learning analytics, and exports.
- Fictional Aarohan Retail scenario. Financial outputs are deterministic teaching assumptions, **not forecasts**.
- AI-generated coaching is screened; rule-based fallback is labeled. A classroom pilot has **not** been conducted.

## Local setup

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Python 3.10+ recommended. Select Demo mode for offline, rule-based testing. Gemini requires an API key; an administrator can configure it in Streamlit Community Cloud **Secrets** (never in GitHub).

## Guidelines

| Setup | Select in the app |
| --- | --- |
| Hosted Streamlit Community Cloud link | **Google Gemini** for live AI feedback when an API key is configured, or **Demo mode (no API key)** for rule-based feedback. |
| Streamlit running on your computer | **Ollama (local, free)** for local AI feedback. Follow the setup below. |

### Run Ollama with local Streamlit

1. Install [Ollama](https://ollama.com/download) and start it on the computer where you will run Streamlit. If the Ollama server is not already running, start it with `ollama serve` and leave that terminal open.
2. In another terminal, download the model with `ollama pull llama3.2:1b`. You can verify installation with `ollama list`.
3. Extract the source ZIP, open a terminal in the `AI_Boardroom_PromptEd` folder, and run:

   ```bash
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

4. In the **CEO Strategy Studio** or **CEO Decision Lab** sidebar, select **Ollama (local, free)** and keep the model set to `llama3.2:1b`. Request advisor feedback to confirm the connection. Ollama needs no API key for this setup.
5. If the app cannot reach Ollama, check that Ollama is running on the same computer and that the model appears in `ollama list`. The app connects to `http://localhost:11434`.

### Review using the hosted Streamlit link

Open the shared app link. Select **Google Gemini** for live AI feedback if the project owner has configured a key, or choose **Demo mode (no API key)** to explore the simulation with rule-based feedback.

On the hosted app, `localhost` refers to the Streamlit server. Installing Ollama on your own computer enables it when you run Streamlit locally. To offer Ollama through the hosted link, the project owner would need to deploy an Ollama service reachable from the Streamlit server and update the app to use that service.

## Streamlit Secrets (private, do not commit)

```toml
GEMINI_API_KEY = "your-private-key"
GEMINI_MODEL = "gemini-3.1-flash-lite"
```

The app also offers an optional session-only personal Gemini API key. Google provider limits and charges may apply.

## Deploy

1. Upload the contents of this ZIP's `AI_Boardroom_PromptEd` folder to the repository root.
2. Ensure `.streamlit/config.toml` is included; keep `app.py` as the main Streamlit entrypoint.
3. Configure Secrets in Streamlit Cloud, not in GitHub.
4. Verify both navigation pages, the five-advisor dashboard, CEO Mentor, and exports.

## Scope and privacy

Scenario values are illustrative. Learning rubric scores are formative, not validated competence measurements. The application does not intentionally persist student session data to a database. Do not upload personal or confidential information.
