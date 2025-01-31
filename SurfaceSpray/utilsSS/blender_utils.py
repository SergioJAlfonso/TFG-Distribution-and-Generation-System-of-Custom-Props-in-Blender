import bpy 
from mathutils import Euler
from .ItemRules import *

from .geometry_utils import (adjustPosition, adjustRotation, adjustScale)

def createObjectsInPoints(points, object, boundingBoxObject, collection):
    inCollection = False 
    #In case something else has been selected, we deselect everything
    bpy.ops.object.select_all(action='DESELECT')
    #Set Active object in case it has changed
    bpy.context.view_layer.objects.active = object 
    #Create object in points
    
    for i in range(len(points)):
        object.select_set(True)
        bpy.ops.object.duplicate(linked=1)
        #We catch new object duplicated
        newObj = bpy.context.active_object
        
        newObj.location = points[i][0]
        #Set location relative to size
        adjustPosition(newObj, boundingBoxObject, points[i][1])

        newObj.rotation_euler = Euler(points[i][2], 'XYZ')

        #Unlink from all collections and link in desired collection
        if(inCollection == False):
            linkedCollection = newObj.users_collection
            #Link before unlink from everything
            collection.objects.link(newObj)
            for col in linkedCollection:
                if(col is not None): col.objects.unlink(newObj)
            inCollection = True
        #Set Active object to new object so we can duplicate from this point
        object = bpy.context.active_object

def createObjectsInPointsN(objectData, object, boundingBoxObject, collection):
    inCollection = False 
    #In case something else has been selected, we deselect everything
    bpy.ops.object.select_all(action='DESELECT')
    #Set Active object in case it has changed
    bpy.context.view_layer.objects.active = object 
    #Create object in points
    
    for i in range(len(objectData)):
        object.select_set(True)
        bpy.ops.object.duplicate(linked=1)
        #We catch new object duplicated
        newObj = bpy.context.active_object
        
        newObj.location = objectData[i][0]
        #Set location relative to size
        adjustPosition(newObj, boundingBoxObject, objectData[i][1])

        adjustRotation(newObj, objectData[i][1], objectData[i][2])
        #newObj.rotation_euler = Euler(points[i][2], 'XYZ')

        #Unlink from all collections and link in desired collection
        if(inCollection == False):
            linkedCollection = newObj.users_collection
            #Link before unlink from everything
            collection.objects.link(newObj)
            for col in linkedCollection:
                if(col is not None): col.objects.unlink(newObj)
            inCollection = True
        #Set Active object to new object so we can duplicate from this point
        object = bpy.context.active_object

def createObjectsInPointsNS(objectData, object, boundingBoxObject, collection, normal_factor = 1):
    inCollection = False 
    #In case something else has been selected, we deselect everything
    bpy.ops.object.select_all(action='DESELECT')
    #Set Active object in case it has changed
    bpy.context.view_layer.objects.active = object 
    #Create object in points
    
    for i in range(len(objectData)):
        object.select_set(True)
        bpy.ops.object.duplicate(linked=1)
        #We catch new object duplicated
        newObj = bpy.context.active_object
        
        # Set scale
        adjustScale(newObj, objectData[i][3])
        
        newObj.location = objectData[i][0]
        #Set location relative to size
        adjustPosition(newObj, boundingBoxObject, objectData[i][1])

        adjustRotation(newObj, objectData[i][1], objectData[i][2], normal_factor)
        #newObj.rotation_euler = Euler(points[i][2], 'XYZ')

        #Unlink from all collections and link in desired collection
        if(inCollection == False):
            linkedCollection = newObj.users_collection
            #Link before unlink from everything
            collection.objects.link(newObj)
            for col in linkedCollection:
                if(col is not None): col.objects.unlink(newObj)
            inCollection = True
        #Set Active object to new object so we can duplicate from this point
        object = bpy.context.active_object

