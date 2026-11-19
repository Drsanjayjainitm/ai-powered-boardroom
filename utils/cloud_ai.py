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
    """Safe controls shared by both Streamlit pages."""
    key, model, configured = gemini_settings()
    if configured:
        st.success("Gemini is configured by the application administrator.")
        st.caption("The API key is stored privately and is not shown to students.")
    else:
        st.warning("Gemini is not configured. Ask the administrator to set GEMINI_API_KEY in Streamlit Secrets.")
        st.caption("Choose Demo mode until the administrator configures Gemini.")
    st.caption("Gemini model: " + model)
    return key, model
