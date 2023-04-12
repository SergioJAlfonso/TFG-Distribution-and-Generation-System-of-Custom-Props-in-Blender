import bpy 
from ...utilsSS.blender_utils import *

class PaintMode_OT_Operator(bpy.types.Operator):
    bl_idname = "addon.enter_paint_mode"
    bl_label = "Simple operator"
    bl_description = "Switch to weight vertex painting mode."

    def execute(self, context):
        if(len(context.scene.target.vertex_groups) < 1):
            bpy.ops.addon.vertex_profile_add('INVOKE_DEFAULT')

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        bpy.ops.object.select_all(action='DESELECT')
        #Change any selected object to Target object so it can be switched to weight painting. 
        bpy.context.view_layer.objects.active = context.scene.target

        bpy.ops.object.mode_set(mode='WEIGHT_PAINT', toggle=False)
        # bpy.ops.paint.weight_paint_toggle()
        return {'FINISHED'}

    # static method
    @classmethod
    def poll(cls, context):
        # active object
        obj = context.scene.target
        return (obj is not None) and (obj.mode == "OBJECT")
    
class ExitPaintMode_OT_Operator(bpy.types.Operator):
    bl_idname = "addon.exit_paint_mode"
    bl_label = "Simple operator"
    bl_description = "Switch to object mode."

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        return {'FINISHED'}

    # static method
    @classmethod
    def poll(cls, context):
        # active object
        obj = context.object
        return (obj is not None) and (obj.mode == "WEIGHT_PAINT")
    
class InvertPainting_OT_Operator(bpy.types.Operator):
    bl_idname = "addon.invert_painting"
    bl_label = "Simple operator"
    bl_description = "Invert current painting weight."

    def execute(self, context):
        bpy.ops.object.vertex_group_invert()
        return {'FINISHED'}

    # static method
    @classmethod
    def poll(cls, context):
        # active object
        obj = context.object
        return (obj is not None) and (obj.mode == "WEIGHT_PAINT")
    
class PaintAll_OT_Operator(bpy.types.Operator):
    bl_idname = "addon.paint_all"
    bl_label = "Simple operator"
    bl_description = "Assign same weight value to all vertices."

    def execute(self, context):
        # bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.editmode_toggle()
        bpy.data.scenes["Scene"].tool_settings.vertex_group_weight = context.scene.allWeightValue
        bpy.ops.object.vertex_group_assign()
        bpy.ops.paint.weight_paint_toggle()
        # bpy.ops.object.vertex_groups["Bosque"]
        return {'FINISHED'}

    # static method
    @classmethod
    def poll(cls, context):
        # active object
        obj = context.object
        return (obj is not None) and (obj.mode == "WEIGHT_PAINT")