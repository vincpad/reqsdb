import streamlit as st
from streamlit_antd_components import antd_tree, TreeItem
from streamlit_antd_components import Buttons
from streamlit_antd_components.Buttons import ButtonsItem
from reqDb_peewee import reqDb, rdb
from bigtree.tree.construct import list_to_tree_by_relation
from streamlit_quill import st_quill
from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd


def newSetMode():
    st.session_state['mode'] = "newSet"


def newReqMode():
    st.session_state['mode'] = "newReq"


def newFolderMode():
    st.session_state['mode'] = "newFolder"


def editMode():
    st.session_state['mode'] = "edit"


def viewMode():
    st.session_state['mode'] = "view"


def getIcon(name, size=20):
    icons = dict({"file-text": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" fill="currentColor" class="bi bi-file-text" viewBox="0 0 16 16"><path d="M5 4a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1H5zm-.5 2.5A.5.5 0 0 1 5 6h6a.5.5 0 0 1 0 1H5a.5.5 0 0 1-.5-.5zM5 8a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1H5zm0 2a.5.5 0 0 0 0 1h3a.5.5 0 0 0 0-1H5z"/><path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2zm10-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1z"/></svg>',
                  "rocket-takeoff": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" fill="currentColor" class="bi bi-rocket-takeoff" viewBox="0 0 16 16"><path d="M9.752 6.193c.599.6 1.73.437 2.528-.362.798-.799.96-1.932.362-2.531-.599-.6-1.73-.438-2.528.361-.798.8-.96 1.933-.362 2.532Z"/><path d="M15.811 3.312c-.363 1.534-1.334 3.626-3.64 6.218l-.24 2.408a2.56 2.56 0 0 1-.732 1.526L8.817 15.85a.51.51 0 0 1-.867-.434l.27-1.899c.04-.28-.013-.593-.131-.956a9.42 9.42 0 0 0-.249-.657l-.082-.202c-.815-.197-1.578-.662-2.191-1.277-.614-.615-1.079-1.379-1.275-2.195l-.203-.083a9.556 9.556 0 0 0-.655-.248c-.363-.119-.675-.172-.955-.132l-1.896.27A.51.51 0 0 1 .15 7.17l2.382-2.386c.41-.41.947-.67 1.524-.734h.006l2.4-.238C9.005 1.55 11.087.582 12.623.208c.89-.217 1.59-.232 2.08-.188.244.023.435.06.57.093.067.017.12.033.16.045.184.06.279.13.351.295l.029.073a3.475 3.475 0 0 1 .157.721c.055.485.051 1.178-.159 2.065Zm-4.828 7.475.04-.04-.107 1.081a1.536 1.536 0 0 1-.44.913l-1.298 1.3.054-.38c.072-.506-.034-.993-.172-1.418a8.548 8.548 0 0 0-.164-.45c.738-.065 1.462-.38 2.087-1.006ZM5.205 5c-.625.626-.94 1.351-1.004 2.09a8.497 8.497 0 0 0-.45-.164c-.424-.138-.91-.244-1.416-.172l-.38.054 1.3-1.3c.245-.246.566-.401.91-.44l1.08-.107-.04.039Zm9.406-3.961c-.38-.034-.967-.027-1.746.163-1.558.38-3.917 1.496-6.937 4.521-.62.62-.799 1.34-.687 2.051.107.676.483 1.362 1.048 1.928.564.565 1.25.941 1.924 1.049.71.112 1.429-.067 2.048-.688 3.079-3.083 4.192-5.444 4.556-6.987.183-.771.18-1.345.138-1.713a2.835 2.835 0 0 0-.045-.283 3.078 3.078 0 0 0-.3-.041Z"/><path d="M7.009 12.139a7.632 7.632 0 0 1-1.804-1.352A7.568 7.568 0 0 1 3.794 8.86c-1.102.992-1.965 5.054-1.839 5.18.125.126 3.936-.896 5.054-1.902Z"/></svg>',
                  "paperclip": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" fill="currentColor" class="bi bi-paperclip" viewBox="0 0 16 16"><path d="M4.5 3a2.5 2.5 0 0 1 5 0v9a1.5 1.5 0 0 1-3 0V5a.5.5 0 0 1 1 0v7a.5.5 0 0 0 1 0V3a1.5 1.5 0 1 0-3 0v9a2.5 2.5 0 0 0 5 0V5a.5.5 0 0 1 1 0v7a3.5 3.5 0 1 1-7 0V3z"/></svg>',
                  "link": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" fill="currentColor" class="bi bi-link" viewBox="0 0 16 16"><path d="M6.354 5.5H4a3 3 0 0 0 0 6h3a3 3 0 0 0 2.83-4H9c-.086 0-.17.01-.25.031A2 2 0 0 1 7 10.5H4a2 2 0 1 1 0-4h1.535c.218-.376.495-.714.82-1z"/><path d="M9 5.5a3 3 0 0 0-2.83 4h1.098A2 2 0 0 1 9 6.5h3a2 2 0 1 1 0 4h-1.535a4.02 4.02 0 0 1-.82 1H12a3 3 0 1 0 0-6H9z"/></svg>',
                  "none": ""})
    return icons[name]


