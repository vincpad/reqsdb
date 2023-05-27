import streamlit as st
from streamlit_antd_components.Tree import antd_tree, TreeItem
from reqDb_peewee import reqDb, rdb
from bigtree import Node, list_to_tree_by_relation
from streamlit_quill import st_quill
from annotated_text import annotated_text

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

def newItem(category):
    sourceItem = st.session_state['selectedItem']
    sourceItemDf = rdb.getItemsDf(local_id=sourceItem)
    
    if(category == "FOLDER"):
        st.text(f'Creating a new folder under the {rdb.getSetKeyPrefix(sourceItem)} set')
        name = st.text_input("Name")
        st.write("Description")
        description = st_quill()
        def createItem():
            rdb.addFolder(name, description, "vrocher", sourceItem)
            viewMode()
        st.button("Create new", on_click=createItem)
        
    if(category == "SET"):
        st.text(f'Creating a new set under the {rdb.getSetKeyPrefix(sourceItem)} project')
        name = st.text_input("Name")
        prefix = st.text_input("Prefix")
        st.text("Description")
        description = st_quill()
        def createItem():
            setHeadLocalId = rdb.addSetOfRequirements(name=name, prefix=prefix, description=description,project="OB1", user="vrocher")
            rdb.addRelation(sourceItem, setHeadLocalId, "HIERARCHY")
            viewMode()
        st.button("Create a new set of requirements", on_click=createItem)
        
    elif(category == "REQUIREMENT"):
        st.text(f'Creating a new requirement under the {rdb.getSetKeyPrefix(sourceItem)} set')
        name = st.text_input("Name")
        st.write("Description")
        description = st_quill()
        type = rdb.getSetKeyPrefix(sourceItem)
        def createItem():
            newItemLocalId = rdb.addItem(name=name, description=description, type=type ,project_prefix="OB1", user="vrocher")
            rdb.addRelation(sourceItem, newItemLocalId, "HIERARCHY")
            viewMode()
        st.button("Create new", on_click=createItem)


def viewItem():
    local_id = st.session_state['selectedItem']
    itemDf = rdb.getItemsDf(local_id=local_id)
    annotated_text(f"Viewing item {local_id}  ", (f'{itemDf.loc[0]["category"]}', "", "#FF4500"),(f'V{itemDf.loc[0]["version"]}', "", "#32CD32"))
    # get the item type        
    if(itemDf.loc[0]["category"] == "REQUIREMENT"):
        st.dataframe(rdb.getItemsDf(local_id=local_id))
        st.dataframe(rdb.getHistoryDf(localId=local_id))
        st.button("Edit", on_click=editMode)
        
    elif(itemDf.loc[0]["category"] == "SET"):
        st.dataframe(rdb.getItemsDf(prefix=rdb.getSetKeyPrefix(local_id)))
        st.write(rdb.getChildren(local_id, "HIERARCHY"))
        st.button("New Requirement", on_click=newReqMode)
        st.button("New Folder", on_click=newFolderMode)
        
    elif(itemDf.loc[0]["category"] == "FOLDER"):
        # st.dataframe(rdb.getItemsDf(prefix=rdb.getSetKeyPrefix(local_id)))
        st.write(rdb.getChildren(local_id, "HIERARCHY"))
        st.button("New Requirement", on_click=newReqMode)
        st.button("New Folder", on_click=newFolderMode)
    
    elif(itemDf.loc[0]["category"] == "PROJECT"):
        st.button("New Set", on_click=newSetMode)
        
    # else:
    #     st.dataframe(rdb.getItemsDf(local_id=local_id))
    #     st.button("New Requirement", on_click=newReqMode)
    #     st.button("New Folder", on_click=newFolderMode)


def editItem():
    local_id = st.session_state['selectedItem']
    itemDf = rdb.getItemsDf(local_id=local_id)
    annotated_text(f"Viewing item {local_id}  ",(f'V{itemDf.loc[0]["version"]}', "", "#32CD32"))
    name = st.text_input("Name", itemDf.loc[0]["name"])
    st.write("Description")
    description = st_quill(itemDf.loc[0]["description"])
    statusList = rdb.getStatusList()
    status = st.selectbox("Status", statusList, index=statusList.index(itemDf.loc[0]["status"]))
    
    
    st.write("Reason of the modification")
    modification_reason = st_quill()
    
    
    type = st.selectbox("Type", rdb.getReqTypeList("OB1"))
    def updateItem():
        rdb.updateItem(justification = modification_reason, local_id=local_id, name=name, description=description, username="vrocher", status=status)
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
        emoji_table = {"REQUIREMENT":"file-text", "PROJECT":"rocket-takeoff", "FOLDER":"folder", "SET":"paperclip"}
        return TreeItem(name, key, icon=emoji_table[category])
    
    root_item = item(root.name)
    
    def iterateChildren(root, root_item):
        if root.children:
            for i in root.children:
                newItem = item(i.name)
                if root_item.children is None:
                    root_item.children = []
                root_item.children = [*root_item.children ,newItem]
                iterateChildren(i, newItem)
    
    iterateChildren(root, root_item)

    selected_values = antd_tree(items=[root_item], show_line=True)
    # if the selected value changed, and we were on edit mode, return to view mode
    if(st.session_state['oldSelectedItem'] != st.session_state['selectedItem'] and st.session_state['mode'] in ("edit","new")):
        st.session_state['mode'] = "view"
    
    if(selected_values): # if a value has been selected, store it to the session state
        st.session_state['oldSelectedItem'] = st.session_state['selectedItem']
        st.session_state['selectedItem'] = selected_values[0]
        if st.session_state['mode'] == "home":
            st.session_state['mode'] = "view"
    

# %%
