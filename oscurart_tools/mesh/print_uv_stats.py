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



import bpy
import bmesh
from mathutils.geometry import area_tri
from math import sqrt
from math import pow




def createMixedMesh():
    global PTM
    PTM = bpy.data.meshes.new("printTestTmp")    
    obs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    bm = bmesh.new()
    for o in obs:
        bm.from_mesh(o.data) 
        
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm_tess = bpy.data.meshes.new("Tris")    
    
    bm.to_mesh(PTM)    
        

def setImageRes(object):
    global pixels
    mat = bpy.context.object.data.materials[0]
    if  mat.node_tree.nodes.active.type in ["TEX_IMAGE"]:
        pixels = [mat.node_tree.nodes.active.image.size[0] ,mat.node_tree.nodes.active.image.size[1] ]
        return(True)

    else:
        print("Please select image node first")
        return(False)




def calcArea():
    global totalArea
    totalArea = 0
    for poly in PTM.polygons:
        uno = PTM.uv_layers.active.data[poly.loop_indices[0]].uv
        dos = PTM.uv_layers.active.data[poly.loop_indices[1]].uv
        tres = PTM.uv_layers.active.data[poly.loop_indices[2]].uv
        area = area_tri(uno, dos, tres)
        totalArea += area



def calcMeshArea():
    global GlobLog
    polyArea = 0
    for poly in PTM.polygons:
        polyArea += poly.area
    ta = "UvGain: %s%s || " % (round(totalArea * 100),"%")
    ma = "MeshArea: %s || " % (polyArea)
    pg = "PixelsGain: %s || " % (round(totalArea * (pixels[0] * pixels[1])))
    pl = "PixelsLost: %s || " % ((pixels[0]*pixels[1]) - round(totalArea * (pixels[0] * pixels[1])))
    tx = "Texel: %s pix/meter" % (round(sqrt(totalArea * pixels[0] * pixels[1] / polyArea)))
    GlobLog = ta+ma+pg+pl+tx



def cleanPrintMeshes():
    bpy.data.meshes.remove(
        PTM,
        do_unlink=True,
        do_id_user=True,
        do_ui_user=True)
  

class uvStats(bpy.types.Operator):
    """Print Uv Stats"""
    bl_idname = "mesh.print_uv_stats"
    bl_label = "Print Uv Stats"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if setImageRes(bpy.context.object):    
            createMixedMesh()        
            calcArea()
            calcMeshArea()

        cleanPrintMeshes()

        self.report({'INFO'}, GlobLog)
        

        return {'FINISHED'}

