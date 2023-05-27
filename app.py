import streamlit as st
# from dynamic_tabs import dynamic_tabs
import gui

if 'selectedItem' not in st.session_state:
    st.session_state['selectedItem'] = ""
if 'oldSelectedItem' not in st.session_state:
    st.session_state['oldSelectedItem'] = ""
if 'mode' not in st.session_state:
    st.session_state['mode'] = "home"
    

st.set_page_config(layout="wide")

# build the sidebar menus
with st.sidebar:
    st.title("Project : ")
    explorer, filter = st.tabs(["Explorer", "Filter"])
    with explorer:
        gui.itemsTree()

if st.session_state['mode'] == "view":
    gui.viewItem()
elif st.session_state['mode'] == "edit":
    gui.editItem()
elif st.session_state['mode'] == "newReq":
    gui.newItem(category = "REQUIREMENT")
elif st.session_state['mode'] == "newFolder":
    gui.newItem(category = "FOLDER")
elif st.session_state['mode'] == "newSet":
    gui.newItem(category = "SET")

    
print(st.session_state['mode'])