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

def getOrder():
    bm = bmesh.from_edit_mesh(bpy.context.object.data)
    selEdges = [edge for edge in bm.edges if edge.select]
    #lista de vertices y edges 
    connections = {}
    for edge in selEdges:
        for vert in edge.verts:
            connections.setdefault(vert.index,[]).append(edge.index)
    #creo vertice inicial de punta
    for vert, edgelist in connections.items():
        if len(edgelist) == 1:
            startVert = vert
            break
    order = [startVert]
    for i in range(len(selEdges)):
        tempVal = connections[startVert][0]
        connections.pop(startVert)
        for vert, edgelist in connections.items():
            if tempVal in edgelist:        
                order.append(vert)
                startVert = vert
                connections[vert].remove(tempVal)
                break    
    bm.select_flush_mode()                
    return(order)            


def alignVerts(self,context):
	# mesh     
	LoopOrder = getOrder()
	bm = bmesh.from_edit_mesh(bpy.context.object.data)
	percents = []
	total = 0
	difTipEnd = bm.verts[LoopOrder[-1]].co - bm.verts[LoopOrder[0]].co

	prevPercent = 0
	for segment in range(len(LoopOrder)-1):
	    dif = (bm.verts[LoopOrder[segment+1]].co - bm.verts[LoopOrder[segment]].co).length
	    percent = dif  /difTipEnd.length 
	    bm.verts[LoopOrder[segment+1]].co = difTipEnd * (percent+prevPercent) + bm.verts[LoopOrder[0]].co
	    prevPercent += percent


	bmesh.update_edit_mesh(bpy.context.object.data)



class alignVertices(bpy.types.Operator):
    bl_idname = "mesh.align_vertices"
    bl_label = "Align Vertices"
    bl_description = ("Align vertices keeping distances")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None

    def execute(self, context):
        alignVerts(self, context)
        return {'FINISHED'}
