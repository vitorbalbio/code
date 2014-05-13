bl_info = {
    "name": "BoolTool",
    "author": "Vitor Balbio",
    "version": (0, 1),
    "blender": (2, 70, 0),
    "location": "View3D > Object > BoolTool",
    "description": "Improve de Boolean Usability",
    "warning": "",
    "wiki_url": "",
    "category": "Object"}

import bpy
from bpy.app.handlers import persistent


#------------------- FUNCTIONS------------------------------

# Do the Basic Union, Difference and Intersection Operations
def Operation(context,_operation):
    for selObj in bpy.context.selected_objects:
        if selObj != context.active_object:            
            actObj = context.active_object
            
            cyclesVis = selObj.cycles_visibility
            for obj in bpy.context.scene.objects:
                try:
                    if obj["ToolBoolRoot"]:
                        for mod in obj.modifiers:
                            if(mod.name == "BTool_" + selObj.name):
                                obj.modifiers.remove(mod)
                except:
                    pass      

            selObj.draw_type = "BOUNDS"
            cyclesVis.camera = False; cyclesVis.diffuse = False; cyclesVis.glossy = False; cyclesVis.shadow = False; cyclesVis.transmission = False;
            newMod = actObj.modifiers.new("BTool_"+ selObj.name,"BOOLEAN")
            newMod.object = selObj
            newMod.operation = _operation
            actObj["ToolBoolRoot"] = True
            selObj["ToolBoolBrush"] = _operation
            

def Remove(context,thisObj):
    deleteList = []
    actObj = context.active_object
    
    print(thisObj)
    if thisObj != "":
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.name == thisObj:
                obj.select = True
    
    try:
        for SelObj in context.selected_objects:
            
            # Exclui um Brush da Lista diretamente
            if thisObj != "":
                bpy.ops.object.delete()
                return
            
            # Verifica todos os objetos selecionados e remove as configuracoes dele
            if SelObj["ToolBoolBrush"]:
                for obj in bpy.context.scene.objects:
                    try:
                        if obj["ToolBoolRoot"]:
                            for mod in obj.modifiers:
                                if(SelObj.name in mod.name):
                                    obj.modifiers.remove(mod)
                    except:
                        pass
                
                cyclesVis = SelObj.cycles_visibility
                SelObj.draw_type = "TEXTURED"
                del SelObj["ToolBoolBrush"]
                cyclesVis.camera = True; cyclesVis.diffuse = True; cyclesVis.glossy = True; cyclesVis.shadow = True; cyclesVis.transmission = True;
    except:
        pass
    
    try:
        if actObj["ToolBoolRoot"] and thisObj == "":
            for mod in actObj.modifiers:
                if("BTool_"in mod.name):
                    deleteList.append(mod.object)
            
            bpy.ops.object.select_all(action='DESELECT')
             
            for obj in deleteList:
                obj.select = True
            bpy.ops.object.delete()
    except:
        pass

def Apply(context):
    deleteList = []
    for selObj in bpy.context.selected_objects:
        try:
            if selObj["ToolBoolRoot"]:
                for mod in selObj.modifiers:
                    if("BTool_"in mod.name):
                        deleteList.append(mod.object)
                    bpy.ops.object.modifier_apply (modifier=mod.name)
                
                bpy.ops.object.select_all(action='TOGGLE')  
                bpy.ops.object.select_all(action='DESELECT')
                for obj in deleteList:
                    obj.select = True
                bpy.ops.object.delete()
                    
        except:
            pass

# Garbage Colletor

def GCollector(_obj):
    try:
        if _obj["ToolBoolRoot"]:
            pass
    except:
        return
    
    if _obj["ToolBoolRoot"]:
        BTRoot = False
        for mod in _obj.modifiers:
            if("BTool_" in mod.name):
                BTRoot = True
                if(mod.object == None):
                    _obj.modifiers.remove(mod)
        if not BTRoot:
            del _obj["ToolBoolRoot"]

# Handle the callbacks when modifing things in the scene
@persistent
def HandleScene(scene):
    if bpy.data.objects.is_updated:
        for ob in bpy.data.objects:
            if ob.is_updated:
                GCollector(ob)

#------------------- OPERATOR CLASSES ------------------------------                
# Boolean Union Operator                
class BooleanUnion(bpy.types.Operator):
    """This Operator Add a Object to Another with Boolean Operations"""
    bl_idname = "object.boolean_union"
    bl_label = "Union"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        Operation(context,"UNION")
        return {'FINISHED'}