def iconThenText(icon, text, size="1rem", iconSize=20):
    st.write(getIcon(icon, iconSize) + " " + f'<span style="font-size:{size}">{text}</span>', unsafe_allow_html=True)


def parameterValue(parameter, value):
    hello = "oui"
    element = f'''
    <b>{parameter}:</b></br>
    <span>{value}</span>
    '''
    st.write(element, unsafe_allow_html=True)


def parameterRelation(parameter):
    element = f'''
    <b>{parameter}:</b></br>
    '''
    st.write(element, unsafe_allow_html=True)


def newItem(category):
    sourceItem = st.session_state['selectedItem']
    sourceItemDf = rdb.getItemsDf(local_id=sourceItem)

    if (category == "FOLDER"):
        st.text(f'Creating a new folder under the {rdb.getSetKeyPrefix(sourceItem)} set')
        name = st.text_input("Name")
        st.write("Description")
        description = st_quill()

        def createItem():
            rdb.addFolder(name, description, "vrocher", sourceItem)
            viewMode()
        st.button("Create new", on_click=createItem)

    if (category == "SET"):
        print(f"sourceItem:{sourceItem}")
        st.text(f'Creating a new set under the {rdb.getSetKeyPrefix(sourceItem)} project')
        name = st.text_input("Name")
        prefix = st.text_input("Prefix")
        st.text("Description")
        description = st_quill()

        def createItem():
            setHeadLocalId = rdb.addSetOfRequirements(
                name=name, prefix=prefix, description=description, project="OB1", user="vrocher")
            rdb.addRelation(sourceItem, setHeadLocalId, "HIERARCHY")
            viewMode()
        st.button("Create a new set of requirements", on_click=createItem)

    elif (category == "REQUIREMENT"):
        st.text(f'Creating a new requirement under the {rdb.getSetKeyPrefix(sourceItem)} set')
        name = st.text_input("Name")
        st.write("Description")
        description = st_quill()
        type = rdb.getSetKeyPrefix(sourceItem)

        def createItem():
            newItemLocalId = rdb.addItem(name=name, description=description, type=type,
                                         project_prefix="OB1", user="vrocher")
            rdb.addRelation(sourceItem, newItemLocalId, "HIERARCHY")
            viewMode()
        st.button("Create new", on_click=createItem)


