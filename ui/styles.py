import streamlit as st


def apply_custom_styles():
    """
    Aplica estilos visuales personalizados a la aplicación Streamlit.
    """

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1300px;
        }

        section[data-testid="stSidebar"] {
            background-color: #1f2330;
            border-right: 1px solid #303545;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #f2f4f8;
        }

        div[data-testid="stMetric"] {
            background-color: #171b26;
            padding: 18px 20px;
            border-radius: 14px;
            border: 1px solid #2d3344;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.25);
        }

        div[data-testid="stMetricLabel"] {
            font-size: 15px;
            color: #b8bcc8;
        }

        div[data-testid="stMetricValue"] {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
            padding: 14px 18px;
            margin-top: 8px;
            margin-bottom: 20px;
        }

        div.stButton > button {
            border-radius: 10px;
            height: 42px;
            font-weight: 600;
        }

        .section-card {
            background-color: #111722;
            padding: 22px;
            border-radius: 16px;
            border: 1px solid #2d3344;
            margin-bottom: 20px;
        }

        .app-caption {
            color: #b8bcc8;
            font-size: 16px;
            margin-bottom: 20px;
        }

        div[data-testid="stCaptionContainer"] {
            color: #9da3b2;
        }
        </style>
        """,
        unsafe_allow_html=True
    )