# Boolean Intersection Operator
class BooleanInters(bpy.types.Operator):
    """This Operator Intersect a Object to Another with Boolean Operations"""
    bl_idname = "object.boolean_inters"
    bl_label = "Intersection"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Operation(context,"INTERSECT")
        return {'FINISHED'}
        
# Boolean Difference Operator
class BooleanDiff(bpy.types.Operator):
    """This Operator Add a Object to Another as a Boolean"""
    bl_idname = "object.boolean_diff"
    bl_label = "Difference"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Operation(context,"DIFFERENCE")
        return {'FINISHED'}

class BTool_FindBrush(bpy.types.Operator):
    """This Operator Add a Object to Another as a Boolean"""
    bl_idname = "btool.find_brush"
    bl_label = ""
    obj = bpy.props.StringProperty("")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        for ob in bpy.context.scene.objects:
            if(ob.name == self.obj):
                bpy.ops.object.select_all(action='TOGGLE')  
                bpy.ops.object.select_all(action='DESELECT')  
                bpy.context.scene.objects.active = ob
                ob.select = True
        return {'FINISHED'}

class BTool_MoveStack(bpy.types.Operator):
    """This Move this Brush Up/Down in the Stack"""
    bl_idname = "btool.move_stack"
    bl_label = ""
    modif = bpy.props.StringProperty("")
    direction = bpy.props.StringProperty("")
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        if(self.direction == "UP"):
            bpy.ops.object.modifier_move_up(modifier=self.modif)
        if(self.direction == "DOWN"):
            bpy.ops.object.modifier_move_down(modifier=self.modif)
        return {'FINISHED'}
    

class BTool_Remove(bpy.types.Operator):
    """This operator removes all ToolBool config assign to it"""
    bl_idname = "btool.remove"
    bl_label = ""
    thisObj = bpy.props.StringProperty("")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Remove(context,self.thisObj)
        return {'FINISHED'}
    
class BTool_ToMesh(bpy.types.Operator):
    """This operator removes all ToolBool config assign to it"""
    bl_idname = "btool.to_mesh"
    bl_label = "Apply To Mesh"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        Apply(context)
        return {'FINISHED'}


#------------------- MENU CLASSES ------------------------------  

class BooleanMenu(bpy.types.Menu):
    bl_label = "Boolean Operators"
    bl_idname = "OBJECT_MT_BooleanMenu"

    def draw(self, context):
        layout = self.layout

        self.layout.operator(BooleanUnion.bl_idname,icon = "ZOOMIN")
        self.layout.operator(BooleanDiff.bl_idname,icon = "ZOOMOUT")
        self.layout.operator(BooleanInters.bl_idname, icon = "PANEL_CLOSE")
        self.layout.separator()
        self.layout.operator(BTool_Remove.bl_idname,icon = "CANCEL")
        self.layout.operator(BTool_ToMesh.bl_idname,icon = "OBJECT_DATAMODE")

