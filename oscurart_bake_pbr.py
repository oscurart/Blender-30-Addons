from datetime import datetime
import os
import bpy
from mathutils import Vector

bl_info = {
    "name": "Bake PBR",
    "author": "Eugenio Pignataro (Oscurart)",
    "version": (1, 3),
    "blender": (3, 00, 0),
    "location": "Render > Bake PBR",
    "description": "Bake PBR maps",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
}


# check IMAGES folder and creates it.
def folderCheck():
    fp = bpy.path.abspath(bpy.data.filepath)
    dirFile = os.path.dirname(fp)
    imagesFile = os.path.join(dirFile, "IMAGES")

    if not os.path.exists(imagesFile):
        os.mkdir(imagesFile)

# Set EXR in scene
def setExr():
    bpy.context.scene.render.image_settings.file_format = "OPEN_EXR"
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.image_settings.exr_codec = "ZIP"
    bpy.context.scene.render.image_settings.color_depth = "16"    

# Set PNG format    
def setPng():
    bpy.context.scene.render.image_settings.file_format = "PNG"   
    bpy.context.scene.render.image_settings.color_mode = "RGBA"
    bpy.context.scene.render.image_settings.color_depth = "8"       

def setSceneOpts():
    global channels
    global channelsDict
    global sizex
    global sizey
    global selected_to_active
    global UDIMS

    # VARIABLES
    sizex = bpy.context.scene.bake_pbr_channels.sizex
    sizey = bpy.context.scene.bake_pbr_channels.sizey
    pngCopy = bpy.context.scene.bake_pbr_channels.use_pngcopy
    deleteExr = bpy.context.scene.bake_pbr_channels.delete_exr
    selected_to_active = bpy.context.scene.bake_pbr_channels.seltoact
    UDIMS = bpy.context.scene.bake_pbr_channels.UDIMS

    channelsDict = {
        "Base_Color": [True],
        "Metallic": [False],
        "Roughness": [False],
        "Specular": [False],
        "Specular_Tint": [False],
        "Subsurface": [False],
        "Subsurface_Color": [True],
        "Subsurface_Radius": [True],
        "Sheen": [False],
        "Sheen_Tint": [False],
        "Clearcoat" : [False],
        "Clearcoat_Roughness" : [False],
        "Transmission_Weight": [False],
        "IOR": [False],
        "Emission": [True],
        "Normal": [True],
        "Alpha": [False],
    }

    setExr() #set exr format

    # set bake options
    #bpy.context.scene.render.bake_type = "TEXTURE"
    bpy.context.scene.render.bake.use_pass_direct = 0
    bpy.context.scene.render.bake.use_pass_indirect = 0
    bpy.context.scene.render.bake.use_pass_color = 1
    bpy.context.scene.render.bake.use_selected_to_active = selected_to_active

# __________________________________________________________________________________


# CHECKING INICIAL

def inicialChecking():
    status = 0
    
    #if selection is none
    if len(bpy.context.selected_objects) == 0:
        if bpy.context.scene.bake_pbr_channels.seltoact:
            print ( "You need select 2 objects at least." ) 
            status =1        
        else:  
            print ( "you need select 1 objects at least." ) 
            status = 1
    
    
    for ob in bpy.context.selected_objects:
        # check material exists and principled
        if len(ob.material_slots) > 0:
            for ms in ob.material_slots:
                if ms.material != None:
                     try:
                        ms.material.node_tree.nodes['Material Output'].inputs[0].links[0].from_node.type == "BSDF_PRINCIPLED"
                     except:
                         print("%s does not have principled." % (ms.material.name))  
                         status =1  
                else:
                    print("%s has empty material slot." % (ob.name))  
                    status = 1                    
                                         
        else:
            print("%s has not material." % (ob.name)) 
            status =1     
        
        #check if selection is ok
        if bpy.context.scene.bake_pbr_channels.seltoact:
            if len(bpy.context.selected_objects) < 2:
                print ( "You need select 2 objects at least.") 
                status =1  

    return (status)                              
            
            
