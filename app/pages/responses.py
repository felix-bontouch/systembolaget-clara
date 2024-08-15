import streamlit as st
import pandas as pd
from utils.streamlit_config import survey_selector

def get_data_subset(
        data: pd.DataFrame, area: list = None, subject: list = None, question: list = None, search: str = None
        ) -> pd.DataFrame:
    """Filter the data based on the provided criteria."""
    if area:
        data = data[data["QuestionSubjectText"].isin(area)]

    if subject:
        data = data[data["SubjectID"].isin(subject)]

    if question:
        data = data[data["QuestionText"].isin(question)]

    if search:
        data = data[data["StringResponse"].str.contains(search, case=False, na=False)]

    return data.reset_index(drop=True)

def display_data():
    """Main function to display the filtered data on the Streamlit app."""
    st.title("Bläddra bland svaren")
    st.text("Här kan du bläddra bland svaren.")

    # Load and filter the data
    data = st.session_state["data"]
    data = data[(~data["StringResponse"].isna()) & (data["QuestionType"] == "Open text")]  # Filter only open text responses
    data = data[data["StringResponse"].apply(lambda x: len(x.split()) > 4)].reset_index(drop=True)  # Filter out very short comments

    # Layout for filters
    col_1, col_2, col_3, col_4 = st.columns(4)
    with col_1:
        area = st.multiselect("Område", data["QuestionSubjectText"].unique(), default=None)
    with col_2:
        subject = st.multiselect("Ämne", data["SubjectID"].unique(), default=None)
    with col_3:
        question = st.multiselect("Fråga", data["QuestionText"].unique(), default=None)
    with col_4:
        search = st.text_input("Sök", placeholder="Sök på innehåll i svaren")

    # Apply filters
    filtered_data = get_data_subset(data, area, subject, question, search)

    # Display filtered results
    _, column, _ = st.columns([0.1, 0.5, 0.4])
    with column:
        # Styling for the response display
        st.markdown("""
            <style>
            .answer-container {
                background-color: #f2f2f2;
                padding: 15px;
                border-radius: 20px;
                margin: 10px 0px;
            }
            .answer-container-right {
                margin-left: auto;
                max-width: 70%;
            }
            .answer-container-left {
                margin-right: auto;
                max-width: 70%;
            }
            .answer-text {
                color: #31333f;
                word-wrap: break-word;
            }
            </style>
            """, unsafe_allow_html=True)

        # Display responses with alternating alignment
        for index, row in filtered_data.iterrows():
            answer = row["StringResponse"]
            alignment_class = "answer-container-right" if index % 2 == 0 else "answer-container-left"
            st.markdown(f"""
                <div class='answer-container {alignment_class}'>
                    <p class='answer-text'>{answer}</p>
                </div>""", unsafe_allow_html=True)

if isinstance(st.session_state.get("data"), pd.DataFrame):
    display_data()