def viewItem():
    local_id = st.session_state['selectedItem']
    itemDf = rdb.getItemsDf(local_id=local_id)
    st.warning("vrocher is currently editing this item, it is therefore locked for edition.")
    # get the item type
    if (itemDf.loc[0]["category"] == "REQUIREMENT"):
        headerCol1, headerCol2 = st.columns([2, 1])
        with headerCol2:
            headButtons = [ButtonsItem("Edit", "pencil-square",)]
            group = Buttons.antd_buttons(headButtons, align="end")
            if group == 0:
                editMode()
                group = None
                # st.experimental_rerun()
        with headerCol1:
            st.markdown(f'#### {itemDf.loc[0]["name"]} :blue[[V{itemDf.loc[0]["version"]}]]')
            type = rdb.getTypeDf(itemDf.loc[0]["type"], "OB1")
            iconThenText("file-text", type.loc[0]["name"])

        body, rightPane = st.columns([6, 1])
        with body:
            parameterValue("PROJECT ID", local_id)
            parameterValue("GLOBAL ID", local_id)
            parameterValue("NAME", itemDf.loc[0]["name"])
            parameterValue("DESCRIPTION", itemDf.loc[0]["description"])
            parameterValue("RATIONALE", itemDf.loc[0]["description"])
            parameterValue("VALIDATION METHOD", itemDf.loc[0]["description"])
            parameterRelation("RELATIONS")
            c1, c2 = st.columns(2)
            with c1:
                iconThenText("link", "Upstream:")
                childrenList = rdb.getChildren(local_id, "DERIVEDFROM")
                data = []
                for i in childrenList:
                    idf = rdb.getItemsDf(local_id=i)
                    data.append([i, idf.loc[0]["name"], "Derived from"])
                df = pd.DataFrame(columns=["ID", "Name", "Relation type"], data=data)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection()
                relationsList = AgGrid(df, gridOptions=gb.build(), columns_auto_size_mode="FIT_ALL_COLUMNS_TO_VIEW",
                                       enable_enterprise_modules=True, key="upstream", reload_data=True)
                buttons = [ButtonsItem("New", "plus"),
                           ButtonsItem("Remove selected", "trash")]
                group = Buttons.antd_buttons(buttons, align="start", key="upstreamButt")
                if group == 0:  # add button clicked
                    select = st.selectbox("selection", options=rdb.getItemsList(), key="selectChild")

                    def addItem():
                        rdb.addRelation(local_id, select, "DERIVEDFROM")
                    st.button("Add selected", on_click=addItem)
                    pass
                if group == 1:  # delete button clicked
                    if (relationsList.selected_rows):
                        selectedId = relationsList.selected_rows[0]["ID"]
                        print(f"delete relation between {local_id} and {selectedId}")
                        st.warning(
                            f"Are you sure you want to delete the relation between {local_id} and {selectedId} ?", icon="⚠️")

                        def deleteRelation():
                            rdb.deleteRelation(local_id, selectedId, "DERIVEDFROM")
                            # st.experimental_rerun()
                        st.button("Yes", "confirmDeleteChild", on_click=deleteRelation)
                        # rdb.deleteRelation(local_id, selectedId, "DERIVEDFROM")
                    group = None

            with c2:
                iconThenText("link", "Downstream:")
                df = pd.DataFrame(columns=["ID", "Name", "Relation type"],
                                  data=[["test", "test", "test"]])
                AgGrid(df, columns_auto_size_mode="FIT_ALL_COLUMNS_TO_VIEW",
                       enable_enterprise_modules=False, key="downstream")

            parameterRelation("HISTORY")
            st.dataframe(rdb.getHistoryDf(localId=local_id))

        # with rightPane:
        #     iconThenText("link", "Upstream:0")
        #     df = pd.DataFrame(columns=["ID", "Name", "Relation type"],
        #                       data=[["test","test","test"]])
        #     AgGrid(df)
        #     iconThenText("link", "Downstream:0")

    elif (itemDf.loc[0]["category"] == "SET"):
        headButtons = [ButtonsItem("New Requirement", "file-text"),
                       ButtonsItem("New Folder", "folder")]
        group = Buttons.antd_buttons(headButtons, align="end")
        if group == 0:
            newReqMode()
            group = None
            # st.experimental_rerun()
        elif group == 1:
            newFolderMode()
            group = None
            # st.experimental_rerun()

        st.dataframe(rdb.getItemsDf(prefix=rdb.getSetKeyPrefix(local_id)))
        st.write(rdb.getChildren(local_id, "HIERARCHY"))

    elif (itemDf.loc[0]["category"] == "FOLDER"):
        # st.dataframe(rdb.getItemsDf(prefix=rdb.getSetKeyPrefix(local_id)))
        st.write(rdb.getChildren(local_id, "HIERARCHY"))
        st.button("New Requirement", on_click=newReqMode)
        st.button("New Folder", on_click=newFolderMode)

    elif (itemDf.loc[0]["category"] == "PROJECT"):
        headButtons = [ButtonsItem("New Set of Requirements", "paperclip")]
        group = Buttons.antd_buttons(headButtons, align="end")
        if group == 0:
            newSetMode()
            group = None
            # st.experimental_rerun()

    # else:
    #     st.dataframe(rdb.getItemsDf(local_id=local_id))
    #     st.button("New Requirement", on_click=newReqMode)
    #     st.button("New Folder", on_click=newFolderMode)


def editItem():
    local_id = st.session_state['selectedItem']
    itemDf = rdb.getItemsDf(local_id=local_id)
    name = st.text_input("Name", itemDf.loc[0]["name"])
    st.write("Description")
    description = st_quill(itemDf.loc[0]["description"])
    statusList = rdb.getStatusList()
    status = st.selectbox("Status", statusList, index=statusList.index(itemDf.loc[0]["status"]))

    st.write("Reason of the modification")
    modification_reason = st_quill()

    type = st.selectbox("Type", rdb.getReqTypeList("OB1"))

    def updateItem():
        rdb.updateItem(justification=modification_reason, local_id=local_id, name=name,
                       description=description, username="vrocher", status=status)
        print("item addded")
        st.session_state['mode'] = "view"
    st.button("Update", on_click=updateItem)


def itemsTree():
    relations = rdb.getRelationsList("HIERARCHY")

    root = list_to_tree_by_relation(relations)

    def item(key):
        itemDf = rdb.getItemsDf(local_id=key)
        name = itemDf.loc[0]["name"]
        category = itemDf.loc[0]["category"]
        emoji_table = {"REQUIREMENT": "file-text", "PROJECT": "rocket-takeoff", "FOLDER": "folder", "SET": "paperclip"}
        return TreeItem(name, icon=emoji_table[category], key=key)

    root_item = item(root.name)

    def iterateChildren(root, root_item):
        if root.children:
            for i in root.children:
                newItem = item(i.name)
                if root_item.children is None:
                    root_item.children = []
                root_item.children = [*root_item.children, newItem]
                iterateChildren(i, newItem)

    iterateChildren(root, root_item)

    selected_values = antd_tree(items=[root_item], show_line=True)
    print(selected_values)
    # if the selected value changed, and we were on edit mode, return to view mode
    print(f"selected{selected_values}")
    if (st.session_state['oldSelectedItem'] != st.session_state['selectedItem'] and st.session_state['mode'] in ("edit", "new")):
        st.session_state['mode'] = "view"

    if (selected_values):  # if a value has been selected, store it to the session state
        st.session_state['oldSelectedItem'] = st.session_state['selectedItem']
        st.session_state['selectedItem'] = selected_values[0]
        if st.session_state['mode'] == "home":
            st.session_state['mode'] = "view"


# %%