def createObjectsInPointsNSMulti(objectData, assets, boundingBoxObject, collection, normal_factor = 1):
    #In case something else has been selected, we deselect everything
    bpy.ops.object.select_all(action='DESELECT')
 
    #Create object in points
    for i in range(len(objectData)):
        #Take current object
        obj_index = int(objectData[i][4])
        object = assets[obj_index]
        #Set Active object in case it has changed
        # bpy.context.view_layer.objects.active = object 

        # object.select_set(True)
        
        # bpy.ops.object.duplicate(linked=1)
        
        #We catch new object duplicated
        # newObj = bpy.context.active_object
        newObj = object.copy()
        
        collection.objects.link(newObj)
        # Set scale
        adjustScale(newObj, objectData[i][3])
        
        newObj.location = objectData[i][0]
        #Set location relative to size
        adjustPosition(newObj, boundingBoxObject[obj_index], objectData[i][1])

        adjustRotation(newObj, objectData[i][1], objectData[i][2], normal_factor)
        #newObj.rotation_euler = Euler(points[i][2], 'XYZ')

        #Unlink from all collections and link in desired collection
        
        # linkedCollection = newObj.users_collection
        # #Link before unlink from everything
        # collection.objects.link(newObj)
        # for col in linkedCollection:
        #     if(col is not None): col.objects.unlink(newObj)
            

        object.select_set(False)
        #Set Active object to new object so we can duplicate from this point
        #object = bpy.context.active_object

#deprecated
def change_search(self, context, nodeSol, vertices, asset, asset_bounding_box_local, collection, target):
        actionsSol = None
        if nodeSol is not None:
            #If we take a Node to take it actions or a list of Action. For retrocompatibility purposes
            if(type(nodeSol).__name__ == "Node"):
                actionsSol = nodeSol.solution()
            else:
                actionsSol = nodeSol
        else:
            # bpy.context.window_manager.popup("Couldn't distribute objects!", title="Error", icon='ERROR')
            self.report({'ERROR'}, "Couldn't distribute objects!\n" + 
                        "Try to paint more, lower density or disable overlap")
            return {'FINISHED'}

        objectsData = []
        for i in range(len(actionsSol)):
            indexVertex = actionsSol[i].indexVertex
            objRotation = actionsSol[i].rotation
            objectsData.append([vertices[indexVertex][0], vertices[indexVertex][1], objRotation])

        createObjectsInPoints(objectsData, asset, asset_bounding_box_local, collection)
        
        if (context.scene.subdivide):
            bpy.data.meshes.remove(target.data)

def change_searchN(self, context, nodeSol, vertices, assets, assets_bounding_box_local, collection, target):
        
        actionsSol = None
        #If we take a Node to take it actions or a list of Actions. For retrocompatibility purposes
        if(type(nodeSol).__name__ == "Node"):
            actionsSol = nodeSol.solution()
        else:
            actionsSol = nodeSol

        #Get just one solution
        # if nodeSol is not None:
        #     actionsSol = nodeSol[0].solution()
        # else:
        #     self.report({'ERROR'}, "Couldn't distribute objects!")
        #     return {'FINISHED'}

        objectsData = []
        #We obtain data from actions to create real objects.
        # ObjectData: [pos, normal, rotation, scale, index]
        for i in range(len(actionsSol)):
            indexVertex = actionsSol[i].indexVertex
            objRotation = actionsSol[i].rotation
            objScale = actionsSol[i].scale
            objIndex = actionsSol[i].asset_index
            objectsData.append(
                [vertices[indexVertex][0], vertices[indexVertex][1], objRotation, objScale, objIndex])

        # Save objectData
        context.scene.objects_data.clear()
        context.scene.objects_data.append(objectsData)

        createObjectsInPointsNSMulti(objectsData, assets,
                              assets_bounding_box_local, collection, context.scene.adjust_normal_value)

        if (context.scene.subdivide):
            bpy.data.meshes.remove(target.data)

        return {'FINISHED'}


def initCollection(collection, nameCollection, checkPartialSol = False):
    """ 
    If collection with given name exists, it's cleaned of objects.
    Else, it's created from zero.

    Returns:
    Collection initialized
    """
    #Si existe, borramos sus objetos, de lo contrario, 
    #creamos una coleccion nueva
    if collection is not None:
        clearCollection(collection, checkPartialSol)
    else:
        collection = bpy.data.collections.new(nameCollection)
        bpy.context.scene.collection.children.link(collection)

    return collection

