
import streamlit as st
from google import genai
from google.genai import types
from ai_engine import ask_gemini, get_api_key


TRAINING_OPTIONS = {
    "Spoken English": "Fluency, pronunciation, clarity, and natural phrasing.",
    "Grammar": "Grammar, sentence construction, and correct English usage.",
    "Vocabulary": "Word choice, vocabulary range, and natural expressions.",
    "Articulation": "Logical structure, concise expression, and clear communication.",
    "Group Discussion": "Arguments, examples, and professional communication.",
    "Interview English": "Interview answers, structure, relevance, and clarity.",
}


def analyse_recording(audio_bytes, mime_type, skill, exercise):
    """Analyse the original audio and generate a detailed speaking report."""
    client = genai.Client(api_key=get_api_key())

    prompt = f"""
You are a professional and supportive English-speaking coach.

PRACTICE SKILL: {skill}

EXERCISE:
{exercise}

Analyse the original audio recording directly. Do not rely only on
a transcript when evaluating features that can be heard in the audio.

First transcribe the learner's response accurately. Then produce
a detailed English assessment.

SCORING RUBRIC — TOTAL 100:
1. Grammar and sentence construction: 15 points
2. Vocabulary and natural phrasing: 15 points
3. Fluency and pace: 20 points
4. Pronunciation and intelligibility: 20 points
5. Articulation and structure: 15 points
6. Relevance and completeness: 15 points

The six scores must add up to exactly 100 maximum points.
Award a score for each category and ensure the total matches.

ASSESSMENT RULES:
- Use the audio for pronunciation and pace observations when possible.
- Do not penalise a learner merely for having an Indian or regional accent.
- Focus on intelligibility and specific sounds, not accent conformity.
- Do not invent pronunciation errors or speaking habits.
- If audio quality or duration limits an assessment, state that limitation.
- Treat all scores as approximate coaching estimates, not certified results.

REPORT FORMAT:

# 1. Overall Score
Give the score out of 100 and explain it briefly.

# 2. Scorecard
Show each category, score earned, maximum points, and reason.

# 3. Transcript
Write the words heard. Mark uncertain words clearly.

# 4. Pronunciation and Clarity
Identify specific words that may need practice, explain the issue,
and give a practical correction where evidence supports it.

# 5. Fluency and Pace
Discuss pace, pauses, hesitation, and continuity when observable.

# 6. Grammar Corrections
Quote original phrases, correct them, and explain the corrections.

# 7. Vocabulary
Suggest more natural expressions where useful.

# 8. Articulation and Structure
Evaluate the opening, logical flow, examples, and conclusion.

# 9. Strengths
List the strongest aspects of the response.

# 10. Three Priority Improvements
Give three specific and achievable improvements.

# 11. Improved Example
Provide a natural example preserving the learner's meaning.
Do not invent personal experiences.

# 12. Ten-Minute Improvement Drill
Create a drill targeting the most important weakness.

Be honest, specific, constructive, and supportive.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            prompt,
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type or "audio/wav",
            ),
        ],
    )

    return (response.text or "").strip()


def review_written_answer(skill, exercise, answer):
    """Review a written answer without making unsupported audio claims."""
    prompt = f"""
You are a supportive English coach.

Skill: {skill}
Exercise: {exercise}
Learner's written answer:
{answer}

Evaluate the written answer with this rubric:
1. Grammar and sentence construction: 15
2. Vocabulary and natural phrasing: 15
3. Fluency of expression in writing: 20
4. Pronunciation and intelligibility: not assessable from text
5. Articulation and structure: 15
6. Relevance and completeness: 15

Provide a score out of 60 for the assessable writing categories.
Do not invent a pronunciation score or claim to measure speaking pace.
Explain that the full speaking score out of 100 requires an audio recording.

Include:
1. Scorecard with earned points and reasons
2. Strengths
3. Original phrases, corrected versions, and simple explanations
4. Vocabulary improvements
5. Clarity and structure feedback
6. A better example response preserving the learner's meaning
7. Three improvement priorities
8. A short exercise for tomorrow

