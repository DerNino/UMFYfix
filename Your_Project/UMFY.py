pip install streamlit
streamlit run app.py

import streamlit as st
import sqlite3
import os
from datetime import datetime

# Funktion zur Initialisierung der Datenbank
def init_db():
    conn = sqlite3.connect('app.db', check_same_thread=False)
    c = conn.cursor()
    # Tabelle für Nutzer: id, username, password, role (admin oder participant)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )''')
    # Tabelle für Übungen: id, title, description, file_path, timestamp
    c.execute('''CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    file_path TEXT,
                    timestamp TEXT
                )''')
    # Tabelle für Views: welche Übung von welchem Nutzer angesehen wurde
    c.execute('''CREATE TABLE IF NOT EXISTS views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_id INTEGER,
                    user_id INTEGER,
                    timestamp TEXT
                )''')
    conn.commit()
    return conn

conn = init_db()

# Standardnutzer erstellen (Admin und zwei Teilnehmer)
def create_default_users(conn):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin123", "admin"))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("user1", "user123", "participant"))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("user2", "user123", "participant"))
        conn.commit()
    except sqlite3.IntegrityError:
        # Falls die Nutzer bereits existieren, passiert nichts
        pass

create_default_users(conn)

# Nutze die in der Session gespeicherten Nutzerdaten
user = st.session_state['user']
st.sidebar.write(f"Angemeldet als: {user['username']} ({user['role']})")
st.title("Sportverein App")

if user['role'] == 'admin':
    st.header("Admin-Bereich: Übungen hochladen")
    
    # Formular zum Hochladen einer neuen Übung
    with st.form("exercise_form", clear_on_submit=True):
        title = st.text_input("Übungstitel")
        description = st.text_area("Übungsbeschreibung")
        uploaded_file = st.file_uploader("Übungsvideo oder Bild", type=["mp4", "jpg", "png"])
        submitted = st.form_submit_button("Übung hochladen")
        if submitted:
            file_path = ""
            if uploaded_file is not None:
                # Erstelle den Upload-Ordner, falls nicht vorhanden
                if not os.path.exists("uploads"):
                    os.makedirs("uploads")
                file_path = os.path.join("uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            # Übung in die Datenbank einfügen
            c = conn.cursor()
            c.execute("INSERT INTO exercises (title, description, file_path, timestamp) VALUES (?, ?, ?, ?)", 
                      (title, description, file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            st.success("Übung hochgeladen!")
            st.experimental_rerun()

    st.header("Übersicht der hochgeladenen Übungen")
    c = conn.cursor()
    c.execute("SELECT * FROM exercises ORDER BY timestamp DESC")
    exercises = c.fetchall()
    for ex in exercises:
        st.subheader(f"{ex[1]} - {ex[4]}")
        st.write(ex[2])
        if ex[3]:
            if ex[3].endswith(('.jpg', '.png')):
                st.image(ex[3])
            elif ex[3].endswith('.mp4'):
                st.video(ex[3])
        # Zeige die Anzahl der Ansichten
        c.execute("SELECT COUNT(*) FROM views WHERE exercise_id=?", (ex[0],))
        view_count = c.fetchone()[0]
        st.write(f"Anzahl Ansichten: {view_count}")
        # Liste der Nutzer, die die Übung gesehen haben
        c.execute("""SELECT u.username FROM views v 
                     JOIN users u ON v.user_id = u.id 
                     WHERE v.exercise_id=?""", (ex[0],))
        viewers = c.fetchall()
        if viewers:
            st.write("Gesehen von: " + ", ".join([v[0] for v in viewers]))
        st.write("---")
        
else:
    st.header("Übungen ansehen")
    c = conn.cursor()
    c.execute("SELECT * FROM exercises ORDER BY timestamp DESC")
    exercises = c.fetchall()
    for ex in exercises:
        st.subheader(f"{ex[1]} - {ex[4]}")
        st.write(ex[2])
        if ex[3]:
            if ex[3].endswith(('.jpg', '.png')):
                st.image(ex[3])
            elif ex[3].endswith('.mp4'):
                st.video(ex[3])
        # Button zum Markieren, dass die Übung angesehen wurde
        if st.button(f"Als gesehen markieren - {ex[1]}", key=f"view_{ex[0]}"):
            c.execute("SELECT * FROM views WHERE exercise_id=? AND user_id=?", (ex[0], user['id']))
            if c.fetchone() is None:
                c.execute("INSERT INTO views (exercise_id, user_id, timestamp) VALUES (?, ?, ?)",
                          (ex[0], user['id'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("Als gesehen markiert!")
            else:
                st.info("Bereits als gesehen markiert.")
            st.experimental_rerun()
