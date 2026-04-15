import datetime as dt
import json
import urllib.parse
from io import BytesIO

import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Digital Agora", page_icon="🗳️", layout="centered")

TARGET_EMAIL = "leonardo.gonnelli@student.unisg.ch"

QUIZ_OPTIONS = {
    "q1": [
        "I know more about my political preferences",
        "My most-used app knows more",
        "Not sure",
    ],
    "q2": [
        "Mostly me",
        "Mostly platform algorithms",
        "Mostly news organizations",
        "Not sure",
    ],
    "q3": [
        "Yes, I can mostly opt out",
        "Partly, but with difficulty",
        "No, not realistically",
    ],
}

COMMUNITY_RULE_SEEDS = [
    "No behavioral advertising of any kind.",
    "Data minimization by default: collect only what is needed for safety.",
    "Chronological feed with user-controlled ranking options.",
    "Human appeal process for every moderation decision.",
    "Open algorithm audits accessible to citizens.",
]


def init_state():
    defaults = {
        "page": "1) Shadow Text Mirror",
        "confession": "",
        "translation": "",
        "compass_structure": 50,
        "compass_threat": 50,
        "compass_role": 50,
        "quiz_q1": QUIZ_OPTIONS["q1"][0],
        "quiz_q2": QUIZ_OPTIONS["q2"][0],
        "quiz_q3": QUIZ_OPTIONS["q3"][1],
        "sanctuary_rule": "",
        "wall_rules": list(COMMUNITY_RULE_SEEDS),
        "final_note": "",
        "submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def scale_label(value: int, left: str, right: str) -> str:
    if value <= 33:
        return left
    if value >= 67:
        return right
    return "Balanced / Mixed"


def epistemic_score() -> int:
    score = 0
    if st.session_state.quiz_q1 == "My most-used app knows more":
        score += 2
    elif st.session_state.quiz_q1 == "Not sure":
        score += 1

    if st.session_state.quiz_q2 == "Mostly platform algorithms":
        score += 2
    elif st.session_state.quiz_q2 == "Not sure":
        score += 1

    if st.session_state.quiz_q3 == "No, not realistically":
        score += 2
    elif st.session_state.quiz_q3 == "Partly, but with difficulty":
        score += 1

    return score


def epistemic_interpretation(score: int) -> str:
    if score <= 1:
        return "Low concern: you still perceive strong personal epistemic agency."
    if score <= 3:
        return "Moderate concern: control is partly shared with platform systems."
    return "High concern: your answers align with Zuboff's 'epistemic inequality' thesis."


def build_summary() -> str:
    timestamp = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    score = epistemic_score()
    return (
        "Digital Agora - Participant Response\n"
        f"Timestamp (UTC): {timestamp}\n\n"
        "1) Shadow Text Mirror\n"
        f"Confession: {st.session_state.confession.strip() or 'N/A'}\n"
        f"Translation: {st.session_state.translation.strip() or 'N/A'}\n\n"
        "2) Democracy Compass\n"
        f"Democracy is (Structure<->Feeling): {st.session_state.compass_structure}/100 "
        f"({scale_label(st.session_state.compass_structure, 'Structure', 'Feeling')})\n"
        f"Biggest threat (State<->Market): {st.session_state.compass_threat}/100 "
        f"({scale_label(st.session_state.compass_threat, 'State', 'Market')})\n"
        f"My role (Observer<->Actor): {st.session_state.compass_role}/100 "
        f"({scale_label(st.session_state.compass_role, 'Observer', 'Actor')})\n\n"
        "3) Epistemic Inequality Quiz\n"
        f"Q1: {st.session_state.quiz_q1}\n"
        f"Q2: {st.session_state.quiz_q2}\n"
        f"Q3: {st.session_state.quiz_q3}\n"
        f"Epistemic concern score: {score}/6\n"
        f"Interpretation: {epistemic_interpretation(score)}\n\n"
        "4) Sanctuary Wishlist\n"
        f"My must-have rule: {st.session_state.sanctuary_rule.strip() or 'N/A'}\n"
        f"Final note: {st.session_state.final_note.strip() or 'N/A'}\n"
    )


def summary_download_bytes(summary_text: str) -> bytes:
    buffer = BytesIO()
    buffer.write(summary_text.encode("utf-8"))
    return buffer.getvalue()


def render_shadow_text():
    st.header("1) The Shadow Text Mirror")
    st.caption("Focus: Zuboff's idea of hidden behavioral data ('shadow text').")
    st.markdown(
        "**Prompt:** What is one thing you did today that an algorithm knows, "
        "but your neighbor doesn't?"
    )

    st.session_state.confession = st.text_area(
        "Digital confession",
        value=st.session_state.confession,
        max_chars=300,
        height=120,
        placeholder="Example: I paused for 8 seconds on a political reel.",
    )

    if st.button("Translate to Surveillance Capital"):
        if not st.session_state.confession.strip():
            st.warning("Write one confession first.")
        else:
            st.session_state.translation = (
                "Translation: This personal moment has been converted into "
                "behavioral data and a prediction product for profit."
            )

    if st.session_state.translation:
        st.error(st.session_state.translation)


def render_compass():
    st.header("2) The Democracy Compass")
    st.caption(
        "Focus: Kegan's subject-object shift. Can you see the lens through which "
        "you interpret democracy?"
    )
    st.session_state.compass_structure = st.slider(
        "Democracy is: Structure <-> Feeling",
        0,
        100,
        int(st.session_state.compass_structure),
    )
    st.session_state.compass_threat = st.slider(
        "Biggest threat is: State <-> Market",
        0,
        100,
        int(st.session_state.compass_threat),
    )
    st.session_state.compass_role = st.slider(
        "My role is: Observer <-> Actor",
        0,
        100,
        int(st.session_state.compass_role),
    )

    labels = [
        scale_label(st.session_state.compass_structure, "Structure", "Feeling"),
        scale_label(st.session_state.compass_threat, "State", "Market"),
        scale_label(st.session_state.compass_role, "Observer", "Actor"),
    ]
    fig = px.bar(
        x=["Democracy lens", "Threat lens", "Role lens"],
        y=[
            st.session_state.compass_structure,
            st.session_state.compass_threat,
            st.session_state.compass_role,
        ],
        text=labels,
        range_y=[0, 100],
        labels={"x": "", "y": "Position on scale"},
        title="Your current democratic lens",
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        "Reflection: You are currently looking at democracy through this lens. "
        "Can you step back and observe the lens itself?"
    )


def render_epistemic_quiz():
    st.header("3) Epistemic Inequality Quiz")
    st.caption("Focus: who knows, who decides who knows, and whether opting out is real.")

    st.session_state.quiz_q1 = st.radio(
        "Who knows more about your political preferences?",
        QUIZ_OPTIONS["q1"],
        index=QUIZ_OPTIONS["q1"].index(st.session_state.quiz_q1),
    )
    st.session_state.quiz_q2 = st.radio(
        "Who decides what appears first in your news feed?",
        QUIZ_OPTIONS["q2"],
        index=QUIZ_OPTIONS["q2"].index(st.session_state.quiz_q2),
    )
    st.session_state.quiz_q3 = st.radio(
        "Can you realistically opt out of being known by the digital world today?",
        QUIZ_OPTIONS["q3"],
        index=QUIZ_OPTIONS["q3"].index(st.session_state.quiz_q3),
    )

    score = epistemic_score()
    st.metric("Epistemic concern score", f"{score}/6")
    st.warning(epistemic_interpretation(score))
    st.markdown(
        "> If authority to know shifts away from persons and publics toward private "
        "systems, democracy becomes structurally weaker."
    )


def render_sanctuary():
    st.header("4) Sanctuary Wishlist")
    st.caption("Focus: designing a digital public square immune to surveillance logic.")
    st.session_state.sanctuary_rule = st.text_area(
        "If you could build a digital sanctuary, what ONE rule must it have?",
        value=st.session_state.sanctuary_rule,
        max_chars=240,
        height=110,
        placeholder="Example: No behavioral ads, ever.",
    )
    if st.button("Add my rule to the community wall"):
        rule = st.session_state.sanctuary_rule.strip()
        if not rule:
            st.warning("Write one rule before adding it.")
        elif rule in st.session_state.wall_rules:
            st.info("This rule is already on the wall.")
        else:
            st.session_state.wall_rules.append(rule)
            st.success("Rule added to the wall.")

    st.markdown("### Community Wall")
    for idx, rule in enumerate(st.session_state.wall_rules, start=1):
        st.markdown(f"- **Rule {idx}:** {rule}")

    st.session_state.final_note = st.text_area(
        "Optional final note",
        value=st.session_state.final_note,
        max_chars=400,
        height=90,
    )


def render_submit_panel():
    st.divider()
    st.subheader("Final Step - Send your response")

    required_ready = (
        bool(st.session_state.confession.strip())
        and bool(st.session_state.translation.strip())
        and bool(st.session_state.sanctuary_rule.strip())
    )
    if not required_ready:
        st.warning(
            "Complete the confession + translation and add one sanctuary rule before finalizing."
        )
        return

    summary_text = build_summary()
    st.text_area("Generated response summary", value=summary_text, height=300)

    st.download_button(
        "Download summary (.txt)",
        data=summary_download_bytes(summary_text),
        file_name="digital_agora_response.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown("**Recipient email (copy this):**")
    st.text_input(
        "Email address",
        value=TARGET_EMAIL,
        disabled=True,
        label_visibility="collapsed",
    )

    mailto_link = (
        f"mailto:{TARGET_EMAIL}?subject="
        f"{urllib.parse.quote('Digital Agora Response')}&body="
        f"{urllib.parse.quote(summary_text)}"
    )
    st.link_button("Open email draft", mailto_link, use_container_width=True)

    if st.button("Mark as submitted", type="primary"):
        st.session_state.submitted = True
        st.success("Thank you. Copy/download your summary and send it by email.")

    if st.session_state.submitted:
        payload = {
            "confession": st.session_state.confession,
            "translation": st.session_state.translation,
            "compass_structure": st.session_state.compass_structure,
            "compass_threat": st.session_state.compass_threat,
            "compass_role": st.session_state.compass_role,
            "quiz_q1": st.session_state.quiz_q1,
            "quiz_q2": st.session_state.quiz_q2,
            "quiz_q3": st.session_state.quiz_q3,
            "sanctuary_rule": st.session_state.sanctuary_rule,
            "final_note": st.session_state.final_note,
        }
        st.markdown("**Structured JSON copy (optional):**")
        st.code(json.dumps(payload, indent=2), language="json")


init_state()

st.title("Digital Agora")
st.caption(
    "A reflective civic experience on surveillance capitalism, epistemic power, "
    "and democratic imagination."
)

progress_lookup = {
    "1) Shadow Text Mirror": 1,
    "2) Democracy Compass": 2,
    "3) Epistemic Inequality Quiz": 3,
    "4) Sanctuary Wishlist": 4,
}

st.session_state.page = st.sidebar.radio(
    "Navigate",
    list(progress_lookup.keys()),
    index=list(progress_lookup.keys()).index(st.session_state.page),
)
st.sidebar.progress(progress_lookup[st.session_state.page] / 4)
st.sidebar.caption(f"Step {progress_lookup[st.session_state.page]} of 4")

if st.session_state.page == "1) Shadow Text Mirror":
    render_shadow_text()
elif st.session_state.page == "2) Democracy Compass":
    render_compass()
elif st.session_state.page == "3) Epistemic Inequality Quiz":
    render_epistemic_quiz()
else:
    render_sanctuary()

render_submit_panel()
