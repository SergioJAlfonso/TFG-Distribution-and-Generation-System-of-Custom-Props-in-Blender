import bpy 
from mathutils import Euler
from ..ItemClasses.ItemRules import *

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

def createObjectsInPointsNS(objectData, object, boundingBoxObject, collection):
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

def change_search(self, context, nodeSol, vertices, asset, asset_bounding_box_local, collection, target):
        actionsSol = None
        if nodeSol is not None:
            actionsSol = nodeSol.solution()
        else:
            # bpy.context.window_manager.popup("Couldn't distribute objects!", title="Error", icon='ERROR')
            self.report({'ERROR'}, "Couldn't distribute objects!")
            return {'FINISHED'}

        objectsData = []
        for i in range(len(actionsSol)):
            indexVertex = actionsSol[i].indexVertex
            objRotation = actionsSol[i].rotation
            objectsData.append([vertices[indexVertex][0], vertices[indexVertex][1], objRotation])

        createObjectsInPoints(objectsData, asset, asset_bounding_box_local, collection)
        
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

def setPanelItemRules(context):
    
    # get item rules from panel
    rotation_x = context.scene.rotate_x
    rotation_y = context.scene.rotate_y
    rotation_z = context.scene.rotate_z

    rotation_range_x = context.scene.rot_range_x
    rotation_range_y = context.scene.rot_range_y
    rotation_range_z = context.scene.rot_range_z

    rotation_steps_x = context.scene.rot_steps_x
    rotation_steps_y = context.scene.rot_steps_y
    rotation_steps_z = context.scene.rot_steps_z

    can_overlap = context.scene.overlap_bool

    use_box = context.scene.bbox_bool

    item_distance = context.scene.item_distance

    scale_min = context.scene.scale_factor_min
    scale_max = context.scene.scale_factor_max

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

    return rules