Be specific, honest, and encouraging. Do not invent personal experiences.
"""
    return ask_gemini(prompt)


def render_english_coach():
    st.header("English Improvement Coach")
    st.write(
        "Practise speaking or writing, receive a detailed report, "
        "and work on your next improvement goal."
    )

    skill = st.selectbox(
        "What do you want to train today?",
        list(TRAINING_OPTIONS.keys()),
        key="english_coach_skill_selector",
    )

    duration = st.selectbox(
        "Practice duration",
        ["5 minutes", "10 minutes", "15 minutes"],
        index=1,
        key="english_coach_duration",
    )

    st.info(f"Today's focus: {TRAINING_OPTIONS[skill]}")

    if st.button(
        "Generate today's exercise",
        key="generate_english_exercise",
        type="primary",
    ):
        prompt = f"""
You are a supportive English coach for an MBA student.

Skill: {skill}
Duration: {duration}
Goal: {TRAINING_OPTIONS[skill]}

Create one practical exercise achievable in the selected time.
Use simple English and include:
1. Today's goal
2. One exact question or task
3. Numbered instructions
4. Success criteria

Do not provide a sample answer before the learner tries.
"""
        try:
            with st.spinner("Preparing your exercise..."):
                exercise = ask_gemini(prompt)

            st.session_state["english_coach_active_skill"] = skill
            st.session_state["english_coach_exercise"] = exercise
            st.session_state["english_coach_audio_report"] = None
            st.session_state["english_coach_written_report"] = None

        except Exception as error:
            st.error("Could not generate the exercise.")
            st.caption(str(error))

    exercise = st.session_state.get("english_coach_exercise")

    if not exercise:
        return

    active_skill = st.session_state.get(
        "english_coach_active_skill", skill
    )

    st.divider()
    st.subheader("Today's Exercise")
    st.markdown(exercise)

    st.divider()
    st.subheader("Practise Your Answer")

    method = st.radio(
        "Choose your practice method",
        ["Record my voice", "Type my answer"],
        horizontal=True,
        key="english_coach_response_method",
    )

    if method == "Record my voice":
        st.write(
            "Record your answer, listen to it, and request your "
            "speaking assessment when you are ready."
        )

        audio = st.audio_input(
            "Record your spoken answer",
            sample_rate=16000,
            key="english_coach_audio",
        )

        if audio is not None:
            st.write("**Your recording**")
            st.audio(audio)

            if st.button(
                "Analyse my recording and generate report",
                key="english_coach_analyse_audio",
                type="primary",
            ):
                try:
                    with st.spinner(
                        "Analysing your recording and preparing your report..."
                    ):
                        report = analyse_recording(
                            audio.getvalue(),
                            getattr(audio, "type", None) or "audio/wav",
                            active_skill,
                            exercise,
                        )

                    if report:
                        st.session_state[
                            "english_coach_audio_report"
                        ] = report
                    else:
                        st.warning("The AI returned an empty report.")

                except Exception as error:
                    st.error("Could not analyse your recording.")
                    st.caption(f"Technical details: {error}")

        report = st.session_state.get("english_coach_audio_report")

        if report:
            st.divider()
            st.subheader("Your Speaking Assessment")
            st.markdown(report)

            st.download_button(
                "Download my speaking report",
                data=report,
                file_name="english_speaking_report.md",
                mime="text/markdown",
                key="download_english_audio_report",
            )

    else:
        answer = st.text_area(
            "Write your answer in English",
            height=180,
            key="english_coach_typed_response",
            placeholder="Write your response here...",
        )

        if st.button(
            "Review my written English",
            key="english_coach_review_typed",
            type="primary",
        ):
            if not answer.strip():
                st.warning("Please enter your response first.")
            else:
                try:
                    with st.spinner("Preparing your feedback report..."):
                        report = review_written_answer(
                            active_skill,
                            exercise,
                            answer.strip(),
                        )

                    st.session_state[
                        "english_coach_written_report"
                    ] = report

                except Exception as error:
                    st.error("Could not review your written answer.")
                    st.caption(f"Technical details: {error}")

        written_report = st.session_state.get(
            "english_coach_written_report"
        )

        if written_report:
            st.divider()
            st.subheader("Your Written-English Report")
            st.markdown(written_report)

            st.download_button(
                "Download my written-English report",
                data=written_report,
                file_name="english_written_report.md",
                mime="text/markdown",
                key="download_english_written_report",
            )

    st.caption(
        "Scores are AI-generated learning estimates. Audio quality, "
        "recording length, and model limitations may affect results."
    )
 