import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Species Addition", layout="centered")

st.title("Book of Life")
st.markdown("@sixie6e")
st.header("Taxonomy Data")
st.image("rbn.png") # static, need to add img upload
with st.container(border=True): 
    col1, col2 = st.columns([2, 2])
    with col1:
        species = st.text_input("Species", placeholder="Sitta canadensis")
        date = st.text_input("Date/Time", placeholder="Mon DD, YYYY")
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
