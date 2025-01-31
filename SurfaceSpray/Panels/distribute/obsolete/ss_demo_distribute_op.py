import bpy 

from mathutils import Euler

from ....utilsSS.ItemRules import *
from ....utilsSS.Item import *

from ....utilsSS.Draw_utils import *
from ....utilsSS.Blender_utils import *
from ....heuristicsSS.obsolete.ThresholdRandDistribution import *
from ....heuristicsSS.Demos.Demo_Dist_RotRang_Distribution import *
from ....heuristicsSS.Demos.Demo_Dist_Overlap_Distribution import *
from ....utilsSS.Blender_utils import *
from ....utilsSS.Geometry_utils import *
from ....utilsSS.StateDistribution import *

from aima3.search import astar_search as aimaAStar
from aima3.search import breadth_first_tree_search as aimaBFTS
from aima3.search import depth_first_tree_search as aimaDFTS

from ...partialSol.partialSol_ops import *

class SurfaceSpray_OT_Operator_DEMO_SELECTION(bpy.types.Operator):
    bl_idname = "addon.distributedemo"
    bl_label = "Distribute Operator"
    bl_description = "Distribute object over a surface"

    #crear diferentes grupos de vertices para cada objeto a distribuir
    # self = method defined for this class 
    def execute(self, context):
        # bpy.ops.view3d.snap_cursor_to_center()
        if(context.scene.target == None):
            self.report({'WARNING'}, 'You must select a target object!')
            return {'FINISHED'}

        if(context.scene.asset == None):
            self.report({'WARNING'}, 'You must select an asset object!')
            return {'FINISHED'}
        
        if(context.scene.vgr_profile == " " or context.scene.vgr_profile == "" ):
            self.report({'WARNING'}, 'You must select an vertex group profile!')
            return {'FINISHED'}

        context.scene.solution_nodes.clear()
        context.scene.current_search = 1

        #Obtenemos todos los datos necesarios
        if (context.scene.subdivide): 
            target = duplicateObject(context.scene.target)
        else:
             target = context.scene.target

        asset = context.scene.asset

        #Note : bpy.types.Scene.num_assets != context.scene.num_assets
        #Get user property data
        numCutsSubdivision = context.scene.num_cuts
        nameCollection = context.scene.collectName
        threshold_weight = context.scene.threshold #valor de 0, 1
        num_instances = context.scene.num_assets
        
        #Make sure there are no duplicates
        bpy.ops.partialsol.remove_duplicates()


        assetsNames_ = []
        assetsNames_.append(context.scene.asset.obj.name)

        #Check if collection name already exists and replace it
        newCollectionName = checkAndReplaceCollectioName(context, nameCollection, assetsNames_)
        if(newCollectionName is not None):
            nameCollection = newCollectionName

        collection = bpy.data.collections.get(nameCollection)
        collection = initCollection(collection, nameCollection)


        bpy.context.view_layer.objects.active = context.scene.target
        oldMode = context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.select_all(action='DESELECT')
        # #Scale asset if necessary
        scaleObject(self, asset)

        # #Get bounding box
        asset_bounding_box_local = getBoundingBox(context, asset)
        target_bounding_box_local = getBoundingBox(context, target)


        #Get objects from list.
        partialSol = []

        for i in range(len(context.scene.partialsol)):
            obj = context.scene.partialsol[i]
            partialSol.append(obj)

        # Bounding info
        # for i in range(len(asset_bounding_box_local)):
        #     print('Vértice ', i,'(x, y, z): ', asset_bounding_box_local[i])
        
        # #Subdivide target to fit assets in every vertex
        if (context.scene.subdivide):
            makeSubdivision(target, asset_bounding_box_local, target_bounding_box_local, numCutsSubdivision)

        data_tridimensional = getVerticesData(target, context.scene.vgr_profile)
        print('Algorithm:', context.scene.algorithm_enum)

        vertices = filterVerticesByWeightThreshold(
            data_tridimensional, threshold_weight)
        
        if(len(vertices)  == 0):
            self.report({'WARNING'}, 'No vertex to place objects! Have you Painted Weight?')
            return {'FINISHED'}
        
        #Initial state as all possible vertices to place an asset

        if context.scene.solution_nodes == []:
            self.report({'INFO'}, "Solution nodes empty, rellenating")

            #Initial state 
            initialState = StateDistribution(vertices, len(context.scene.partialsol))
            num_assets = min(num_instances, len(vertices))

            #Potential final state 
            goalState = StateDistribution(None, num_assets)

            # Establishes rules for the assets in order to place them correctly
            rules = setPanelItemRules(context)
            distribution = ThresholdRandDistribution(rules, asset_bounding_box_local, initialState, goalState)    
            #distribution = Demo_Over_Dist_RotRang_Distribution(rules, initialState, goalState)
            for i in range(context.scene.num_searches):
                print("Solution: ", i)
                context.scene.solution_nodes.append(aimaBFTS(distribution))

            change_search(self, context, context.scene.solution_nodes[context.scene.current_search-1], vertices, asset, asset_bounding_box_local, collection, target)

        bpy.ops.object.mode_set(mode=oldMode, toggle=False)

        return {'FINISHED'}
            
    # static method
    @classmethod
    def poll(cls, context):
        # active object
        obj = context.object
        return (obj is not None) and ((obj.mode == "OBJECT") or (obj.mode == "WEIGHT_PAINT"))

