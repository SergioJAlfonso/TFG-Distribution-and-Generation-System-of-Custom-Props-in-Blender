import bpy 
from .utils.draw_utils import *
from .heuristics.ThresholdRandDistribution import *
from .utils.addon_utils import *

class MegaTron_OT_Operator(bpy.types.Operator):
    bl_idname = "addon.distribute"
    bl_label = "Simple operator"
    bl_description = "Distribute object over a surface"

    #crear diferentes grupos de vertices para cada objeto a distribuir
    # self = method defined for this class 
    def execute(self, context):
        # bpy.ops.view3d.snap_cursor_to_center()
        if(context.scene.target == None):
            self.report({'WARNING'}, 'You must select a target object!')
            return {'FINISHED'}

        if(context.scene.asset == None):
            self.report({'WARNING'}, 'You must select a target object!')
            return {'FINISHED'}


        #Obtenemos todos los datos necesarios 
        target = duplicateObject(context.scene.target)
        asset = context.scene.asset

        #Nota : bpy.types.Scene.num_assets != context.scene.num_assets
        #Get user property data
        nameCollection = context.scene.collectName
        threshold_weight = context.scene.threshold #valor de 0, 1
        num_instances = context.scene.num_assets
        
        collection = bpy.data.collections.get(nameCollection)
        collection = initCollection(collection, nameCollection)

        #Scale asset if necessary
        if(asset.scale[0] != 1 or asset.scale[1] != 1 or asset.scale[2] != 1):
            self.report({'WARNING'}, 'Asset scale will be applied!')
            bpy.context.active_object.select_set(False)
            bpy.context.view_layer.objects.active = asset
            bpy.ops.object.transform_apply(location = False, rotation = False, scale=True)

        #Get bounding box
        asset_bounding_box_local = getBoundingBox(context, asset)
        target_bounding_box_local = getBoundingBox(context, target)

        #Subdivide target to fit assets in every vertex
        if (context.scene.subdivide):
            makeSubdivision(target, asset_bounding_box_local, target_bounding_box_local)

        data_bidimensional = getVerticesWeight(target)
        bpy.data.meshes.remove(target.data)
        # print('Algorithm:', context.scene.algorithm_enum)
        distribution = ThresholdRandDistribution(None)
        sol = distribution.distribute(data_bidimensional, asset_bounding_box_local, 
                                      num_instances, threshold_weight)
        
        #TODO: Sumar bounding box a la normal donde se está posicionando
        createObjectsInPoints(sol, asset, asset_bounding_box_local, collection)

        #Delete the newly created target (Not used, the target deletes when context )
        # deleteObject(target)

        return {'FINISHED'}

    # static method
    @classmethod
    def poll(cls, context):
        # active object
        obj = context.object
        return (obj is not None) and (obj.mode == "OBJECT")

def createObjectsInPoints( points, object, boundingBoxObject, collection):
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
        
        #Set location relative to size
        newObj.location = points[i]
        newObj.location[2] += abs(boundingBoxObject[0][2]/2)
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
