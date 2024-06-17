import streamlit as st

# homepage
st.title("Welcome to CineTrip!")
if st.button("Next"):
    st.switch_page("pages\step1.py")


