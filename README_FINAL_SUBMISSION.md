# AI-Powered Boardroom — Final Submission Release

## Changes
- Public-facing header no longer shows internal milestone numbers or uncompleted classroom pilot claims.
- Streamlit default navigation hidden and explicit page links added, replacing the `app` label.
- Gemini diagnostic controls removed from the public sidebar.
- Administrator Gemini key remains in Streamlit Secrets. Users may optionally provide their own key via a masked session-only field.
- Developer credit added: Dr. Sanjay Jain, Professor, Department of Computer Science & Applications, ITM University Gwalior, India.

## Deploy
Upload all changed files at their existing paths. Keep the Streamlit Community Cloud entrypoint set to `app.py`. In particular, upload `.streamlit/config.toml` (the hidden `.streamlit` folder). No new packages are required.

## Security and usage
Never commit API keys. A personal key is held in Streamlit session state for the active session and sent to the selected Gemini provider for inference; do not promise browser-only processing. User-owned keys may incur charges. The application does not persist simulation data in its own database.

## Testing
Run `python -m pytest -q` in the project directory. Check sidebar page links, both pages, Gemini administrator and personal key modes, five advisors, CEO Mentor, and exports after deployment.
