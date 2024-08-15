import streamlit as st
from .database import Database
from .config import settings

def init() -> None:
    """Initializing the Streamlit application"""

    # Main page configuration
    st.set_page_config(
        page_title="Enkätanalys", 
        page_icon="https://sb-web-ecommerce-cms.azureedge.net/4a51ce/globalassets/logo.svg?q=75&w=2000",
        layout="wide",
    )
    
    # Setting up the states
    set_up_states()

    # Show survey selector as a modal dialog if no survey is selected
    if not st.session_state.get("survey_selected", False):
        survey_selector_dialog()  
    else:
        # When a survey is selected, set up the pages
        set_up_pages()

def set_up_pages() -> None:
    """Setting up the pages"""
    
    # --- NAVIGATION ---
    survey_overview = st.Page("./pages/survey_overview.py", title="Enkätöversikt", icon=":material/poll:")
    themes = st.Page("./pages/themes.py", title="Teman", icon=":material/layers:")
    comparison = st.Page("./pages/comparison.py", title="Jämförelse & Djupdykning", icon=":material/compare:")
    hypothesis_test = st.Page("./pages/hypothesis_test.py", title="Hypotestestning", icon=":material/science:")
    responses = st.Page("./pages/responses.py", title="Bläddra bland svaren", icon=":material/question_answer:")

    # --- PAGE ARRANGEMENT ---
    st.session_state["pages"] = st.navigation(
        {
            "Alternativ": [
                survey_overview, themes, comparison, hypothesis_test, responses
            ]
        }
    )
    # Initialize the pages
    st.session_state["pages"].run()

def set_up_states() -> None:
    """Setting up the initial states and loading general values to relevant states"""
    
    init_session_states = ["init", "db", "data", "survey_selected"]

    # --- INITIALIZE SESSION STATES ---
    for state in init_session_states:
        if state not in st.session_state:
            st.session_state[state] = False  

    if not st.session_state["init"]:
        st.session_state["db"] = Database(settings)
        st.session_state["init"] = True

def load_survey_data(survey_name) -> None:
    """Loading survey data"""
    with st.spinner("Loading data.."):
        db = st.session_state["db"]
        data = db.fetch_answers_with_questions()
        st.session_state["data"] = data
        st.session_state["survey_selected"] = True
        st.rerun()

@st.dialog("Välj enkät", width="small")
def survey_selector_dialog() -> None:
    """Modal dialog for selecting a survey."""
    survey_name = st.selectbox("Välj enkät", ["systembolaget-surveys", "other-surveys"])
    if st.button("Ladda enkätdata", key="load-survey-modal"):
        load_survey_data(survey_name)

def survey_selector():
    """Regular selector for a survey."""
    survey_name = st.selectbox("Byt enkät", ["systembolaget-surveys", "systembolaget-surveys"])
    if st.button("Ladda enkätdata", key="load-survey-sidebar"):
        load_survey_data(survey_name)
