import streamlit as st, sqlite3, numpy as np
from datetime import datetime
import cv2
import face_recognition
from sql_scripts import *

def app():
    conn = sqlite3.connect("worker_database.db")
    cursor = conn.cursor()
    # Create table if does not exists
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
    conn.commit()


    if 'images' not in st.session_state:
        load_images_and_classnames()
    #st.write(st.session_state)
    col1,col2, col3 = st.columns(3)
    col2.subheader(":blue[Live Face Detection]")
    st.header("", divider="blue")
    name = None
    col1,col2,col3 = st.columns([5,1,1])
    with col1:
        img_file_buffer = st.camera_input(label="CCTV Camera")
        if img_file_buffer is not None:
            if len(st.session_state.encodelist)>=1:
                encoded_face_train = st.session_state.encodelist
                img_file_buffer = cv2.imdecode(np.frombuffer(img_file_buffer.read(), np.uint8), cv2.IMREAD_COLOR) 
                imgs = cv2.resize(img_file_buffer, (0, 0), None, 0.25, 0.25)
                imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)
                face_in_frame = face_recognition.face_locations(imgs)
                if len(face_in_frame) == 1:
                    encode_face = face_recognition.face_encodings(imgs, face_in_frame)
                    for encode_face, faceloc in zip(encode_face, face_in_frame):
                        matches = face_recognition.compare_faces(encoded_face_train, encode_face)
                        faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
                        matchIndex = np.argmin(faceDist)
                        #st.write(matchIndex)
                        if matches[matchIndex]:
                            id = int(st.session_state.classnames[matchIndex].upper().lower())
                            worker_info_result = worker_info(conn, id)
                            #st.write(worker_info_result)
                            name = worker_info_result["Name"]
                            department = worker_info_result["Department"]
                            position = worker_info_result["Position"]            
                            y1, x2, y2, x1 = faceloc
                            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                            cv2.rectangle(img_file_buffer, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.rectangle(img_file_buffer, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img_file_buffer, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                        else:
                            col2.warning("**Couldn't recognise face or found 2 or more face**")        
                    # Display the recognized image with highlighted faces
                    if name:
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        current_date =datetime.now().date()
                        current_time_h = datetime.now().strftime('%H:%M:%S')
                        col2.header(f"Have a nice day, {name}")
                        col2.image(img_file_buffer, channels='BGR', use_column_width=True)
                        col2.markdown(f"**Worker Name:**\n{name}")
                        col2.markdown(f"**Department:**\n{department}")
                        col2.markdown(f"**Position:**\n{position}")
                        col2.markdown(f"**Time Now:**\n{current_time}")
                        if has_user_checked_in_today(conn,id,current_date):
                            if col2.button("Check-Out"):
                                cursor.execute("UPDATE registration SET Check_out_dt = ?,Check_out_time = ?, Status = 'Check-out' WHERE Id = ? AND Date = ?",
                                            (current_time,current_time_h, id, current_date))
                                conn.commit()
                                col2.success("You checked out", icon = "✅")
                        else:
                            if col2.button("Check-In"):
                                cursor.execute("INSERT INTO registration (Id, Date, Check_in_dt, Check_out_dt, Status, Check_in_time,Check_out_time) VALUES (?,?,?,?,?,?,?)",
                                    ( id, current_date, current_time,None, 'Check-in',current_time_h, None))
                                conn.commit()
                                col2.success("You checked in", icon = "✅")    
                else:
                    col2.warning("**Couldn't recognise face or found 2 or more face**")
            else:
                col2.warning("**There is no data in Database**")