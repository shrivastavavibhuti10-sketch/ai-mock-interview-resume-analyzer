import streamlit as st
import os
import sqlite3
import pandas as pd
import plotly.express as px

from modules.resume_parser import extract_text
from modules.ai_resume_analyzer import analyze_resume_ai
from modules.jd_matcher import match_resume_with_jd_ai
from modules.question_generator import generate_questions
from modules.interview_manager import get_questions
from modules.answer_evaluator import evaluate_answer
from modules.pdf_generator import generate_pdf , generate_coding_pdf
from modules.speech_to_text import speech_to_text

from streamlit_mic_recorder import mic_recorder
from modules.coding_interview import (
    generate_coding_question,
    evaluate_code
)

from database import (
    register_user,
    login_user,
    save_interview,
    get_interviews
)

from modules.theme import load_theme
from modules.ui import hero, glass_card, feature_card

# ======================================================
# Page Configuration
# ======================================================

st.set_page_config(
    page_title="AI Mock Interview & Resume Analyzer",
    page_icon="🤖",
    layout="wide"
)

# ======================================================
# Load Theme
# ======================================================

load_theme()

# ======================================================
# Session State
# ======================================================

default_states = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "resume_text": "",
    "jd_text": "",
    "questions": [],
    "answers": [],
    "scores": [],
    "feedbacks": [],
    "current": 0
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ======================================================
# Application Title
# ======================================================

st.title("🤖 AI Mock Interview & Resume Analyzer")
st.markdown("---")
# ======================================================
# Sidebar Navigation
# ======================================================

if st.session_state["logged_in"]:

    st.sidebar.success(
        f"Welcome, {st.session_state['user_name']} 👋"
    )

    page = st.sidebar.radio(

        "Navigation",

        [

            "🏠 Dashboard",

            "📄 Resume Analyzer",

            "🎤 Mock Interview",

            "📊 Analytics",

            "👤 Profile",

            "💻 Coding Interview"

        ]

    )

else:

    page = st.sidebar.radio(

        "Navigation",

        [

            "🔑 Login",

            "📝 Register"

        ]

    )

# ======================================================
# Register
# ======================================================

if page == "📝 Register":

    st.title("📝 Create Account")

    name = st.text_input("Full Name")

    email = st.text_input("Email")

    password = st.text_input(

        "Password",

        type="password"

    )

    if st.button(

        "Register",

        use_container_width=True

    ):

        if (

            name == ""

            or email == ""

            or password == ""

        ):

            st.warning(

                "Please fill all fields."

            )

        else:

            success = register_user(

                name,

                email,

                password

            )

            if success:

                st.success(

                    "Registration Successful!"

                )

            else:

                st.error(

                    "Email already exists."

                )

# ======================================================
# Login
# ======================================================

if page == "🔑 Login":

    st.title("🔑 Login")

    email = st.text_input(

        "Email"

    )

    password = st.text_input(

        "Password",

        type="password"

    )

    if st.button(

        "Login",

        use_container_width=True

    ):

        user = login_user(

            email,

            password

        )

        if user:

            st.session_state["logged_in"] = True

            st.session_state["user_id"] = user[0]

            st.session_state["user_name"] = user[1]

            st.success(

                "Login Successful!"

            )

            st.rerun()

        else:

            st.error(

                "Invalid Email or Password."

            )
            # ======================================================
# Dashboard
# ======================================================

