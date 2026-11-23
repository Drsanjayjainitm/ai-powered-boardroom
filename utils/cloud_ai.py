"""Shared cloud AI configuration. Never render or log API secrets."""
import os
import streamlit as st

DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"

def secret_value(name, default=""):
    """Read Streamlit Secrets, falling back to an environment variable."""
    try:
        value = st.secrets.get(name, None)
        if value:
            return str(value).strip()
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    return os.environ.get(name, default).strip()

def gemini_settings():
    """Return (key, model, centrally_configured); no key is exposed in UI."""
    key = secret_value("GEMINI_API_KEY")
    model = secret_value("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    return key, model, bool(key)

def gemini_sidebar():
    """Session-only optional personal key; administrator key stays secret."""
    admin_key, model, configured = gemini_settings()
    if configured:
        st.success("Gemini AI is available for this session.")
    else:
        st.info("Enter your own Gemini API key to enable AI coaching, or use Demo mode.")

    use_own_key = st.checkbox(
        "Use personal Gemini API key",
        value=False,
        key="boardroom_use_own_gemini_key",
        help="Your key is used only for requests in this browser session and is not saved by the application.",
    )
    if use_own_key:
        personal_key = st.text_input(
            "Personal Gemini API key", type="password", value="",
            key="boardroom_personal_gemini_key",
            help="Do not share your key in screenshots, reports or public repositories.",
        ).strip()
        st.caption("Used for this session only; Google usage limits or charges may apply. Do not enter shared credentials.")
        if not personal_key:
            st.warning("Enter your key, or untick this option to use the application key.")
        key = personal_key  # Never silently use administrator quota when BYOK was selected.
    else:
        key = admin_key
        if not configured:
            st.caption("No administrator Gemini key is configured.")

    st.caption("AI model: " + model)
    # Administrator diagnostics are intentionally not exposed in this public release.
    return key, model


