import datetime as dt
import json
import re
from collections import Counter
from io import BytesIO

import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud

st.set_page_config(page_title="Digital Agora", page_icon="🗳️", layout="centered")

ZUBOFF_QUOTES = [
    (
        "Surveillance capitalism claims private human experience as free raw "
        "material for translation into behavioral data."
    ),
    (
        "An epistemic coup concentrates rights to know, rights to decide, and "
        "rights to the future in the hands of private power."
    ),
    (
        "Instrumentarian power works by shaping behavior at scale, often "
        "without our awareness."
    ),
]

DEFAULT_CORPUS = [
    "participation",
    "rights",
    "accountability",
    "pluralism",
    "voice",
    "dignity",
    "justice",
    "equality",
    "representation",
    "freedom",
]


def init_state():
    defaults = {
        "page": "Page 1 - Defining Democracy",
        "definition": "",
        "threat_level": 50,
        "threat_note": "",
        "wishlist": "",
        "final_note": "",
        "submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clean_text_for_cloud(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    stopwords = {
        "the",
        "and",
        "that",
        "this",
        "with",
        "for",
        "are",
        "was",
        "you",
        "your",
        "have",
        "from",
        "they",
        "their",
        "about",
        "into",
        "can",
        "not",
        "but",
        "our",
        "who",
        "how",
        "what",
        "when",
        "where",
        "why",
        "democracy",
    }
    tokens = [token for token in cleaned.split() if len(token) > 2 and token not in stopwords]
    return " ".join(tokens)


def render_word_cloud(text: str):
    source_text = clean_text_for_cloud(text)
    if not source_text.strip():
        source_text = " ".join(DEFAULT_CORPUS)
    wc = WordCloud(width=900, height=400, background_color="white", colormap="viridis")
    image = wc.generate(source_text)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(image, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)


def rating_label(score: int) -> str:
    if score <= 20:
        return "Low"
    if score <= 40:
        return "Mild"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "High"
    return "Critical"


def build_summary() -> str:
    timestamp = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return (
        "Digital Agora - Participant Response\n"
        f"Timestamp (UTC): {timestamp}\n\n"
        "1) Defining Democracy\n"
        f"{st.session_state.definition.strip()}\n\n"
        "2) Perceived Threat (Behavioral Extraction)\n"
        f"Score (0-100): {st.session_state.threat_level}\n"
        f"Intensity label: {rating_label(st.session_state.threat_level)}\n"
        f"Comment: {st.session_state.threat_note.strip() or 'N/A'}\n\n"
        "3) Democratic Wishlist\n"
        f"{st.session_state.wishlist.strip()}\n\n"
        "Optional closing note\n"
        f"{st.session_state.final_note.strip() or 'N/A'}\n"
    )


def summary_download_bytes(summary_text: str) -> bytes:
    buffer = BytesIO()
    buffer.write(summary_text.encode("utf-8"))
    return buffer.getvalue()


def render_page_1():
    st.header("Page 1 - Defining Democracy")
    st.caption("Write your personal definition before seeing collective keywords.")
    st.session_state.definition = st.text_area(
        "What is democracy to you?",
        value=st.session_state.definition,
        placeholder="Example: Democracy is collective self-government with rights, participation, and accountability.",
        max_chars=800,
        height=170,
    )

    if st.session_state.definition.strip():
        st.success("Definition saved in your local session.")
        st.markdown("**Reflection cloud (generated from your text + neutral civic terms):**")
        render_word_cloud(st.session_state.definition)
    else:
        st.info("Write a definition to unlock the reflection cloud.")