# __________________________________________________________________________________            
            
            
#  MERGE OBJECTS
def mergeObjects():
    global selectedObjects
    global object
    global selObject
    global mergeMatSlots
    
    # Make selected and active groups
    object = bpy.context.active_object
    selectedObjects = bpy.context.selected_objects[:].copy()
    selectedObjects.remove(bpy.context.active_object)

    # if it is selected to active it makes a merge
    if selected_to_active:
        obInScene = bpy.data.objects[:].copy()
        bpy.ops.object.select_all(action="DESELECT")
        for o in selectedObjects:
            o.select_set(state=True)
        bpy.context.view_layer.objects.active = selectedObjects[0]
        bpy.ops.object.convert(target="MESH", keep_original=True)
        bpy.ops.object.select_all(action="DESELECT")
        for ob in bpy.data.objects:
            if ob not in obInScene:
                ob.select_set(True)
        selObject = bpy.context.active_object
        bpy.ops.object.join()
        bpy.ops.object.transform_apply(
            location=True,
            rotation=True,
            scale=True,
            properties=True)
    else:
        selObject = bpy.context.active_object

    # seteo el objeto activo
    bpy.context.view_layer.objects.active = object

    # materiales en slot de objeto mergeado
    mergeMatSlots = [ms.material for ms in selObject.material_slots]


# __________________________________________________________________________________


# TEMPORARY MATERIALS FOR EACH CHANNEL

def createTempMats():
    global channelVector
    global selObject
    materiales = [m.material for m in selObject.material_slots]
    # compruebo los canales prendidos
    for channel, channelVector in channelsDict.items():
        # todo lo que no sea normales
        if channel not in ["Normal", "Emission"]:
            if getattr(bpy.context.scene.bake_pbr_channels, channel):
                for mat in materiales:
                    channelMat = mat.copy()
                    channelMat.name = "%s_%s" % (channel, mat.name)
                    principleds = [
                        node.inputs[0].links[0].from_socket.node for node in channelMat.node_tree.nodes if node.type == "OUTPUT_MATERIAL"]
                    mixs = [
                        node for node in channelMat.node_tree.nodes if node.type == "MIX_SHADER"]

                    # apago emisores
                    for node in channelMat.node_tree.nodes:
                        if node.type == "EMISSION":
                            node.inputs[1].default_value = 0

                    # conecta los valores a los mix
                    for prin in principleds:
                        if prin.inputs[channel.replace("_", " ")].is_linked:
                            channelMat.node_tree.links.new(
                                prin.outputs['BSDF'].links[0].to_socket, prin.inputs[channel.replace("_", " ")].links[0].from_socket)
                        else:
                            inputRGB = channelMat.node_tree.nodes.new(
                                "ShaderNodeRGB")
                            channelMat.node_tree.links.new(
                                prin.outputs['BSDF'].links[0].to_socket, inputRGB.outputs[0])
                            if channelVector[0]:  # si es float o un vector
                                if len(prin.inputs[channel.replace(
                                        "_", " ")].default_value) == 4:  # si es color o vector de 3 componentes
                                    inputRGB.outputs[0].default_value = prin.inputs[channel.replace(
                                        "_", " ")].default_value
                                else:
                                    inputRGB.outputs[0].default_value = prin.inputs[channel.replace(
                                        "_", " ")].default_value[:] + (1,)
                            else:
                                rgbValue = prin.inputs[channel.replace("_"," ")].default_value
                                inputRGB.outputs[0].default_value = (
                                    rgbValue, rgbValue, rgbValue, 1)
        # normal
        if channel in ["Normal", "Emission"]:
            if getattr(bpy.context.scene.bake_pbr_channels, channel):
                for mat in materiales:
                    channelMat = mat.copy()
                    channelMat.name = "%s_%s" % (channel, mat.name)


# __________________________________________________________________________________


def cambiaSlots(selObject, canal):
    for actualMs, originalMs in zip(selObject.material_slots, mergeMatSlots):
        actualMs.material = bpy.data.materials["%s_%s" % (
            canal, originalMs.name)]


