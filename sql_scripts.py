import sqlite3, streamlit as st, cv2, face_recognition, pandas as pd
import os, numpy as np
from datetime import datetime,timedelta
import pandas as pd, io,base64
conn = sqlite3.connect("worker_database.db")
# Define a function to create and return a database connection
def create_connection(database_name):
    conn = sqlite3.connect(database_name)
    return conn

# Define a function to initialize the database tables if they don't exist
def initialize_database(conn):
    cursor = conn.cursor()
    
    # Create the workers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
               Id  INTEGER PRIMARY KEY AUTOINCREMENT,
               Name TEXT NOT NULL,
               Department TEXT,
               Position TEXT,
               Date_registered DATETIME,
               photo BLOB
        )
    """)

    # Create the registration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration (
               Id  INTEGER NOT NULL,
               Date DATE NOT NULL,
               Check_in_dt DATETIME,
               Check_out_dt DATETIME,
               Status TEXT, 
               Check_in_time real,
               Check_out_time real
        )
    """)

    conn.commit()
    cursor.close()

def has_user_checked_in_today(conn ,Id, current_date):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration where Date = ?  and Id = ?", (current_date,Id ))
    result = cursor.fetchall()
    # If no record is found for today, check if the user ID exists in the table
    if result is None:
        cursor.execute("SELECT * FROM registration WHERE Id = ?", (Id,))
        result = cursor.fetchone()
    cursor.close()
    return True if result != [] else False

def check_out(conn, Id, current_date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO registration VALUES")


def registration_table(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration")
    registration_data = cursor.fetchall()
    cursor.close()
    return registration_data

def get_worker_ids(conn)    :
    cursor = conn.cursor()
    cursor.execute("SELECT Id FROM workers")
    ids = cursor.fetchall()
    cursor.close()
    return [name[0] for name in ids]

def get_max_id(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Id) FROM workers")
    max_id = cursor.fetchall()
    cursor.close()
    if max_id[0][0] is not None:
        id = max_id[0][0]
    else:
        id = 0
    return id

def worker_info(conn, Id):
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Department, Position from workers where Id = ?", (Id,))
    result = cursor.fetchall()
    cursor.close()
    if result:
        info = {
            "Name": result[0][0],
            "Department": result[0][1],
            "Position": result[0][2]
        }
        return info
    else:
        return None

def show_workers(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Department, Position, Date_registered from workers")
    headers = [description[0] for description in cursor.description]
    workers_db = cursor.fetchall()
    cursor.close()
    return [headers] + workers_db

def delete_worker_table(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM workers")
    conn.commit()

    # Remove all photos
    photo_folder = 'visitor_database'
    for file_name in os.listdir(photo_folder):
        file_path = os.path.join(photo_folder, file_name)
        os.remove(file_path)
    st.session_state['images'] = []
    st.session_state['classnames'] = []
    st.session_state['encodelist'] = []


def load_new_image(image):
    current_image = cv2.imread(image)
    try:
        img = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)[0]
        st.session_state.encodelist.append(encoded_face)
        st.session_state.images.append(current_image)
        st.session_state.classnames.append(os.path.splitext(os.path.basename(image))[0])
    except:
        st.write("Couldn't recognise face of employee, try 1 more time please")

def load_not_encoded(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT Id FROM workers")
    workers = [str(row[0]) for row in cursor.fetchall()]
    available_classnames = [str(classname) for classname in st.session_state.classnames]
    cursor.close()
    not_in_available = list(set(workers) - set(available_classnames))
    return not_in_available

def remove_image(Id):
    try:
        position = st.session_state.classnames.index(str(Id))
        st.session_state.classnames.pop(position)
        st.session_state.images.pop(position)
        st.session_state.encodelist.pop(position)
    except:
        pass

def load_images_and_classnames():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    visitor_database = os.path.join(root_dir, "visitor_database")
    st.session_state['images'] = []
    st.session_state['classnames'] = []
    st.session_state['encodelist'] = []
    mylist = os.listdir(visitor_database)
    for photo in mylist:
        current_image = cv2.imread(f'{visitor_database}/{photo}')
        st.session_state.images.append(current_image)
        st.session_state.classnames.append(os.path.splitext(photo)[0])
        img = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(img)[0]
        st.session_state.encodelist.append(encoded_face)
    return st.session_state.images, st.session_state.classnames, st.session_state.encodelist

# def find_encodings(images):
#     st.session_state.encodelist = []
#     for index, img in enumerate(images):
#         try:
#             img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             encoded_face = face_recognition.face_encodings(img)[0]
#             st.session_state.encodelist.append(encoded_face)
#         except:
#             print(f"Couldn't recognise photo of index {index}")
#     return st.session_state.encodelist

def find_face(new_worker_photo):
    bytes_data = new_worker_photo.getvalue()
    image = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(image, (0, 0), None, 0.25, 0.25)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect face locations in the image
    face_locations = face_recognition.face_locations(img)
    face_number = len(face_locations)
    if len(face_locations) == 1:
        # Draw rectangles around detected faces
        for face_location in face_locations:
            y1, x2, y2, x1 = face_location
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(image, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        
        # Display the image with detected faces
        st.image(image, channels="BGR", use_column_width=True)
        return face_number
    elif len(face_locations) != 1:
        st.write(" :confused: No faces detected in the photo or more than 1 faces are found.")  
        return face_number

def get_week_dates(week_offset = 0):
    current_date = datetime.now().date()
    start_date = current_date - timedelta(days=current_date.weekday()) - timedelta(weeks=week_offset)
    end_date = start_date + timedelta(days=6)
    return start_date, end_date
def generate_report(conn, choosen_date,option_select):
    df = pd.DataFrame()
    if choosen_date == "Today":
        start_date, end_date = datetime.now().date(), datetime.now().date()
    elif choosen_date == "Yesterday":
        start_date = datetime.now().date() - timedelta(days=1)
        end_date = start_date
    elif choosen_date == "This Week":
        start_date, end_date = get_week_dates(0)
    elif choosen_date == "Last Week":
        start_date, end_date = get_week_dates(1)
    elif option_select == "Date Range":
        start_date,end_date = choosen_date
    elif option_select == "Date":
        start_date,end_date = choosen_date,choosen_date
    query = """
    SELECT r.*, w.Name, w.Department, w.Position, 
    CASE WHEN r.Check_out_time IS NULL THEN 0
    ELSE (strftime('%s', r.Check_out_time) - strftime('%s', r.Check_in_time)) / 3600.0
    END AS Hour
    FROM registration AS r
    INNER JOIN workers AS w ON r.Id = w.Id
    WHERE r.Date BETWEEN ? AND ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    if result:
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(result, columns=columns)
    cursor.close()
    return df
def download_excel(dataframe, filename):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, sheet_name='data', index=False)

    excel_buffer.seek(0)
    b64 = base64.b64encode(excel_buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}.xlsx">Download {filename} File</a>'
    #st.write(f"Successfully downloaded {filename}")
    return href

# Create a function to close the database connection
def close_connection(conn):
    conn.close()