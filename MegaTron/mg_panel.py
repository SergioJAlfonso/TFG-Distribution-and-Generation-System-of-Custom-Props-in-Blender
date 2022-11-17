import bpy

#definimos que lo que queremos seleccionar(target de la escena) es de tipo Object
bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)
bpy.types.Scene.asset = bpy.props.PointerProperty(type=bpy.types.Object)

        #_PT_Panel ->Convention
class Main_PT_Panel(bpy.types.Panel):
    bl_idname = "Main_PT_Panel"
    bl_label = "Object To Distribute"
    bl_category = "MegaTron"
    bl_description = "Entry Data Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = layout.column()
        box = layout.box()
        
        row.operator('addon.distribute', text = "Distribute")
        row.operator('addon.clear', text = "Clear")
        col.prop(context.scene, "algorithm_enum")


        box.label(text="Subdivision")

        box.row().prop(context.scene, "subdivide")
        box.row().prop(context.scene, "num_cuts")

        col.prop(context.scene, "threshold")
        col.prop(context.scene, "num_assets")
        col.prop(context.scene, "collectName")


        self.layout.prop_search(context.scene, "asset", context.scene, "objects", text="Asset")
        self.layout.prop_search(context.scene, "target", context.scene, "objects", text="Target Object")
        # placeholder = context.scene.placeholder
        # col.prop(placeholder, "inc_dec_int", text="Asset Instances")

class Groups_PT_Panel(bpy.types.Panel):
    bl_idname = "Groups_PT_Panel"
    bl_label = "Object Distribution"
    bl_category = "MegaTron"
    bl_description = "Groups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
    