def restauraSlots(selObject):
    for actualMs, originalMs in zip(selObject.material_slots, mergeMatSlots):
        actualMs.material = bpy.data.materials[originalMs.name]

# __________________________________________________________________________________


def bake(map, frame, udim):
    # time
    start_time = datetime.now()

    # paso a cycles
    bpy.context.scene.render.engine = "CYCLES"

    # crea imagen
    imgpath = "%s/IMAGES" % (os.path.dirname(bpy.data.filepath))
    img = bpy.data.images.new(
        map,
        width=sizex,
        height=sizey,
        alpha=True,
        float_buffer=True)
    print("Render: %s" % (map))
    img.colorspace_settings.name = 'Linear Rec.709'

    if not selected_to_active:
        img.filepath = "%s/%s_%s%s.exr" % (imgpath,
                                           object.name,
                                           map.replace(
                                               "_",
                                               ""),
                                           "%04d" % (frame) if getattr(
                                               bpy.context.scene.bake_pbr_channels,
                                               "sequence") else "")
    else:
        img.filepath = "%s/%s_%s%s.exr" % (imgpath,
                                           object.active_material.name,
                                           map.replace(
                                               "_",
                                               ""),
                                           "%04d" % (frame) if getattr(
                                               bpy.context.scene.bake_pbr_channels,
                                               "sequence") else "")


    #UDIM
    if bpy.context.scene.bake_pbr_channels.UDIMS != "":
        img.filepath = img.filepath.replace(".","_%s." % (udim))
    
    
    
    # cambio todos los slots por el del canal
    cambiaSlots(selObject, map)

    # creo nodos y bakeo
    if not selected_to_active:
        for activeMat in selObject.data.materials:  # aca estaba el mscopy
            # seteo el nodo
            node = activeMat.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = img
            activeMat.node_tree.nodes.active = node
            #node.image.colorspace_settings.name = "Non-Colour Data"
            node.select = True
            node.name = "BakePBRTemp"
    else:
        activeMat = object.active_material
        # seteo el nodo
        node = activeMat.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = img
        activeMat.node_tree.nodes.active = node
        #node.image.colorspace_settings.name = "Non-Colour Data"
        node.select = True
        node.name = "BakePBRTemp"

    if map not in ["Normal"]:
        bpy.ops.object.bake(type="EMIT")
    else:
        bpy.ops.object.bake(type="NORMAL")
    img.save_render(img.filepath)
    
    # save png copy
    if bpy.context.scene.bake_pbr_channels.use_pngcopy:
        setPng()    
        oimg = bpy.data.images.load(img.filepath)    
        if  any(ColorChan in oimg.filepath for ColorChan in ["Color","Emission"]) :
            oimg.colorspace_settings.name="Linear Rec.709"
        else:

            oimg.colorspace_settings.name="sRGB"#OfficialLuts 
    
        vt=bpy.context.scene.view_settings.view_transform #save viewtransform
        vLook=bpy.context.scene.view_settings.look

        bpy.context.scene.view_settings.view_transform = "Standard"  #OfficialLuts  
         
        bpy.context.scene.view_settings.look="None"                 
        oimg.save_render(oimg.filepath.replace("exr","png")) #save png  
        #restore color management
        bpy.context.scene.view_settings.view_transform = vt
        bpy.context.scene.view_settings.look = vLook 
        #cleanup
        bpy.data.images.remove(oimg)     
        setExr()
        
        
    #delete exr    
    if bpy.context.scene.bake_pbr_channels.delete_exr:
        os.remove(img.filepath)
    
    #clearimage
    bpy.data.images.remove(img)
    print("%s Done!" % (map))

    for node in activeMat.node_tree.nodes:
        if node.name.count("BakePBRTemp"):
            activeMat.node_tree.nodes.remove(node)

    restauraSlots(selObject)

    # fin tiempo
    time_elapsed = datetime.now() - start_time
    print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

    


# __________________________________________________________________________________
# UDIMS

def offsetUdims(bakerestore,udim):

    horizontal =(int(udim[-1])-1) * bakerestore
    vertical = int(udim[-2]) * bakerestore
    offset = Vector((horizontal,vertical))
    # use object like a global name
    for vcorn in  object.data.uv_layers.active.uv:
        vcorn.vector += offset    


