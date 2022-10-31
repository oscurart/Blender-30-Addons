bl_info = {
    "name": "Edit Hair Curves",
    "author": "Oscurart",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Add > Mesh > Add",
    "description": "Adds a Mesh to edit Hair Curves",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy.types import Operator


def add_edit_curves_mesh(self, context):
    vi = 0
    edgelist = []
    vertlist = []
    for stroke in bpy.context.object.data.curves:        
        for p in stroke.points:
            vertlist.append(p.position)         
        cantPuntos= len(stroke.points)-1            
        for a in range(0,cantPuntos):
            edgelist.append((vi,vi+1))
            vi = vi+1
        vi += 1 
    me = bpy.data.meshes.new("data")
    gpdb = bpy.data.objects.new("%s_Edit" % (bpy.context.object.name), me)
    me.from_pydata(vertlist,edgelist,[])
    me.update()
    bpy.context.scene.collection.objects.link(gpdb)

def apply_curves_mesh(self, context):
    target = bpy.data.objects[bpy.context.object.name.replace("_Edit","")]
    editCurves = bpy.context.object
    for ep,tp in zip(target.data.points,editCurves.data.vertices):
        ep.position = tp.co



class OBJECT_OT_add_curves_editor(Operator):
    """Create curves editor"""
    bl_idname = "mesh.curves_editor"
    bl_label = "Add Mesh Curves Editor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        add_edit_curves_mesh(self, context)

        return {'FINISHED'}
    
    
class OBJECT_OT_apply_curves_edit(Operator):
    """Apply Curves edit"""
    bl_idname = "mesh.apply_curves_edit"
    bl_label = "Apply Curves Edit"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        apply_curves_mesh(self, context)

        return {'FINISHED'}    
    
    


# Registration

def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_curves_editor.bl_idname,
        text="Add Mesh Curves Editor",
        icon='PLUGIN')
    self.layout.operator(
        OBJECT_OT_apply_curves_edit.bl_idname,
        text="Apply Mesh Curves Editor",
        icon='PLUGIN')

def register():
    bpy.utils.register_class(OBJECT_OT_add_curves_editor)
    bpy.utils.register_class(OBJECT_OT_apply_curves_edit)    
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)



def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_curves_editor)
    bpy.utils.unregister_class(OBJECT_OT_apply_curves_edit)      
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)



if __name__ == "__main__":
    register()
