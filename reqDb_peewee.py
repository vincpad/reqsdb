# %% create models : omm dbscheme.sql  -m sqlalchemy
from models_peewee import *
import pandas as pd
from utilities import check_email

# try:
# newcateg = Categories(name="REQUIREMENT")


# except:
class reqDb:
    # # Categories management
    def addCategory(self, name):
        Categories(name=name).save()

    def addRelationType(self, name):
        RelationsTypes(name=name).save()

    # Status management
    def addStatus(self, name):
        Status(name=name).save()

    # Projects management
    def addProject(self, name, prefix, description, username):
        projectId = Projects(name=name, prefix=prefix, description=description).save()
        self.addType(name=name, prefix=prefix, description=description, category_name="PROJECT", project_prefix=prefix)
        self.addItem(name, description=description, type=prefix,
                     project_prefix=prefix, user=username, set_key_prefix=prefix)

    # # Types management
    def addType(self, name, prefix, description, category_name, project_prefix):
        categ = Categories.get(Categories.name == category_name)
        project_id = Projects.get(Projects.prefix == project_prefix)
        newtype = Types(name=name, prefix=prefix, description=description, category=categ, project=project_id)
        newtype.save()

    # User management
    def addUser(self, user_name, full_name, email, role):
        if (check_email(email)):
            newuser = Users(user_name=user_name, full_name=full_name, email=email, role=role)
            newuser.save()
        else:
            print(f"Wrong email : {email}")

    def updateUser(self, user_name, full_name, email, role, enabled=""):
        user = Users.get(user_name == user_name)
        user.full_name = full_name
        user.email = email
        user.role = role
        if (enabled is bool):
            user.enabled = enabled
        user.save()

    def generateIds(self, prefix, projectName):
        # get the number of existing items under this prefix
        type = Types.get(Types.prefix == prefix)
        localReqs = list(Items.select().where(Items.type == type))
        globalReqs = list(Items.select())
        numberOfLocalItems = len(localReqs)
        numberOfGlobalItems = len(globalReqs)

        localId = f'{projectName}-{prefix}-{numberOfLocalItems + 1}'
        globalId = f'GLOBAL-{numberOfGlobalItems+1}'
        return localId, globalId

    # Item management
    def addItem(self, name, description, type, project_prefix, user, set_key_prefix=None):
        itemtype = Types.get(Types.prefix == type)
        project = Projects.get(Projects.prefix == project_prefix)
        _user = Users.get(Users.user_name == user)
        status = Status.get(Status.get(Status.name == "New"))
        # create the item entry
        localId, globalId = self.generateIds(type, project_prefix)

        if not set_key_prefix:  # if no set key as been given, create the item without set key
            newitem = Items(type_id=itemtype, global_id=globalId, local_id=localId, project_id=project)
        else:
            set_key = Types.get(Types.prefix == set_key_prefix, Types.project == project)
            newitem = Items(type_id=itemtype, global_id=globalId, local_id=localId, project_id=project, set_key=set_key)

        # create the fields entry
        newfield = Fields(name=name, description=description)

        newversion = Versions(item_id=newitem, fields_id=newfield, user_id=_user,
                              status=status, justification="Creation")
        newitem.save()
        newfield.save()
        newversion.save()
        return localId

    def updateItem(self, justification, local_id, name, description, username, status):
        item = Items.get(Items.local_id == local_id)
        user = Users.get(Users.user_name == username)
        _status = Status.get(Status.name == status)

        # get the number of existing items under this prefix
        versions = Versions.select().where(Versions.item_id == item)
        numberOfVersions = len(versions)

        # create the fields entry
        newfield = Fields(name=name, description=description)

        newversion = Versions(item_id=item, fields_id=newfield, user_id=user, status=_status,
                              justification=justification, number=numberOfVersions + 1)

        newfield.save()
        newversion.save()

    def getItemsDf(self, local_id="", global_id="", prefix="", project_prefix="OB1"):
        if prefix == "":  # it is a single requirement
            item = ""
            if local_id != "":
                print(f"localid:{local_id}")
                item = Items.get(Items.local_id == local_id)
            if global_id != "":
                item = Items.get(Items.global_id == global_id)
            versions = Versions.select().where(Versions.item_id == item).order_by(Versions.number.asc())
            last_version = list(versions)[-1]
            last_field = Fields.get(Fields.id == last_version.fields_id)
            type = Types.get(Types.id == item.type)
            category = Categories.get(Categories.id == type.category)
            df = pd.DataFrame(data=[[local_id, last_field.name, last_field.description, last_version.status.name, last_version.number, type.prefix, category.name]],
                              columns=['local_id', 'name', 'description', 'status', 'version', 'type', 'category'])
            return df
        else:
            type = Types.get(Types.prefix == prefix)
            project = Projects.get(Projects.prefix == project_prefix)
            # latest_version_query = (Versions
            #             .select(Versions.item_id, fn.MAX(Versions.number).alias('max_number'))
            #             .join(Items)
            #             .where(Items.project == project)
            #             .group_by(Versions.item_id)
            #             .alias('sub'))
            # latest_versions = (Versions
            #         .select()
            #         .join(latest_version_query, on=((Versions.item_id == latest_version_query.c.item_id) & (Versions.number == latest_version_query.c.max_number))))
            latest_versions = (Versions
                               .select()
                               .join(Items)
                               .join(Types, on=(Items.type == Types.id))
                               .where(Types.project == project, Types.prefix == prefix)
                               .group_by(Versions.item_id)
                               .having(Versions.number == fn.MAX(Versions.number)))

            df = pd.DataFrame(columns=["local_id", "name", "description", 'status'])

            for i in list(latest_versions):
                fields = Fields.get(Fields.id == i.fields)
                item = Items.get(Items.id == i.item_id)
                local_id = item.local_id
                name = fields.name
                description = fields.description
                status = Status.get(Status.id == i.status)
                df.loc[len(df)] = [local_id, name, description, status]

            return df

    def getHistoryDf(self, localId):
        item = Items.get(Items.local_id == localId)
        versions = Versions.select().where(Versions.item_id == item).order_by(Versions.number.desc())
        df = pd.DataFrame(columns=["Version", "Name", "Description"])
        for i in list(versions):
            fields = Fields.get(Fields.id == i.fields)
            df.loc[len(df)] = [i.number, fields.name, fields.description]
        return df

    def getTypeDf(self, prefix, project):
        projectId = Projects.get(Projects.name == project)
        type = Types.get(Types.prefix == prefix, Types.project == projectId)
        category = Categories.get(Categories.id == type.category)
        df = pd.DataFrame(columns=["name", "prefix", "description", "category"],
                          data=[[type.name, type.prefix, type.description, category.name]])
        return df

    def getItemsList(self):
        items = Items.select()
        local_ids = [i.local_id for i in list(items)]
        return local_ids

    def addRelation(self, parentLocalId, childLocalId, type):
        parent = Items.get(Items.local_id == parentLocalId)
        child = Items.get(Items.local_id == childLocalId)
        typeId = RelationsTypes.get(RelationsTypes.name == type)
        Relations(parent_id=parent, child_id=child, type_id=typeId).save()

    def deleteRelation(self, parentLocalId, childLocalId, type):
        parent = Items.get(Items.local_id == parentLocalId)
        child = Items.get(Items.local_id == childLocalId)
        typeId = RelationsTypes.get(RelationsTypes.name == type)
        query = Relations.get(Relations.parent_id == parent, Relations.child_id == child, Relations.type_id == typeId)
        query.delete_instance()

    def getChildren(self, parentLocalId, type):
        parent = Items.get(Items.local_id == parentLocalId)
        typeId = RelationsTypes.get(RelationsTypes.name == type)
        childRelations = list(Relations.select(Relations.child_id).where(
            Relations.parent_id == parent, Relations.type_id == typeId))
        children = [Items[i.child_id].local_id for i in childRelations]
        return children

    def getParents(self, childLocalId, type):
        child = Items.get(Items.local_id == childLocalId)
        typeId = RelationsTypes.get(RelationsTypes.name == type)
        parentRelations = list(Relations.select(Relations.parent_id).where(
            Relations.child_id == child, Relations.type_id == typeId))
        parents = [Items[i.parent_id].local_id for i in parentRelations]
        return parents

    def getRelationsList(self, type):
        typeId = RelationsTypes.get(RelationsTypes.name == type)
        relations = Relations.select().where(Relations.type_id == typeId)
        relationsList = []
        for r in relations:
            parent = Items.get(Items.id == r.parent_id).local_id
            child = Items.get(Items.id == r.child_id).local_id
            relationsList.append((parent, child))
        return relationsList

    def getTypesList(self, projectPrefix):
        project = Projects.get(Projects.prefix == projectPrefix)
        types = Types.select().where(Types.project == project)
        types_list = [t.prefix for t in list(types)]
        return types_list

    def getReqTypeList(self, projectPrefix):
        project = Projects.get(Projects.prefix == projectPrefix)
        reqCategory = Categories.get(Categories.name == "REQUIREMENT")
        types = Types.select().where(Types.project == project, Types.category == reqCategory)
        types_list = [t.prefix for t in list(types)]
        return types_list

    def getCategory(self, localId):
        item = Items.get(Items.local_id == localId)
        type = Types.get(Types.id == item.type)
        category = Categories.get(Categories.id == type.category_id)
        return category.name

    def getItem(self, localId):
        return Items.get(Items.local_id == localId)

    def getPrefix(self, item):
        return Types.get(Types.id == item.type).prefix

    def getItemNameByLocalId(self, localId, projectPrefix):
        project = Projects.get(Projects.prefix == projectPrefix)
        item = Items.select().join(Types).where(Items.local_id == localId, Types.project == project).first()
        return item.name

    def getStatusList(self):
        return [s.name for s in list(Status.select())]

    def addSetOfRequirements(self, name, prefix, description, project, user):
        # create the requirement type
        self.addType(name, prefix, description, "REQUIREMENT", project)
        # create the set head item
        projectId = Projects.get(Projects.name == project)
        setItemLocalId = self.addItem(name, description, "SET", project, user, set_key_prefix=prefix)
        return setItemLocalId

    def getSetKeyPrefix(self, setHeadLocalId):
        setHeadItemKey = Items.get(Items.local_id == setHeadLocalId).set_key
        return Types.get(Types.id == setHeadItemKey).prefix

    def addFolder(self, name, description, user, sourceItemLocalId, project_prefix="OB1"):
        newItemLocalId = self.addItem(name=name, description=description, type="FLD",
                                      project_prefix=project_prefix, user=user, set_key_prefix=rdb.getSetKeyPrefix(sourceItemLocalId))
        self.addRelation(sourceItemLocalId, newItemLocalId, "HIERARCHY")

    def lockItem(self, local_id, projectPrefix, user):
        userId = Users.get(Users.user_name == user)
        project = Projects.get(Projects.prefix == projectPrefix)
        item = Items.select().join(Types, on=(Items.type == Types.id)
                                   ).where(Types.project == project, Items.local_id == local_id).first()
        item.locked_by = userId
        item.save()

    def unlockItem(self, local_id, projectPrefix):
        project = Projects.get(Projects.prefix == projectPrefix)
        item = Items.select().join(Types, on=(Items.type == Types.id)
                                   ).where(Types.project == project, Items.local_id == local_id).first()
        item.locked_by = None
        item.save()

    def checkLock(self, local_id, projectPrefix):
        project = Projects.get(Projects.prefix == projectPrefix)
        item = Items.select().join(Types, on=(Items.type == Types.id)).where(
            Types.project == project, Items.local_id == local_id).first()
        return Users.get(Users.id == item.locked_by).user_name