# __________________________________________________________________________________

def executePbr():
    
    engine = bpy.context.scene.render.engine
    vtr = bpy.context.scene.view_settings.view_transform
    look = bpy.context.scene.view_settings.look
    try:    
        bpy.context.scene.view_settings.view_transform = "Linear Raw"
    except:
        bpy.context.scene.view_settings.view_transform = "Raw"    
    bpy.context.scene.view_settings.look = "None"

    # bakeo
    folderCheck()
    setSceneOpts()
    mergeObjects()
    createTempMats()
       

    for map in channelsDict.keys():
        if getattr(bpy.context.scene.bake_pbr_channels, map):
            if getattr(bpy.context.scene.bake_pbr_channels, "sequence"):
                for frameNumber in range(
                        bpy.context.scene.frame_start,
                        bpy.context.scene.frame_end + 1):
                    bpy.context.scene.frame_set(frameNumber)
                    bake(map, frameNumber,"")
            else:
                if UDIMS == "":
                    bake(map, "", "")
                else:
                    for UDIM in bpy.context.scene.bake_pbr_channels['UDIMS'].split(","):
                        offsetUdims(-1,UDIM) #UDIMS  OFFSET   
                        bake(map, "", UDIM)
                        offsetUdims(1,UDIM)#UDIMS RESTORE
                    
    # remuevo materiales copia
    for ma in bpy.data.materials:
        if ma.users == 0:
            bpy.data.materials.remove(ma)

    # borro el merge
    if selected_to_active:
        bpy.data.objects.remove(
            selObject,
            do_unlink=True,
            do_id_user=True,
            do_ui_user=True)
    
    bpy.context.scene.render.engine = engine
    bpy.context.scene.view_settings.view_transform = vtr
    bpy.context.scene.view_settings.look = look

class BakePbr (bpy.types.Operator):
    """Bake PBR materials"""
    bl_idname = "object.bake_pbr_maps"
    bl_label = "Bake PBR Maps"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):        
        
        #inicial checking , if initial checking is ok let you continue
        if  inicialChecking()  ==  0 :    
            executePbr()      
        else:            
            self.report({'WARNING'}, "ERROR, check console")
        return {'FINISHED'}


# __________________________________________________________________________________


class bakeChannels(bpy.types.PropertyGroup):
    Base_Color: bpy.props.BoolProperty(name="Base Color", default=False)
    Metallic: bpy.props.BoolProperty(name="Metallic", default=False)
    Roughness: bpy.props.BoolProperty(name="Roughness", default=False)
    Specular: bpy.props.BoolProperty(name="Specular", default=False)
    Specular_Tint: bpy.props.BoolProperty(name="Specular Tint", default=False)
    Subsurface: bpy.props.BoolProperty(name="Subsurface", default=False)
    Subsurface_Color: bpy.props.BoolProperty(
        name="Subsurface Color", default=False)
    Subsurface_Radius: bpy.props.BoolProperty(
        name="Subsurface Radius", default=False)
    Sheen: bpy.props.BoolProperty(name="Sheen", default=False)  
    Sheen_Tint: bpy.props.BoolProperty(name="Sheen Tint", default=False)   
    Clearcoat : bpy.props.BoolProperty(name="Clearcoat", default=False) 
    Clearcoat_Roughness : bpy.props.BoolProperty(name="Clearcoat Roughness", default=False) 
    Transmission_Weight: bpy.props.BoolProperty(name="Transmission Weight", default=False)
    IOR: bpy.props.BoolProperty(name="IOR", default=False)
    Emission: bpy.props.BoolProperty(name="Emission", default=False)
    Normal: bpy.props.BoolProperty(name="Normal", default=False)
    Alpha: bpy.props.BoolProperty(name="Alpha", default=False)
    sizex: bpy.props.IntProperty(name="Size x", default=1024)
    sizey: bpy.props.IntProperty(name="Size y", default=1024)
    seltoact: bpy.props.BoolProperty(name="Selected to active", default=True)
    use_pngcopy: bpy.props.BoolProperty(name="Get a png copy", default=True)    
    delete_exr: bpy.props.BoolProperty(name="Delete EXR at finish", default=False)   
    sequence: bpy.props.BoolProperty(name="Render sequence", default=False)
    UDIMS: bpy.props.StringProperty(name="UDIMS", default="")

