import bpy
from bpy.types import Operator

def defcreateUvEdition(ob):
    for edge in ob.data.edges:
        edge.use_edge_sharp = edge.use_seam

    mod = ob.modifiers.new("split", "EDGE_SPLIT")
    mod.use_edge_angle = 0
    bpy.ops.object.modifier_apply(modifier="split")

    me = ob.data.copy()
    dob = bpy.data.objects.new("%s_edit" % (ob.name), me)
    bpy.context.layer_collection.collection.objects.link(dob)

    for loop in dob.data.loops:
        dob.data.vertices[loop.vertex_index].co = dob.data.uv_layers.active.data[loop.index].uv[:] + (
            1,)


def defcopyUvEdition(ob):
    if ob.name.count("_edit"):
        dob = bpy.context.object
        ob = bpy.data.objects[dob.name.removesuffix("_edit")]

        for dloop, loop in zip(dob.data.loops, ob.data.loops):
            ob.data.uv_layers.active.data[loop.index].uv = dob.data.vertices[loop.vertex_index].co[:2]

        for edge in ob.data.edges:
            edge.use_edge_sharp = 0
    else:
        print("select _edit mesh")        
        


class createUvEdition(Operator):
    """It creates a new mesh for uv edition in 3d area"""
    bl_idname = "mesh.create_uv_edition"
    bl_label = "Create UV Mesh Edition"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH' and
                context.view_layer.objects.active.mode == "OBJECT")

    def execute(self, context):
        defcreateUvEdition( bpy.context.object)
        return {'FINISHED'}

class copyUvEdition(Operator):
    """It copies the uv to original mesh"""
    bl_idname = "mesh.restore_uv_edition"
    bl_label = "Restore UV Mesh Edition"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH' and
                context.view_layer.objects.active.mode == "OBJECT")

    def execute(self, context):
        defcopyUvEdition( bpy.context.object)
        return {'FINISHED'}