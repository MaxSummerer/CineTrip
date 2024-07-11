import streamlit as st
import requests
from src.scripts.gpt_questionare import create_questionnaire

# only parts inside experimental_fragment will rerun
@st.experimental_fragment
def create_quiz(response):
    index = 0
    score = {}
    for question in response['questions']:
        with (st.container()):
            quiz = st.radio(f"Question {index}: {question['question']}",
                            [f"A {question['options']['a']}",
                             f"B {question['options']['b']}",
                             f"C {question['options']['c']}",
                             f"D {question['options']['d']}"],
                            index=None)

            if quiz is not None:
                if quiz[0].lower() == question['correct_answer']:
                    st.markdown(':rainbow[Correct!]')
                    score[index] = 1
                else:
                    st.markdown('Wrong:)')
            index = index + 1
    if st.button("Check your score"):
        total_score = sum(score.values())
        st.markdown(f"{total_score} / 8")
    if st.button("Go back"):
        st.switch_page("pages/step3.py")


if st.session_state['country'] and st.session_state['city'] and st.session_state['city'] != "":
    with st.spinner('Wait for generating quiz...'):
        response = create_questionnaire(st.session_state['city'])

    st.title(f"Quiz time! How much do you know about {st.session_state['city']}?")
    create_quiz(response)
