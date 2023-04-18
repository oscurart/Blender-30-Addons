# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import bmesh
import json
import os
from mathutils import Vector


def SaveSym(self, context):
    C = bpy.context
    bpy.context.scene.tool_settings.use_uv_select_sync = True
    me = bpy.context.object.data
    bm = bmesh.from_edit_mesh(me)
    vertices = [vert.index for vert in bm.verts if vert.select]
    vertList = {}

    for index in vertices:
        #ivert = vert.index
        bpy.ops.mesh.select_all(action="DESELECT")    
        bm.verts[index].select = True
        bpy.ops.mesh.select_mirror()
        mirrorVert = [mirrorvert.index for mirrorvert in bm.verts if mirrorvert.select][0]
        vertList[mirrorVert] = index

 
    file = os.path.basename(bpy.data.filepath)
    file = file.rpartition(".")[0]

    directorio = "%s/%s.txt" % (os.path.dirname(bpy.data.filepath),C.object.name)

    with open(directorio, 'w') as f:
        f.writelines(str(vertList))


def RestoreSym(self, context):
    invert = (-1,1,1)
    C = bpy.context
    directorio = "%s/%s.txt" % (os.path.dirname(bpy.data.filepath),C.object.name)

    with open(directorio, 'r') as f:
        diccionario = f.readline()
        
    vertList = eval(diccionario)
    me = C.object.data
    bm = bmesh.from_edit_mesh(me)

    for vert in bm.verts:
        if vert.select:
            if vert.index in vertList.keys():  
                print(vert.index)
                vert.co = bm.verts[vertList[vert.index]].co * Vector((-1,1,1))
    
    bmesh.update_edit_mesh(me)    
        

class SaveSymmetry(bpy.types.Operator):
    """Save Symmetry"""
    bl_idname = "mesh.save_symmetry"
    bl_label = "Save Symmetry"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH' and
                context.view_layer.objects.active.mode == "EDIT")


    def execute(self, context):
        SaveSym(self, context)
        return {'FINISHED'}


class RestoreSymmetry(bpy.types.Operator):
    """Restore Symmetry"""
    bl_idname = "mesh.restore_symmetry"
    bl_label = "Restore Symmetry"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH' and
                context.view_layer.objects.active.mode == "EDIT")


    def execute(self, context):
        RestoreSym(self, context)
        return {'FINISHED'}
