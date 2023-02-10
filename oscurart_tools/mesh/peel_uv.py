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



def PeelUv(self, context):

    ob = bpy.context.object
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    selFaces = [face for face in bm.faces if face.select]

    for selFace in selFaces:    
        
        #deselect all         
        for poly in bm.faces:
            poly.select_set(False)    
        
        #active
        bm.faces.active = selFace
        selFace.select_set(True)    
        ob.data.update()
        
        edgeKeys = bm.faces.active.edges
        loopIndices = bm.faces.active.loops

        # guardo las posiciones de los vertices del poligono para calcular la proporcion
        uno = abs((edgeKeys[0].verts[0].co - edgeKeys[0].verts[1].co).length)
        dos = abs((edgeKeys[1].verts[0].co - edgeKeys[1].verts[1].co).length)
        tres = abs((edgeKeys[2].verts[0].co - edgeKeys[2].verts[1].co).length)
        cuatro = abs((edgeKeys[3].verts[0].co - edgeKeys[3].verts[1].co).length)

        proporcion = (uno + tres) / (dos + cuatro)

        #set positions
        uv_layer = bm.loops.layers.uv.active

        bm.faces.active.loops[0][uv_layer].uv = (0,0)
        bm.faces.active.loops[1][uv_layer].uv = (1,0)
        bm.faces.active.loops[2][uv_layer].uv = (1,1/proporcion)
        bm.faces.active.loops[3][uv_layer].uv = (0,1/proporcion)


        ob.data.update()

        #bpy.context.object.data.polygons.active = actPoly.index
        bpy.ops.mesh.select_linked(delimit={"SEAM"})
        bpy.ops.uv.follow_active_quads(mode="LENGTH_AVERAGE")
        bpy.ops.uv.pack_islands()

        

class PeelUnwrap(bpy.types.Operator):
    """Peel uv"""
    bl_idname = "mesh.peel_unwrap"
    bl_label = "Peel Unwrap"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (context.view_layer.objects.active is not None and
                context.view_layer.objects.active.type == 'MESH' and
                context.view_layer.objects.active.mode == "EDIT")


    def execute(self, context):
        PeelUv(self, context)
        return {'FINISHED'}
