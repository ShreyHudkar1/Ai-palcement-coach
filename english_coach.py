
import streamlit as st
from google import genai
from google.genai import types
from ai_engine import ask_gemini, get_api_key


TRAINING_OPTIONS = {
    "Spoken English": (
        "Improve fluency, natural phrasing, clarity, "
        "and confidence in everyday English conversation."
    ),
    "Grammar": (
        "Identify grammar mistakes, explain corrections simply, "
        "and give a short practice exercise."
    ),
    "Vocabulary": (
        "Teach useful English words and phrases with meanings, "
        "natural examples, and a short usage exercise."
    ),
    "Articulation": (
        "Help the learner organize thoughts, speak concisely, "
        "and express ideas in a clear structure."
    ),
    "Group Discussion": (
        "Practise opening statements, logical arguments, examples, "
        "agreeing or disagreeing politely, and entering a discussion."
    ),
    "Interview English": (
        "Practise professional interview answers using clear "
        "structure, relevant examples, and natural English."
    ),
}


def transcribe_audio(audio_bytes, mime_type="audio/wav"):
    """Convert a recorded answer into text using Gemini."""
    client = genai.Client(api_key=get_api_key())

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            (
                "Transcribe the learner's recording accurately. "
                "Return only the words spoken. Do not correct grammar, "
                "summarise, or add commentary."
            ),
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type or "audio/wav",
            ),
        ],
    )

    return (response.text or "").strip()


def review_response(skill, exercise, answer, response_mode):
    """Review a learner's answer and provide actionable feedback."""
    prompt = f"""
You are a supportive but honest English language coach.

Selected skill: {skill}
Exercise: {exercise}
Response method: {response_mode}

Learner's response:
{answer}

Review the response using these sections:

1. Overall score out of 10
2. What the learner did well
3. Grammar and sentence corrections
   - Quote the original phrase.
   - Give the corrected version.
   - Explain why in simple English.
4. Vocabulary and more natural phrasing
5. Clarity and structure
6. A stronger example response that preserves the learner's meaning
7. One specific improvement goal for the next practice
8. A short exercise for tomorrow

Be specific, practical, and encouraging.
Do not invent pronunciation problems from a transcript.
Do not claim to measure speaking speed, accent, confidence, or
pronunciation from text alone.

For a recorded response, explain that the feedback is based primarily
on the transcription. Do not pretend to have analysed audio features.
"""
    return ask_gemini(prompt)


def render_english_coach():
    st.header("English Improvement Coach")
    st.write(
        "Choose a skill, practise by typing or speaking, "
        "and receive personalised feedback."
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

Training skill: {skill}
Available practice time: {duration}
Training goal: {TRAINING_OPTIONS[skill]}

Create ONE practical exercise.

Requirements:
1. Use simple, clear English.
2. Give the exact task or question the learner must answer.
3. Explain how to complete it in numbered steps.
4. Make it realistic for college, interviews, presentations,
   group discussions, or everyday communication.
5. Keep it achievable in the selected time.
6. Do not provide the sample answer before the learner tries.
7. Encourage the learner without exaggerated praise.

Format:
Today's Goal
Exercise
Instructions
Success Criteria
"""
        try:
            with st.spinner("Preparing your exercise..."):
                exercise = ask_gemini(prompt)

            st.session_state["english_coach_active_skill"] = skill
            st.session_state["english_coach_exercise"] = exercise
            st.session_state["english_coach_feedback"] = None
            st.session_state["english_coach_transcript_edit"] = ""
            st.session_state["english_coach_answer"] = ""

        except Exception as error:
            st.error("Could not generate the exercise.")
            st.caption(str(error))

    exercise = st.session_state.get("english_coach_exercise")

    if not exercise:
        return

    active_skill = st.session_state.get(
        "english_coach_active_skill",
        skill,
    )

    st.divider()
    st.subheader("Today's Exercise")
    st.markdown(exercise)

    st.divider()
    st.subheader("Practise Your Answer")

    response_method = st.radio(
        "How would you like to practise?",
        ["Record my voice", "Type my answer"],
        horizontal=True,
        key="english_coach_response_method",
    )

    if response_method == "Record my voice":
        st.write(
            "Press the microphone button, record your answer, "
            "and finish the recording when you are done."
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
                "Transcribe my recording",
                key="english_coach_transcribe",
                type="primary",
            ):
                try:
                    with st.spinner("Converting your speech into text..."):
                        transcript = transcribe_audio(
                            audio.getvalue(),
                            getattr(audio, "type", None) or "audio/wav",
                        )

                    if transcript:
                        st.session_state[
                            "english_coach_transcript_edit"
                        ] = transcript
                        st.session_state[
                            "english_coach_answer"
                        ] = transcript
                        st.session_state[
                            "english_coach_feedback"
                        ] = None
                        st.success("Recording transcribed successfully.")
                    else:
                        st.warning(
                            "No speech was detected. Please try recording again."
                        )

                except Exception as error:
                    st.error("Could not transcribe your recording.")
                    st.caption(f"Technical details: {error}")

        transcript = st.session_state.get(
            "english_coach_transcript_edit",
            "",
        )

        if transcript:
            st.write("**Review your transcript**")
            st.caption(
                "Correct any transcription mistakes before requesting feedback."
            )

            edited_transcript = st.text_area(
                "Your spoken answer",
                key="english_coach_transcript_edit",
                height=180,
                placeholder="Your transcribed answer will appear here...",
            )

            if st.button(
                "Review my spoken English",
                key="english_coach_review_spoken",
                type="primary",
            ):
                if not edited_transcript.strip():
                    st.warning("Please record or enter an answer first.")
                else:
                    try:
                        with st.spinner("Reviewing your English..."):
                            feedback = review_response(
                                active_skill,
                                exercise,
                                edited_transcript.strip(),
                                "spoken and transcribed",
                            )

                        st.session_state[
                            "english_coach_feedback"
                        ] = feedback
                        st.session_state[
                            "english_coach_answer"
                        ] = edited_transcript.strip()

                    except Exception as error:
                        st.error("Could not review your answer.")
                        st.caption(f"Technical details: {error}")

    else:
        typed_answer = st.text_area(
            "Write your response here",
            key="english_coach_typed_response",
            height=180,
            placeholder="Write your answer in English...",
        )

        if st.button(
            "Review my written English",
            key="english_coach_review_typed",
            type="primary",
        ):
            if not typed_answer.strip():
                st.warning("Please enter your response first.")
            else:
                try:
                    with st.spinner("Reviewing your English..."):
                        feedback = review_response(
                            active_skill,
                            exercise,
                            typed_answer.strip(),
                            "typed",
                        )

                    st.session_state[
                        "english_coach_feedback"
                    ] = feedback
                    st.session_state[
                        "english_coach_answer"
                    ] = typed_answer.strip()

                except Exception as error:
                    st.error("Could not review your answer.")
                    st.caption(f"Technical details: {error}")

    feedback = st.session_state.get("english_coach_feedback")

    if feedback:
        st.divider()
        st.subheader("Your Personalised Feedback")
        st.markdown(feedback)

        st.caption(
            "Note: A score out of 10 is an AI-generated learning estimate, "
            "not a formal language proficiency test."
        )
