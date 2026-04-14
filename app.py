import datetime as dt

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Digital Agora (MVP)",
    page_icon="🗳️",
    layout="centered",
)

st.title("Digital Agora - Minimal Works Version")
st.caption("Quick MVP to validate Streamlit Cloud + Google Sheets connection.")


def get_connection():
    """Try to initialize a gsheets connection; return None if unavailable."""
    try:
        from streamlit_gsheets import GSheetsConnection  # type: ignore
    except Exception:
        try:
            from st_gsheets_connection import GSheetsConnection  # type: ignore
        except Exception:
            return None

    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None


def load_entries(conn) -> pd.DataFrame:
    if conn is None:
        return pd.DataFrame()
    try:
        data = conn.read(worksheet="responses", ttl=0)
        if data is None:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()


def append_entry(conn, definition: str, threat_level: int):
    timestamp = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    row = pd.DataFrame(
        [
            {
                "timestamp_utc": timestamp,
                "democracy_definition": definition.strip(),
                "threat_level": int(threat_level),
            }
        ]
    )

    if conn is None:
        return False, "No Google Sheets connection available."

    try:
        existing = load_entries(conn)
        combined = pd.concat([existing, row], ignore_index=True)
        conn.update(worksheet="responses", data=combined)
        return True, "Saved to Google Sheet."
    except Exception as exc:
        return False, f"Save failed: {exc}"


conn = get_connection()
if conn is None:
    st.warning(
        "Google Sheets connection is not configured yet. "
        "The app still runs, but data cannot be saved."
    )
else:
    st.success("Google Sheets connection available.")

st.subheader("Quick test submission")
definition = st.text_area(
    "In one sentence, what is democracy to you?",
    placeholder="Example: Democracy is shared power with accountability.",
    max_chars=500,
)
threat = st.slider(
    "How much does behavioral extraction threaten your freedom?",
    min_value=0,
    max_value=100,
    value=50,
)

if st.button("Submit test response", type="primary"):
    if not definition.strip():
        st.error("Please write a short definition first.")
    else:
        ok, message = append_entry(conn, definition, threat)
        if ok:
            st.success(message)
        else:
            st.error(message)

st.divider()
st.subheader("Smoke test: latest rows")
entries = load_entries(conn)
if entries.empty:
    st.info("No rows found yet (or connection not configured).")
else:
    st.dataframe(entries.tail(10), use_container_width=True)