def duplicateObject(obj, data=True, actions=True, collection=None):
    obj_copy = obj.copy()
    if data:
        obj_copy.data = obj_copy.data.copy()
    if actions and obj_copy.animation_data:
        obj_copy.animation_data.action = obj_copy.animation_data.action.copy()
    if collection != None:
        collection.objects.link(obj_copy)

        
    return obj_copy

def deleteObject(obj):
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.objects.active = obj 
    obj.select_set(True)
    bpy.ops.object.delete() 

def clearCollection(collection, checkPartialSol = False):
    partialSol = bpy.context.scene.partialsol
    
    for obj in collection.objects:
        #Search if object is a partial sol. If it is, dont remove it.
        j = 0
        while(checkPartialSol and j < len(partialSol) and  obj.name != partialSol[j].name):
            j+=1

        if(j >= len(partialSol) or checkPartialSol == False):    
            bpy.data.objects.remove(obj, do_unlink=True)

def setPanelItemRules(context, item_index = 0):
    
    # get item rules from panel
    use_box = context.scene.itemRules_HashMap["bbox_bool"][item_index]
    
    if(use_box):
        rotation_x = rotation_y = rotation_z = False
    else:
        rotation_x = context.scene.itemRules_HashMap["rotate_x"][item_index]
        rotation_y = context.scene.itemRules_HashMap["rotate_y"][item_index]
        rotation_z = context.scene.itemRules_HashMap["rotate_z"][item_index]

    rotation_range_x = context.scene.itemRules_HashMap["rot_range_x"][item_index]
    rotation_range_y = context.scene.itemRules_HashMap["rot_range_y"][item_index]
    rotation_range_z = context.scene.itemRules_HashMap["rot_range_z"][item_index]

    rotation_steps_x = context.scene.itemRules_HashMap["rot_steps_x"][item_index]
    rotation_steps_y = context.scene.itemRules_HashMap["rot_steps_y"][item_index]
    rotation_steps_z = context.scene.itemRules_HashMap["rot_steps_z"][item_index]

    can_overlap = context.scene.itemRules_HashMap["overlap_bool"][item_index]


    item_distance = context.scene.itemRules_HashMap["item_distance"][item_index]

    scale_min = context.scene.itemRules_HashMap["scale_factor_min"][item_index]
    scale_max = context.scene.itemRules_HashMap["scale_factor_max"][item_index]

    appearance_prob = context.scene.itemRules_HashMap["item_weight"][item_index]

    #Set Item rules
    rules = ItemRules()

    rules.rotations = [rotation_x, rotation_y, rotation_z]
    rules.rotation_range = [rotation_range_x, rotation_range_y, rotation_range_z]
    rules.rotation_steps = [rotation_steps_x, rotation_steps_y, rotation_steps_z]
    rules.overlap = can_overlap
    rules.use_bounding_box = use_box
    rules.distance_between_items = item_distance
    rules.min_scale_factor = scale_min
    rules.max_scale_factor = scale_max
    rules.appear_weight = appearance_prob

    return rules

def existsCollectionName(nameCollection):
    for collection in bpy.data.collections:
        if collection.name == nameCollection:
             return True
        
def ShowMessageBox(title = "Message Box", message = "", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def checkAndReplaceCollectioName(context, nameCollection, assetsNames_):
    #Check if previous distribution is different to this.
    newCollectionName = None

    if(len(context.scene.previous_distributionObjs) > 0 ):
        firstSetDifferent = set(context.scene.previous_distributionObjs) - set(assetsNames_)
        secondSetDifferent = set(assetsNames_) - set(context.scene.previous_distributionObjs)
        if (firstSetDifferent or secondSetDifferent):
            if existsCollectionName(nameCollection):
                #Replace collection name operator.
                bpy.ops.addon.replace_collec_name()
                #update name Collection
                newCollectionName = context.scene.collectName

            print("Las listas son diferentes")
            context.scene.previous_distributionObjs.clear() 
            context.scene.previous_distributionObjs.extend(assetsNames_)

    else:
        context.scene.previous_distributionObjs.extend(assetsNames_)

    return newCollectionName
            
