# Milestone 4.1.1 — Gemini Cloud Integration Patch

## What changed
- Both Streamlit pages read `GEMINI_API_KEY` from Streamlit Cloud Secrets (or an environment variable).
- No Gemini API key entry field appears in the public student interface.
- Gemini model is configured centrally via optional `GEMINI_MODEL`; the default is `gemini-3.1-flash-lite`. **Verify the exact model ID and availability in Google AI Studio before using it.**
- Existing deterministic business calculations, advisor grounding, fallback, and classroom exports are preserved.
- API failures are classified without exposing raw provider error details.

## Deploy
1. Replace your GitHub application files with the files inside `AI_Boardroom_PromptEd/`. **Keep the contents at the repository root**, not inside an extra folder.
2. In Streamlit Community Cloud → your app → Settings → Secrets, enter:

```toml
GEMINI_API_KEY = "your-private-key-here"
GEMINI_MODEL = "gemini-3.1-flash-lite"
```

3. Save Secrets and reboot/redeploy if needed. Do not commit a real `.streamlit/secrets.toml` or any key to GitHub.
4. In a private browser window, select Google Gemini on both pages. The sidebar should say it is administrator-configured and **must not show the key**.
5. Test a single advisor request first, then CEO Mentor. If responses fall back, inspect rate limits and Streamlit logs; a model being listed in AI Studio does not guarantee availability for a given API key.

## Important operational notes
- Public use consumes your project's quota; free-tier requests can be limited. Monitor Google AI Studio usage and supervise initial testing.
- This patch does **not** introduce authentication, per-student API quotas, persistent student storage, or a database. Use a small supervised pilot and fictional case data.
- Demo mode remains deterministic and is not generative AI. Local Ollama is not reachable from public Streamlit Cloud.
- The project includes no real API keys.
