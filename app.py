import streamlit as st
# from dynamic_tabs import dynamic_tabs
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

st.set_page_config(layout="wide")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized'],
)

name, authentication_status, username = authenticator.login('Login', 'main')

# if authentication_status:
#     authenticator.logout('Logout', 'main', key='unique_key')
#     st.write(f'Welcome *{name}*')
#     st.title('Some content')
if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

# if the user is authentified, show the app
if authentication_status:
    import gui
    if 'selectedItem' not in st.session_state:
        st.session_state['selectedItem'] = ""
    if 'oldSelectedItem' not in st.session_state:
        st.session_state['oldSelectedItem'] = ""
    if 'mode' not in st.session_state:
        st.session_state['mode'] = "home"

    # st.set_page_config(layout="wide")

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
        gui.newItem(category="REQUIREMENT")
    elif st.session_state['mode'] == "newFolder":
        gui.newItem(category="FOLDER")
    elif st.session_state['mode'] == "newSet":
        gui.newItem(category="SET")

    print(
        f"mode:{st.session_state['mode']}, selectedItem:{st.session_state['selectedItem']}, oldSelectedItem:{st.session_state['oldSelectedItem']}")