if page == "🏠 Dashboard":

    hero(
       "🤖 AI Mock Interview Platform",
       "Your Personal AI Career Coach"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
       glass_card(
        "Resume Score",
        "92%",
        "📄"
    )

    with col2:
       glass_card(
        "Interviews",
        "18",
        "🎤"
    )


    with col3:
       glass_card(
         "ATS Score",
         "88%",
         "🚀"
        )

    st.markdown("---")

    st.subheader("🚀 Welcome")

    st.write(
        f"Hello *{st.session_state['user_name']}*, welcome to your AI Interview Assistant."
    )

    st.markdown("---")


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📄 Resume",
            "Ready"
            if st.session_state["resume_text"]
            else "Not Uploaded"
        )

    with col2:

        st.metric(
            "📋 Job Description",
            "Ready"
            if st.session_state["jd_text"]
            else "Not Uploaded"
        )

    with col3:

        st.metric(
            "🎤 Questions",
            len(st.session_state["questions"])
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        feature_card(
            "Resume Analyzer",
            [
            "AI Resume Analysis",
            "ATS Score",
            "Resume vs JD Match",
            "Missing Skills",
            "Resume Improvement"
            ],
        "📄"
        )

    with col2:

        feature_card(
          "AI Mock Interview",
           [
            "AI Generated Questions",
            "Voice Interview",
            "AI Evaluation",
            "Score & Feedback",
            "PDF Report"
           ],
        "🎤"
        )

    st.success(
        "Use the sidebar to access Resume Analyzer, Mock Interview, Analytics and Profile."
    )
# ======================================================
# Login Required
# ======================================================

if (
    not st.session_state["logged_in"]
    and page
    not in
    [
        "🔑 Login",
        "📝 Register"
    ]
):

    st.warning(
        "Please login to continue."
    )

    st.stop()

# ======================================================
# Application Ready
# ======================================================

st.sidebar.markdown("---")

if st.session_state["logged_in"]:

    st.sidebar.success(
        f"👤 {st.session_state['user_name']}"
    )

    st.sidebar.caption(
        "AI Mock Interview & Resume Analyzer"
    )
# ======================================================
# Resume Analyzer
# ======================================================

if page == "📄 Resume Analyzer":

    st.title("📄 AI Resume Analyzer")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        resume_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx"],
            key="resume_upload"
        )

    with col2:

        jd_file = st.file_uploader(
            "Upload Job Description",
            type=["pdf", "docx", "txt"],
            key="jd_upload"
        )

    st.markdown("---")

    if resume_file is not None:

        try:

            st.session_state["resume_text"] = extract_text(
                resume_file
            )

            st.success("✅ Resume Uploaded Successfully")

        except Exception as e:

            st.error(f"Resume Error: {e}")

    if jd_file is not None:

        try:

            st.session_state["jd_text"] = extract_text(
                jd_file
            )

            st.success("✅ Job Description Uploaded Successfully")

        except Exception as e:

            st.error(f"JD Error: {e}")

    st.markdown("---")

    if (
        st.session_state["resume_text"] != ""
        and
        st.session_state["jd_text"] != ""
    ):

        if st.button(
            "🚀 Analyze Resume",
            use_container_width=True
        ):

            with st.spinner(
                "Analyzing Resume..."
            ):

                analysis = analyze_resume_ai(
                    st.session_state["resume_text"]
                )

                ats = match_resume_with_jd_ai(
                    st.session_state["resume_text"],
                    st.session_state["jd_text"]
                )

            st.session_state["analysis"] = analysis

            st.session_state["ats"] = ats

    if "analysis" in st.session_state:

        st.markdown("---")

        st.subheader("🤖 AI Resume Analysis")

        st.write(
            st.session_state["analysis"]
        )

if "ats" in st.session_state:

    st.markdown("---")

    st.subheader("📊 ATS Analysis")

    st.write(
        st.session_state["ats"]
    )
# ======================================================
# Mock Interview
# ======================================================