def render_page_2():
    st.header("Page 2 - The Death Match")
    st.caption("Inspired by Zuboff (2022): surveillance capitalism and epistemic power.")
    for quote in ZUBOFF_QUOTES:
        st.markdown(f"> {quote}")

    st.session_state.threat_level = st.slider(
        "How much does behavioral extraction threaten your personal freedom?",
        min_value=0,
        max_value=100,
        value=int(st.session_state.threat_level),
    )
    st.session_state.threat_note = st.text_area(
        "Optional: why did you choose this score?",
        value=st.session_state.threat_note,
        placeholder="A short reason in 1-3 sentences.",
        max_chars=500,
        height=120,
    )

    st.metric("Current threat intensity", rating_label(st.session_state.threat_level))
    fig = px.bar(
        x=["Your score"],
        y=[st.session_state.threat_level],
        range_y=[0, 100],
        labels={"x": "", "y": "Threat score"},
        title="Perceived threat score",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_page_3():
    st.header("Page 3 - The Vision")
    st.caption("Write one concrete improvement for a stronger democratic society.")
    st.session_state.wishlist = st.text_area(
        "Your Democratic Wishlist idea",
        value=st.session_state.wishlist,
        placeholder="Example: Make algorithmic systems in public services fully auditable by citizens.",
        max_chars=900,
        height=170,
    )
    st.session_state.final_note = st.text_area(
        "Optional final note",
        value=st.session_state.final_note,
        placeholder="Any final thought about democracy and digital power.",
        max_chars=400,
        height=100,
    )

    st.markdown("**Bulletin preview (session-only):**")
    items = []
    if st.session_state.wishlist.strip():
        items.append(st.session_state.wishlist.strip())
    if st.session_state.final_note.strip():
        items.append(st.session_state.final_note.strip())
    if not items:
        st.info("No ideas added yet.")
    else:
        for idx, idea in enumerate(items, start=1):
            st.markdown(f"- **Idea {idx}:** {idea}")


def render_submit_panel():
    st.divider()
    st.subheader("Final Step - Share your response")
    valid = (
        bool(st.session_state.definition.strip())
        and bool(st.session_state.wishlist.strip())
        and isinstance(st.session_state.threat_level, int)
    )
    if not valid:
        st.warning("Please complete Page 1 and Page 3 before finalizing.")
        return

    summary_text = build_summary()
    st.text_area("Generated response summary", value=summary_text, height=260)

    st.download_button(
        "Download summary (.txt)",
        data=summary_download_bytes(summary_text),
        file_name="digital_agora_response.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.code(
        "mailto:YOUR_EMAIL@example.com?subject=Digital%20Agora%20Response",
        language="text",
    )
    st.caption(
        "Replace YOUR_EMAIL@example.com with your address and ask participants "
        "to paste the summary into an email."
    )

    if st.button("Mark as submitted", type="primary"):
        st.session_state.submitted = True
        st.success("Thank you. Your response is ready to be shared by email.")

    if st.session_state.submitted:
        payload = {
            "definition": st.session_state.definition,
            "threat_level": st.session_state.threat_level,
            "threat_note": st.session_state.threat_note,
            "wishlist": st.session_state.wishlist,
            "final_note": st.session_state.final_note,
        }
        st.markdown("**Structured JSON copy (optional):**")
        st.code(json.dumps(payload, indent=2), language="json")


init_state()

st.title("Digital Agora")
st.caption("A 3-stage interactive journey on democracy, digital power, and civic imagination.")

progress_lookup = {
    "Page 1 - Defining Democracy": 1,
    "Page 2 - The Death Match": 2,
    "Page 3 - The Vision": 3,
}

st.session_state.page = st.sidebar.radio(
    "Navigate",
    list(progress_lookup.keys()),
    index=list(progress_lookup.keys()).index(st.session_state.page),
)
st.sidebar.progress(progress_lookup[st.session_state.page] / 3)
st.sidebar.caption(f"Step {progress_lookup[st.session_state.page]} of 3")

if st.session_state.page == "Page 1 - Defining Democracy":
    render_page_1()
elif st.session_state.page == "Page 2 - The Death Match":
    render_page_2()
else:
    render_page_3()

render_submit_panel()
