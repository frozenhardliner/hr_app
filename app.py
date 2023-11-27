import streamlit as st
import sqlite3
import Face_Detection, Database, Report
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
            selected = option_menu("Main Menu", ["Face Detection", 'Database', 'Report'], 
                icons=['house', 'gear'], menu_icon="cast", default_index=0)
        if selected == "Face Detection":
            Face_Detection.app()
        if selected == "Database":
            Database.app()
        if selected == "Report":
            Report.app()
    
    run()
