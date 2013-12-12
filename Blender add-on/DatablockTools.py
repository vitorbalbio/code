bl_info = {
    "name": "Datablock Tools",
    "author": "Vitor Balbio",
    "version": (1, 1),
    "blender": (2, 69, 0),
    "location": "View3D > Object > Datablock Tools",
    "description": "Some tools to handle Datablocks ",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/3D_interaction/Datablock_Tools",
    "tracker_url": "",
    "category": "3D View"}
	
import bpy
import os

def CleanImages():
    # Clean Derivative Images
    # para cada objeto selecionado, para cada face verifica se a textura ( com nome já tratado
    # para remover a extensao se necessario) possui "." então busca na lista de imagens a image
    # original e aplica
    
    ImageList = []
    # se o ultimo caracter nao for numero entao remove os ultimos 3 caracteres (formato da imagem)"
    for i in bpy.data.images:
        try:
            a = int(i.name[-1])
            imagename = i.name
        except ValueError:
            imagename, a = os.path.splitext(i.name)
       
        ImageList.append([imagename,i])
    
    
    for obj in bpy.context.selected_objects:
        for uv in obj.data.uv_textures.items():
            for faceTex in uv[1].data:
                image = faceTex.image          
                # se o ultimo caracter nao for numero entao remove os ultimos 3 caracteres (formato da imagem)"
                try:
                    a = int(image.name[-1])
                    imagename = image.name
                except ValueError:
                    imagename, a = os.path.splitext(image.name)
    
                if( ".0" in imagename):
                    for ima_name, ima in ImageList:
                        if((ima_name in imagename) and (".0" not in ima_name)):
                            faceTex.image.user_clear()
                            faceTex.image = ima


class CleanImagesOP(bpy.types.Operator):
    """Replace the ".0x" images with the original and mark this to remove in next load"""
    bl_idname = "object.clean_images"
    bl_label = "Clean Images Datablock"

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        
        CleanImages()
        return {'FINISHED'}
    
    
def CleanMaterials():
    # Clean Derivative Materials 
    # para cada objeto da cena se ele tiver um material que contenha "." entao busca na lista
    # de materiais o material original e aplica
    
    matlist = bpy.data.materials
    for obj in bpy.context.selected_objects:
        for mat_slt in obj.material_slots:
            if(mat_slt.material != None): # se não tiver material associado
                if( ".0" in mat_slt.material.name):
                    for mat in matlist:
                        if((mat.name in mat_slt.material.name) and ("." not in  mat.name)):
                            mat_slt.material = mat


class CleanMaterialsOP(bpy.types.Operator):
    """Replace the ".0x" materials with the original and mark this to remove in next load"""
    bl_idname = "object.clean_materials"
    bl_label = "Clean Materials Datablock"

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        CleanMaterials()
        return {'FINISHED'}

class SetInstanceOP(bpy.types.Operator):
    """Set all Seletect Objects as instance of Active Object"""
    bl_idname = "object.set_instance"
    bl_label = "Set as Instance"
    
    @classmethod
    def poll(cls, context):
        return ((context.selected_objects is not None) and (context.active_object is not None))
    
    def execute(self, context):
        active_obj = bpy.context.active_object
        for sel_obj in bpy.context.selected_objects:
            sel_obj.data = active_obj.data
        return {'FINISHED'}

class DatablockToolsMenu(bpy.types.Menu):
    bl_label = "Datablock Tools"
    bl_idname = "VIEW_MT_datablock_tools"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.clean_images")
        layout.operator("object.clean_materials")
        layout.operator("object.set_instance")


def draw_item(self, context):
    layout = self.layout
    layout.menu(DatablockToolsMenu.bl_idname)


def register():
    bpy.utils.register_class(CleanImagesOP)
    bpy.utils.register_class(CleanMaterialsOP)
    bpy.utils.register_class(SetInstanceOP)
    bpy.utils.register_class(DatablockToolsMenu)

    # lets add ourselves to the main header
    bpy.types.VIEW3D_MT_object.append(draw_item)


def unregister():
    bpy.utils.register_class(CleanImagesOP)
    bpy.utils.unregister_class(CleanMaterialsOP)
    bpy.utils.unregister_class(SetInstanceOP)
    bpy.utils.unregister_class(DatablockToolsMenu)

    bpy.types.VIEW3D_MT_object.remove(draw_item)


if __name__ == "__main__":
    register()