import streamlit as st
from datetime import datetime
import os
import sqlite3
import pandas as pd
from PIL import Image
import hashlib

def init_db():
    conn = sqlite3.connect("bol.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS organisms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species TEXT,
            common_name TEXT,
            location TEXT,
            date TEXT,
            image_path TEXT,
            user TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect("bol.db")
    df = pd.read_sql_query("SELECT * FROM organisms", conn)
    conn.close()
    return df

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def add_user(username, password):
    conn = sqlite3.connect("bol.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, make_hashes(password)))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def login_user(username, password):
    conn = sqlite3.connect("bol.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return check_hashes(password, data[0])
    return False

init_db()


st.set_page_config(page_title="Species Addition", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in:
    st.title("Book of Life — Portal Access")
    auth_mode = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)
    
    username_input = st.text_input("Username").strip()
    password_input = st.text_input("Password", type="password")

    if auth_mode == "Login":
        if st.button("Log In", type="primary"):
            if login_user(username_input, password_input):
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.success(f"Welcome back, {username_input}!")
                st.rerun()
            else:
                st.error("Invalid.")
                
    elif auth_mode == "Sign Up":
        if st.button("Create Account", type="primary"):
            if username_input and password_input:
                if add_user(username_input, password_input):
                    st.success("Account created. Log in.")
                else:
                    st.error("Username exists.")
            else:
                st.error("No players. Empty field.")
    st.stop() 
df = get_data()


with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.username}**")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

st.title("Book of Life")
st.markdown("@sixie6e")
st.image("/img/rbn1.png")


with st.container(border=True):
    uploaded_file = st.file_uploader("Image", type=["png"])

col1, col2 = st.columns(2)
with col1:
    species = st.text_input("Species")
    date = st.text_input("Date/Time")
with col2:
    common_name = st.text_input("Common Name")        
    loc = st.text_input("Location")

if st.button("Review Submission", type="primary"):
    st.subheader("Submission Preview")
    st.markdown(f"> {species} \n\n> {common_name} \n\n> {loc} {date} \n")
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Submission Preview")

if st.button("Submit"):
    if species and common_name:
        image_path = ""
        if uploaded_file is not None:
            save_dir = "img/"
            os.makedirs(save_dir, exist_ok=True)
            image_path = os.path.join(save_dir, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        conn = sqlite3.connect("bol.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO organisms (species, common_name, location, date, image_path, user)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (species, common_name, loc, date, image_path, st.session_state.username))
        conn.commit()
        conn.close()
        st.success(f"Successfully added {common_name} to the Book of Life!")
        st.rerun() 
    else:
        st.error("No players, empty field.")

if not df.empty:
    num_columns = 3
    for i in range(0, len(df), num_columns):
        cols = st.columns(num_columns)
        for j in range(num_columns):
            if i + j < len(df):
                row = df.iloc[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(row["common_name"])
                        
                        record_owner = row["user"] if "user" in df.columns and row["user"] else "System"
                        st.caption(f"Submitted by: {record_owner}")
                        
                        img_path = row["image_path"]
                        if img_path and os.path.exists(img_path):
                            try:
                                opened_img = Image.open(img_path)
                                st.image(opened_img, width=True)
                            except Exception:
                                st.caption("Error Loading Image File")
                        else:
                            st.caption("No Image Available")
                        
                        if st.button("View Details", key=f"btn_{row['id']}"):
                            st.info(f"{row['species']}\n\n{row['location']}\n\n{row['date']}")

                        if record_owner == st.session_state.username:
                            delete_key = f"confirm_{row['id']}"
                            if delete_key not in st.session_state:
                                st.session_state[delete_key] = False

                            if not st.session_state[delete_key]:
                                if st.button("Remove Addition", key=f"btn_remove_{row['id']}"):
                                    st.session_state[delete_key] = True
                                    st.rerun()
                            else:
                                st.warning("Are you sure?")
                                col_yes, col_no = st.columns(2)
                                
                                with col_yes:
                                    if st.button("Yes", key=f"yes_{row['id']}", type="primary"):
                                        del_conn = sqlite3.connect("bol.db")
                                        del_c = del_conn.cursor()
                                        del_c.execute("DELETE FROM organisms WHERE id = ?", (int(row['id']),))
                                        del_conn.commit()
                                        del_conn.close()
                                       
                                        if img_path and os.path.exists(img_path):
                                            try:
                                                os.remove(img_path)
                                            except Exception:
                                                pass
                                            
                                        st.session_state[delete_key] = False
                                        st.rerun()
                                        
                                with col_no:
                                    if st.button("No", key=f"no_{row['id']}"):
                                        st.session_state[delete_key] = False
                                        st.rerun()