class BooleanTab(bpy.types.Panel):
    bl_label = "BoolTool"
    bl_idname = "ToolBoolTab"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "BoolTool"
    bl_context = "objectmode"
    
    def draw(self,context):
        self.layout.label("Operators:",icon = "MODIFIER")
        self.layout.operator(BooleanUnion.bl_idname,icon = "ZOOMIN")
        self.layout.operator(BooleanDiff.bl_idname,icon = "ZOOMOUT")
        self.layout.operator(BooleanInters.bl_idname, icon = "PANEL_CLOSE")
        self.layout.separator()
        Rem = self.layout.operator(BTool_Remove.bl_idname,icon = "CANCEL", text="Remove")
        Rem.thisObj = ""
        self.layout.operator(BTool_ToMesh.bl_idname,icon = "OBJECT_DATAMODE")
        
        self.layout.separator()        
    #---------- Tree Viewer--------------
        actObj = bpy.context.active_object
        icon = ""
              
        self.layout.label("Info:", icon = "INFO")
        try:
            contParam = self.layout.box()
            
            try:
                if actObj["ToolBoolRoot"]:
                    contParam.label("CANVAS", icon = "MESH_CUBE")
                    
            except:
                pass
            pass            
            
            if actObj["ToolBoolBrush"]:
                if(actObj["ToolBoolBrush"] == "UNION"):
                   icon ="ZOOMIN"
                if(actObj["ToolBoolBrush"] == "DIFFERENCE"):
                    icon ="ZOOMOUT"
                if(actObj["ToolBoolBrush"] == "INTERSECT"):
                    icon ="PANEL_CLOSE"
                
                contParam.label("BRUSH" ,icon = icon)
        except:
            try:
                if actObj["ToolBoolRoot"]:
                    pass
            except:
                pass
            pass

        try:
            if actObj["ToolBoolRoot"]:
                self.layout.separator()
                self.layout.label("Brushes:",icon = "GROUP")
                container = self.layout.box()
                
                for mod in actObj.modifiers:
                    row = container.row(True)
                    if("BTool_" in mod.name):
                        if(mod.operation == "UNION"):
                            icon ="ZOOMIN"
                        if(mod.operation == "DIFFERENCE"):
                            icon ="ZOOMOUT"
                        if(mod.operation == "INTERSECT"):
                            icon ="PANEL_CLOSE"

                        row.label(icon=icon)
                        row.label(text=mod.object.name)
                        objSelect = row.operator("btool.find_brush",icon ="HAND")
                        objSelect.obj = mod.object.name
                        
                        Delel = row.operator("btool.remove", icon="CANCEL")
                        Delel.thisObj = mod.object.name
                        
                        #Stack Changer
                        Up = row.operator("btool.move_stack",icon ="TRIA_UP")
                        Up.modif = mod.name
                        Up.direction = "UP"
                        
                        Dw = row.operator("btool.move_stack",icon ="TRIA_DOWN")
                        Dw.modif = mod.name
                        Dw.direction = "DOWN"
                        
                        
                        
                    else:
                        row.label(mod.name)
                        #Stack Changer
                        Up = row.operator("btool.move_stack",icon ="TRIA_UP")
                        Up.modif = mod.name
                        Up.direction = "UP"
                        
                        Dw = row.operator("btool.move_stack",icon ="TRIA_DOWN")
                        Dw.modif = mod.name
                        Dw.direction = "DOWN"

        except:
            return
        
def VIEW3D_BooleanMenu(self, context):
    self.layout.menu(BooleanMenu.bl_idname)
    
#------------------- REGISTER ------------------------------      
addon_keymaps = []

def register():
    
    #Handlers
    bpy.app.handlers.scene_update_post.append(HandleScene)
    
    
    # Operators
    bpy.utils.register_class(BooleanUnion)
    bpy.utils.register_class(BooleanDiff)
    bpy.utils.register_class(BooleanInters)
    
    # Others
    bpy.utils.register_class(BTool_FindBrush)
    bpy.utils.register_class(BTool_MoveStack)
    bpy.utils.register_class(BTool_Remove)
    bpy.utils.register_class(BTool_ToMesh)
          
    #Append 3DVIEW Menu
    bpy.utils.register_class(BooleanMenu)
    bpy.types.VIEW3D_MT_object.append(VIEW3D_BooleanMenu)
    
    # Append 3DVIEW Tab
    bpy.utils.register_class(BooleanTab)
    
    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(BooleanUnion.bl_idname, 'NUMPAD_PLUS', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BooleanDiff.bl_idname, 'NUMPAD_MINUS', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    kmi = km.keymap_items.new(BooleanInters.bl_idname, 'NUMPAD_ASTERIX', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    

def unregister():
    
    bpy.utils.unregister_class(BooleanMenu)
    bpy.utils.unregister_class(BooleanTab)
    bpy.types.VIEW3D_MT_object.remove(VIEW3D_BooleanMenu)
        
    #Operators
    bpy.utils.unregister_class(BooleanUnion)
    bpy.utils.unregister_class(BooleanDiff)
    bpy.utils.unregister_class(BooleanInters)
    bpy.utils.unregister_class(BTool_ToMesh)
    
    #Othes
    bpy.utils.unregister_class(BTool_FindBrush)
    bpy.utils.unregister_class(BTool_MoveStack)
    bpy.utils.unregister_class(BTool_Remove)
        
    bpy.app.handlers.scene_update_post.remove(HandleScene)
    bpy.types.VIEW3D_MT_object.remove(VIEW3D_BooleanMenu)
    
    # Keymapping
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    

if __name__ == "__main__":
    register()
