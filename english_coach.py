
import streamlit as st
from ai_engine import ask_gemini

TRAINING_OPTIONS = {
    "Spoken English": (
        "Improve fluency, natural phrasing, clarity, and confidence "
        "in everyday English conversation."
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


def render_english_coach():
    st.header("English Improvement Coach")
    st.write(
        "Choose a skill, complete a short exercise, "
        "and get feedback to improve your English."
    )

    skill = st.selectbox(
        "What do you want to train today?",
        list(TRAINING_OPTIONS.keys()),
    )

    duration = st.selectbox(
        "Practice duration",
        ["5 minutes", "10 minutes", "15 minutes"],
        index=1,
    )

    st.info(f"Today's focus: {TRAINING_OPTIONS[skill]}")

    if st.button("Generate today's exercise"):
        prompt = f"""
You are a supportive English coach for an MBA student.

Training skill: {skill}
Available practice time: {duration}
Training goal: {TRAINING_OPTIONS[skill]}

Create ONE practical English exercise suitable for this learner.

Requirements:
1. Use simple, clear English.
2. Give the exact task or question the learner must answer.
3. Explain how to complete it in numbered steps.
4. Make it realistic for college, interviews, presentations,
   group discussions, or everyday communication as appropriate.
5. Keep the exercise achievable in the chosen time.
6. Do not provide the sample answer before the learner tries.
7. Encourage the learner without exaggerated praise.

Format:
Today's goal
Exercise
Instructions
Success criteria
"""
        try:
            with st.spinner("Preparing your exercise..."):
                exercise = ask_gemini(prompt)

            st.session_state["english_coach_skill"] = skill
            st.session_state["english_coach_exercise"] = exercise
            st.session_state["english_coach_answer"] = ""
            st.session_state["english_coach_feedback"] = None

        except Exception as error:
            st.error("Could not generate the exercise.")
            st.caption(str(error))

    exercise = st.session_state.get("english_coach_exercise")

    if exercise:
        st.subheader("Today's exercise")
        st.markdown(exercise)

        answer = st.text_area(
            "Write your response here",
            key="english_coach_answer",
            height=180,
            placeholder="Type your answer in English...",
        )

        if st.button("Review my English"):
            if not answer.strip():
                st.warning("Please enter your response first.")
            else:
                review_prompt = f"""
You are a constructive English language coach.

Skill being practised: {st.session_state.get("english_coach_skill")}
Exercise: {exercise}

Learner's response:
{answer}

Review the response using these sections:

1. What you did well
2. Grammar and sentence corrections
   - Quote the original phrase.
   - Give a corrected version.
   - Explain why in simple English.
3. Vocabulary and natural phrasing
4. Clarity and structure
5. A better version of the response
6. One specific improvement goal for next time
7. Practice exercise for tomorrow

Give an overall English score out of 10, considering the
selected skill. Be fair and specific. Do not invent pronunciation
problems from text alone. Do not claim to assess speaking speed
or accent from a typed response.
"""
                try:
                    with st.spinner("Reviewing your response..."):
                        feedback = ask_gemini(review_prompt)

                    st.session_state["english_coach_feedback"] = feedback

                except Exception as error:
                    st.error("Could not review your response.")
                    st.caption(str(error))

        feedback = st.session_state.get("english_coach_feedback")

        if feedback:
            st.subheader("Your feedback")
            st.markdown(feedback)
