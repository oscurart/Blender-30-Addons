import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


# ---------------------------BATCH MAKER------------------


def setRenderBorder(self):
    bpy.context.scene.render.use_border = True

    x = []
    y = []

    depsgraph = bpy.context.evaluated_depsgraph_get()

    bm = bmesh.new()#

    for ob in bpy.context.selected_objects:
        obMatrix = ob.matrix_world
        me = ob.evaluated_get(depsgraph).to_mesh()
        for v in me.vertices:
            v.co = obMatrix @ v.co
        bm.from_mesh(me)#

    bmesh.ops.convex_hull(bm,input=bm.verts)

    tmpMesh = bpy.data.meshes.new("helloBye")
    bm.to_mesh(tmpMesh)
    
    bm.free()#

    for v in tmpMesh.vertices:
        point = world_to_camera_view(bpy.context.scene, bpy.context.scene.camera, v.co  )
        x.append( point[0])
        y.append( point[1])
        
    bpy.context.scene.render.border_min_x = min(x)
    bpy.context.scene.render.border_max_x = max(x)
    bpy.context.scene.render.border_min_y = min(y)
    bpy.context.scene.render.border_max_y = max(y)

    bpy.data.meshes.remove(tmpMesh)


class oscSetRenderBorder (bpy.types.Operator):
    """Set a render border only for selected Objects"""
    bl_idname = "render.set_render_border"
    bl_label = "Set Render Border"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        setRenderBorder(self)
        return {'FINISHED'}

