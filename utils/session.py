import streamlit as st

def initialise_state():
    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None
