import streamlit as st
import streamlit_antd_components as sac
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Assume db is already set in the session state
db = st.session_state.get("db")
data = st.session_state.get("data")
summaries = db.fetch_survey_summaries()

# --- VISUALISATION ---
def placeholder_chart_data(insight_name):
    """Generate a placeholder DataFrame with counts of positive, neutral, and negative."""
    data = {
        'Sentiment': ['Positive', 'Neutral', 'Negative'],
        'Count': np.random.choice(a=np.arange(10,100), size=3)
    }
    df = pd.DataFrame(data)
    return df

def render_chart(row):
    df_chart = placeholder_chart_data(row['InsightName'])
    fig = generate_plotly_chart(df_chart)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def generate_plotly_chart(df):
    """Generate a minimalist Plotly horizontal stacked bar chart with a height of 20px from a DataFrame."""
    fig = go.Figure()

    # Adding each sentiment category as a separate trace
    fig.add_trace(go.Bar(
        y=['Sentiment'],
        x=[df[df['Sentiment'] == 'Positive']['Count'].values[0]],
        name='Positive',
        marker_color='#5CAA7F',
        orientation='h',
        text=str(df[df['Sentiment'] == 'Positive']['Count'].values[0]),  # Show actual value
        textposition='inside'  # Position the text inside the bar
    ))

    fig.add_trace(go.Bar(
        y=['Sentiment'],
        x=[df[df['Sentiment'] == 'Neutral']['Count'].values[0]],
        name='Neutral',
        marker_color='#dad7cd',
        orientation='h',
        text=str(df[df['Sentiment'] == 'Neutral']['Count'].values[0]),  # Show actual value
        textposition='inside'  # Position the text inside the bar
    ))

    fig.add_trace(go.Bar(
        y=['Sentiment'],
        x=[df[df['Sentiment'] == 'Negative']['Count'].values[0]],
        name='Negative',
        marker_color='#8B202C',
        orientation='h',
        text=str(df[df['Sentiment'] == 'Negative']['Count'].values[0]),  # Show actual value
        textposition='inside'  # Position the text inside the bar
    ))

    # Update layout to remove unnecessary elements and reduce margins
    fig.update_layout(
        barmode='stack',
        showlegend=False,  # Hide legend
        margin=dict(l=0, r=0, t=0, b=0),  # Tight layout
        height=30,  # Set height to 20px
        xaxis=dict(
            showgrid=False,  # Hide gridlines
            zeroline=False,  # Hide zero line
            showline=False,  # Hide axis line
            showticklabels=False  # Hide x-axis labels
        ),
        yaxis=dict(
            showgrid=False,  # Hide gridlines
            zeroline=False,  # Hide zero line
            showline=False,  # Hide axis line
            showticklabels=False  # Hide y-axis labels
        ),
        plot_bgcolor='rgba(0,0,0,0)'  # Make background transparent
    )

    return fig

# --- TEXT BOXES ---
def calculate_height(word_count, base_height=120, height_per_word=4):
    """Calculate the required height for a container based on the word count."""
    return base_height + (word_count * height_per_word)

def get_max_word_count(rows):
    """Get the maximum word count from a list of descriptions."""
    return max(len(row["InsightDescription"].split()) for row in rows)

def render_survey_card(row, height):
    """Render a single survey card with a specified height."""
    st.markdown(
        f"""
        <div style="
            height: {height}px; 
            background-color: #FFFFFF; 
            padding: 20px; 
            border-radius: 10px; 
            display: flex; 
            margin-bottom: 10px;
            flex-direction: column; 
            justify-content: space-between;">

        <div style="
            font-size: 20px; 
            font-weight: bold; 
            margin-bottom: 10px;"
            >{row['InsightName']}
        </div>

        <div style="
            flex-grow: 1;"
            >{row['InsightDescription']}
        </div> 
        """,
        unsafe_allow_html=True
    )

# --- GENERAL RENDERING ---
def show_survey_overview(summaries, data):
    cols = st.columns(3)
    current_row = []
    
    for i, row in summaries.iterrows():
        current_row.append(row)
        
        if len(current_row) == 3 or i == len(summaries) - 1:
            # Calculate the maximum height for the current row
            max_word_count = get_max_word_count(current_row)
            box_height = calculate_height(max_word_count)
            
            # Render the row
            for j, row in enumerate(current_row):
                with cols[j]:
                    with st.container(border=True):
                        render_survey_card(row, box_height)
                        render_chart(row)
                        if st.button(
                            "Läs mer", 
                            key=row['InsightName'],
                            use_container_width=True
                            ):
                            st.switch_page("pages/themes.py")
            
            # Add spacing between rows
            st.markdown(
                f"""<div style="margin-bottom: 20px;"></div>""",
                unsafe_allow_html=True
            )

            # Reset for the next row
            current_row = []
            cols = st.columns(3)

# --- RUN ---

st.title("Enkätöversikt")

# Define your tabs with more customization
custom_tabs = [
    sac.TabsItem(label='Ämnen', icon="archive"),
    sac.TabsItem(label='Fritext', icon = "collection")
]

# Display custom tabs and get the selected tag
selected_tab = sac.tabs(
    custom_tabs, 
    format_func='title', 
    align='left', 
    key="main_tabs", 
    size='md', 
    use_container_width=False, 
    variant='outline'
    )

if selected_tab == "Ämnen":
    show_survey_overview(summaries[:9], data)
else:
    pass