if page == "🎤 Mock Interview":

    st.title("🎤 AI Mock Interview")

    if st.session_state["resume_text"] == "":

        st.warning(
            "Please upload your Resume first."
        )

        st.stop()

    if st.session_state["jd_text"] == "":

        st.warning(
            "Please upload the Job Description first."
        )

        st.stop()

    if "questions" not in st.session_state:

        st.session_state["questions"] = []

    if "current" not in st.session_state:

        st.session_state["current"] = 0

    if "answers" not in st.session_state:

        st.session_state["answers"] = []

    if "scores" not in st.session_state:

        st.session_state["scores"] = []

    if "feedbacks" not in st.session_state:

        st.session_state["feedbacks"] = []

    st.markdown("---")

    if st.button(

        "🚀 Generate Interview Questions",

        use_container_width=True

    ):

        with st.spinner(

            "Generating AI Interview Questions..."

        ):

            questions = generate_questions(

                st.session_state["resume_text"],

                st.session_state["jd_text"]

            )

            st.session_state["questions"] = get_questions(

                questions

            )

            st.session_state["current"] = 0

            st.session_state["answers"] = []

            st.session_state["scores"] = []

            st.session_state["feedbacks"] = []

        st.success(

            "✅ Interview Questions Generated Successfully"

        )

    if len(st.session_state["questions"]) > 0:

        questions = st.session_state["questions"]

        current = st.session_state["current"]

        if current < len(questions):

            st.markdown("---")

            st.subheader(
                f"Question {current + 1} of {len(questions)}"
            )

            st.write(
                questions[current]
            )

            answer = st.text_area(

                "Your Answer",

                height=200,

                key=f"answer_{current}"

            )

            st.markdown("### 🎙️ Voice Answer")

            audio = mic_recorder(

                start_prompt="🎤 Start Recording",

                stop_prompt="⏹️ Stop Recording",

                key=f"voice_{current}"

            )

            if audio:

                try:

                    voice_text = speech_to_text(

                        audio["bytes"]

                    )

                    st.success(

                        "✅ Voice converted to text"

                    )

                    st.text_area(

                        "Recognized Speech",

                        value=voice_text,

                        height=150,

                        key=f"speech_{current}"

                    )

                    answer = voice_text

                except Exception as e:

                    st.error(

                        f"Speech Recognition Error: {e}"

                    )

            col1, col2 = st.columns(2)
            with col1:

                if st.button(
                    "✅ Evaluate Answer",
                    use_container_width=True
                ):

                    if answer.strip() == "":

                        st.warning(
                            "Please enter or record your answer."
                        )

                    else:

                        with st.spinner(
                            "Evaluating Answer..."
                        ):

                            score, feedback = evaluate_answer(
                                questions[current],
                                answer
                            )

                        if len(st.session_state["answers"]) <= current:

                            st.session_state["answers"].append(answer)
                            st.session_state["scores"].append(score)
                            st.session_state["feedbacks"].append(feedback)

                        else:

                            st.session_state["answers"][current] = answer
                            st.session_state["scores"][current] = score
                            st.session_state["feedbacks"][current] = feedback

                        st.success(
                            f"⭐ Score: {score}/10"
                        )

                        st.info(
                            feedback
                        )

            with col2:

                if st.button(
                    "➡️ Next Question",
                    use_container_width=True
                ):

                    if len(st.session_state["answers"]) <= current:

                        st.warning(
                            "Please evaluate your answer first."
                        )

                    else:

                        st.session_state["current"] += 1

                        st.rerun()

        else:

            st.balloons()

            st.success(
                "🎉 Interview Completed!"
            )

            average = (
                sum(st.session_state["scores"])
                /
                len(st.session_state["scores"])
            )

            st.metric(
                "⭐ Overall Score",
                f"{average:.1f}/10"
            )

            pdf_name = (
                f"Interview_Report_"
                f"{st.session_state['user_name']}.pdf"
            )

            generate_pdf(
                pdf_name,
                st.session_state["user_name"],
                st.session_state["questions"],
                st.session_state["answers"],
                st.session_state["scores"],
                st.session_state["feedbacks"]
            )

            with open(pdf_name, "rb") as pdf:

                st.download_button(
                    "📄 Download Interview Report",
                    pdf,
                    file_name=pdf_name,
                    mime="application/pdf",
                    use_container_width=True
                )
# =====================================================
# Coding Interview
# =====================================================
# 💻 Coding Interview Section

if page == "💻 Coding Interview":

    st.title("💻 AI Coding Interview")

    st.markdown("---")


    # Difficulty and Language

    col1, col2 = st.columns(2)


    with col1:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )


    with col2:

        language = st.selectbox(
            "Programming Language",
            [
                "Python",
                "Java",
                "C++",
                "JavaScript"
            ]
        )


    st.markdown("---")


    # Generate Question Function

    def generate_question():

        with st.spinner(
            "Generating Coding Question..."
        ):

            question = generate_coding_question(
                st.session_state.get("resume_text", ""),
                st.session_state.get("jd_text", ""),
                language,
                difficulty
            )

            st.session_state["coding_question"] = question
            st.session_state["submitted_code"] = ""


    # First Question Button

    if st.button(
        "🚀 Generate Coding Question",
        use_container_width=True
    ):

        generate_question()



    # Display Question

    if "coding_question" in st.session_state:


        st.markdown("---")

        st.subheader(
            "📝 Coding Question"
        )


        st.info(
            st.session_state["coding_question"]
        )


        st.markdown("---")


        # Large Code Editor

        code = st.text_area(

            "💻 Write Your Code",

            value=st.session_state.get(
                "submitted_code",
                ""
            ),

            height=500,

            placeholder=
            "Write your solution here..."

        )


        st.session_state["submitted_code"] = code



        col3, col4 = st.columns(2)


        # Evaluate Code Button

        with col3:

            if st.button(
                "🔍 Evaluate Code",
                use_container_width=True
            ):


                if code.strip() == "":

                    st.warning(
                        "Please write your code first."
                    )


                else:


                    with st.spinner(
                        "Evaluating your solution..."
                    ):


                        evaluation = evaluate_code(

                        st.session_state["coding_question"],

                            code,

                            language

                        )


                    st.markdown("---")

                    st.subheader(
                        "📊 Evaluation Result"
                    )


                    st.write(
                        evaluation
                    )


        # Next Question Button

        with col4:


            if st.button(

                "➡️ Generate Next Question",

                use_container_width=True

            ):

                generate_question()