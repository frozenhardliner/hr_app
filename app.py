import streamlit as st
import sqlite3
import Face_Detection, Database, Report, Support
from streamlit.config import on_config_parsed
from streamlit_option_menu import option_menu
st.set_page_config(
     page_title="Face Detection App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="collapsed")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
def heavy_imports() -> None:
    from streamlit_option_menu import option_menu    
on_config_parsed(heavy_imports) 
conn = sqlite3.connect("worker_database.db")
class MultiApp:
    with st.sidebar:
        st.image("img2.png")
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })
    def run():
        # app = st.sidebar(
        with st.sidebar:        
            selected = option_menu("Menu", ["Check In/Out", 'Database', 'Report', 'Support'], 
                icons=['house', 'database-fill-up', 'file-earmark-text', 'person-raised-hand'], menu_icon="cast", default_index=0,
                    styles={
        "container": {"padding": "0!important", "background-color": "transparent"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link-selected": {"background-color": "blue"},
    })
        if selected == "Check In/Out":
            Face_Detection.app()
        if selected == "Database":
            Database.app()
        if selected == "Report":
            Report.app()
        if selected == "Support":
            Support.app()
    run()

