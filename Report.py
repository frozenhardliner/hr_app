import streamlit as st
import sqlite3
from sql_scripts import generate_report, download_excel
from datetime import datetime
import pandas as pd
import io

# buffer to use for excel writer
buffer = io.BytesIO()
def app():
    if 'report_df' not in st.session_state:
        st.session_state.report_df = None
    conn = sqlite3.connect("worker_database.db")
    col1, col2, col3 = st.columns(3)
    col4, col5, col6,col7 = st.columns([1,1,2,2])
    col2.header(":blue[Generate Report]")
    st.header("", divider="blue")
    option_select = st.radio(":blue[Choose by]",("Default","Date", "Date Range"), horizontal=True)
    if option_select == "Date Range":
        from_date = col4.date_input(":blue[From Date]")
        to_date = col5.date_input(":blue[To Date]")
        choosen_date = (from_date,to_date)
    if option_select == "Default":
        choosen_date = st.radio(":blue[Pick Date to generate report]", 
                ("Today", "Yesterday", "This Week", "Last Week"))
    if option_select == "Date":
        choosen_date = col4.date_input(":blue[From Date]")
    if st.button("Generate Report"):
        if choosen_date and st.session_state.report_df is not None:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            report = generate_report(conn, choosen_date,option_select)
            st.session_state.report_df = pd.DataFrame(report)
    st.data_editor(st.session_state.report_df)
    if st.session_state.report_df is not None:
        if st.button("Download as Excel", type = "primary"):
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            filename = f"Report_{current_time}"
            excel = download_excel(st.session_state.report_df, filename)
            st.markdown(excel, unsafe_allow_html=True) 
