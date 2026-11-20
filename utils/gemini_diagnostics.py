"""Gemini connectivity checks with deliberately sanitized diagnostics."""
import re


def classify_error(exc):
    """Avoid exposing raw provider exception text (which can contain request data)."""
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if isinstance(status, str) and status.isdigit():
        status = int(status)
    # google.genai.errors.ClientError commonly includes the HTTP status in its string.
    # Only extract a 3-digit HTTP code, never display the exception text itself.
    if not isinstance(status, int):
        match = re.search(r"(?<!\d)(400|401|403|404|408|429|500|502|503|504)(?!\d)", str(exc))
        status = int(match.group(1)) if match else None
    labels = {
        400: "Invalid request or model configuration (HTTP 400)",
        401: "Authentication rejected (HTTP 401)",
        403: "Project permission or API access denied (HTTP 403)",
        404: "Model not found or unavailable (HTTP 404)",
        408: "Provider request timed out (HTTP 408)",
        429: "Quota or rate limit reached (HTTP 429)",
        500: "Provider internal error (HTTP 500)",
        502: "Provider gateway error (HTTP 502)",
        503: "Provider temporarily unavailable (HTTP 503)",
        504: "Provider timeout (HTTP 504)",
    }
    return labels.get(status, "Provider request failed (" + type(exc).__name__ + ")")


def check_gemini_connection(api_key, model):
    """Make one short test call, returning a safe, structured result."""
    if not api_key:
        return False, "GEMINI_API_KEY is not configured."
    if not model or not re.fullmatch(r"[a-zA-Z0-9_.-]{2,100}", model):
        return False, "Invalid Gemini model identifier format."
    try:
        from google import genai
        from google.genai import types
        with genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=15000)) as client:
            response = client.models.generate_content(
                model=model,
                contents="Reply with the single word READY.",
                config=types.GenerateContentConfig(max_output_tokens=16, temperature=0),
            )
        if response.text and response.text.strip():
            return True, "Gemini API request succeeded; model returned a response."
        return False, "Request succeeded but returned no text."
    except Exception as exc:
        return False, classify_error(exc)
