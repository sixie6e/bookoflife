import streamlit as st
from datetime import datetime
import os
import sqlite3
import pandas as pd

conn = sqlite3.connect("bol.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS organisms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        species TEXT,
        common_name TEXT,
        location TEXT,
        date TEXT,
        image_path TEXT
    )
""")
conn.commit()
df = pd.read_sql_query("SELECT * FROM organisms", conn)
st.set_page_config(page_title="Species Addition", layout="centered")

st.title("Book of Life")
st.markdown("@sixie6e")
st.image("/img/rbn.png")

with st.container(border=True):
    uploaded_file = st.file_uploader("Image", type=["png", "jpg", "jpeg"])

col1, col2 = st.columns([2, 2])
with col1:
    species = st.text_input("Species", placeholder="Sitta canadensis")
    date = st.text_input("Date/Time", placeholder="Mon DD, YYYY TT:TTA/P")
with col2:
    common_name = st.text_input("Common Name", placeholder="Red-breasted Nuthatch")        
    loc = st.text_input("Location", placeholder="Kennebec, ME")

if st.button("Review Submission", type="primary"):
    st.subheader(" Submission Preview")
    st.markdown(f"""
    > {species} \n
    > {common_name} \n
    > {loc} {date} \n
    """)
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Submission Preview")

if st.button("Submit"):
    if species and common_name:
        image_path = ""
        if uploaded_file is not None:
            save_dir = "/img/"
            os.makedirs(save_dir, exist_ok=True)
            image_path = os.path.join(save_dir, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        c.execute("""
            INSERT INTO organisms (species, common_name, location, date, image_path)
            VALUES (?, ?, ?, ?, ?)
        """, (species, common_name, loc, date, image_path))
        conn.commit()
        st.success(f"Successfully added {common_name} to the Book of Life!")
    else:
        st.error("No players, empty field.")

st.dataframe(df)