bpy.utils.register_class(bakeChannels)


class OSCPBR_PT_LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Bake PBR"
    bl_idname = "RENDER_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    """
    @classmethod
    def poll(cls, context):
        return bpy.context.scene.render.engine == "CYCLES"
    """

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Create a simple row.
        layout.label(text=" Channels:")

        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Base_Color")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Metallic")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Roughness")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Specular")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Specular_Tint")        
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Subsurface")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Subsurface_Color")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Subsurface_Radius")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Sheen")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Sheen_Tint") 
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Clearcoat") 
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Clearcoat_Roughness")                                
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Transmission_Weight")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "IOR")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Emission")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Normal")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "Alpha")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "UDIMS")        
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "sizex")
        row.prop(scene.bake_pbr_channels, "sizey")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "seltoact")
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "use_pngcopy")   
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "delete_exr")              
        row = layout.row()
        row.prop(scene.bake_pbr_channels, "sequence")
        # Big render button
        row = layout.row()
        row.scale_y = 2
        row.operator("object.bake_pbr_maps")


# ___________________ CARGA MATS


def loadPBRMaps():
    mat = bpy.context.object.material_slots[0].material
    activePrincipled = mat.node_tree.nodes.active
    imgpath = "%s/IMAGES" % (os.path.dirname(bpy.data.filepath))
    loc = activePrincipled.location[1]
    locx = activePrincipled.location[0] - 500
    principledInputs = [input.name for input in activePrincipled.inputs]
    principledInputs.append("Emission")

    for input in principledInputs:
        if os.path.exists(
            "%s/%s_%s.exr" %
            (imgpath,
             mat.name,
             input.replace(
                 " ",
                 ""))):
            print("Channel %s connected" % (input.replace(" ", "")))
            img = bpy.data.images.load(
                "%s/%s_%s.exr" %
                (imgpath, mat.name, input.replace(
                    " ", "")))
            imgNode = mat.node_tree.nodes.new("ShaderNodeTexImage")
            imgNode.image = img

            if input == "Normal":
                normalShader = mat.node_tree.nodes.new("ShaderNodeNormalMap")
                mat.node_tree.links.new(
                    normalShader.outputs[0],
                    activePrincipled.inputs["Normal"])
                mat.node_tree.links.new(
                    imgNode.outputs[0], normalShader.inputs[1])
                normalShader.location[0] = activePrincipled.location[0]
                normalShader.location[1] = activePrincipled.location[1] - 600
                imgNode.location[0] = activePrincipled.location[0]
                imgNode.location[1] = activePrincipled.location[1] - 900

            if input not in ["Normal"]:
                mat.node_tree.links.new(
                    imgNode.outputs[0], activePrincipled.inputs[input])
                imgNode.location[1] += loc
                imgNode.location[0] = locx
                loc -= 300


class loadPbrMaps (bpy.types.Operator):
    """Load bakePBR maps"""
    bl_idname = "material.load_pbr_maps"
    bl_label = "Load PBR Maps"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        loadPBRMaps()
        return {'FINISHED'}

# ---------------------------------------------------------------------------------


def register():
    bpy.types.Scene.bake_pbr_channels = bpy.props.PointerProperty(
        type=bakeChannels)
    bpy.utils.register_class(OSCPBR_PT_LayoutDemoPanel)
    bpy.utils.register_class(BakePbr)
    bpy.utils.register_class(loadPbrMaps)


def unregister():
    bpy.utils.unregister_class(OSCPBR_PT_LayoutDemoPanel)
    bpy.utils.unregister_class(BakePbr)
    bpy.utils.unregister_class(loadPbrMaps)


if __name__ == "__main__":
    register()