rdb = reqDb()


def initAll():
    initialize_db()
    rdb.addUser(user_name="vrocher", full_name="Vincent Rocher", email="vr@hypr-space.com", role="Admin")
    rdb.addCategory(name="FOLDER")
    rdb.addCategory(name="REQUIREMENT")
    rdb.addCategory(name="PROJECT")
    rdb.addCategory(name="SET")
    rdb.addStatus(name="New")
    rdb.addStatus(name="Closed")
    rdb.addRelationType(name="HIERARCHY")
    rdb.addRelationType(name="DERIVEDFROM")

    rdb.addProject(name="OB1", prefix="OB1", description="Le microlanceur", username="vrocher")

    rdb.addType("Set of requirements", "SET", "Set of requirements", "SET", "OB1")
    rdb.addType("Folder", "FLD", "Folder", "FOLDER", "OB1")

    newSet = rdb.addSetOfRequirements(name="Stakeholders Needs", prefix="STK",
                                      description="Stakeholders needs", project="OB1", user="vrocher")
    rdb.addRelation("OB1-OB1-1", newSet, "HIERARCHY")
    newItem1 = rdb.addItem("Being profitable", "Make money in other terms", "STK", "OB1", "vrocher")
    rdb.addRelation(newSet, newItem1, "HIERARCHY")

    newSet = rdb.addSetOfRequirements(name="Laws", prefix="LAW", description="Law", project="OB1", user="vrocher")
    rdb.addRelation("OB1-OB1-1", newSet, "HIERARCHY")
    newItem2 = rdb.addItem("Respect the law", "Because we need to", "LAW", "OB1", "vrocher")
    rdb.addRelation(newSet, newItem2, "HIERARCHY")

    newSet = rdb.addSetOfRequirements(name="System requirements", prefix="SYSS",
                                      description="System related requirement", project="OB1", user="vrocher")
    rdb.addRelation("OB1-OB1-1", newSet, "HIERARCHY")
    newItem3 = rdb.addItem("Do things because of law and stakeholder ", "Because we need to", "SYSS", "OB1", "vrocher")
    rdb.addRelation(newSet, newItem3, "HIERARCHY")

    rdb.addRelation(newItem1, newItem3, "DERIVEDFROM")
    rdb.addRelation(newItem2, newItem3, "DERIVEDFROM")


# initAll()

# %%


# rdb.addType("Reglementation Technique", "RT", "car on est français", "FOLDER", "OB1")
# rdb.addType("Reglement d'exploitation intérieure", "REI", "parce que le CSG", "FOLDER", "OB1")

# add a set

# rdb.addItem("Stakeholders needs", "Stakeholders needs", "SET", "OB1", "vrocher")
# rdb.addRelation("OB1-OB1-1","OB1-SET-1")
# #%%
# for i in range(0,10):
#     localid = rdb.addItem("Go to Space", "We want not to explode", "SFTY", "OB1", "vrocher")
#     rdb.addRelation("OB1-OB1-1", localid)
# # #%%
# # rdb.updateItem("because we can", "OB1-SFTY-1", "changed", "changeddext", "vrocher", "New")


# rdb.addChild("OB1-SFTY-1", "OB1-SFTY-2")


# %%
