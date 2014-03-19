bl_info = {
    "name": "Blender Navigator",
    "category": "Scene",
}

import bpy

import socket
import mathutils
import math

#----------- Initial Values ----------------------------
print("----------------------------------------------")


# Math -----------------------------
TargetZoom = 0;

# UDP Network
HOST = '192.168.2.101'  # Endereco IP do Servidor
PORT = 6000            # Porta que o Servidor esta
dest = (HOST, PORT)
server = (HOST, PORT)

#----------------------------------------------------------------------

# --------------------------------------------------------------
class BlenderNavPanel(bpy.types.Panel):
    """Blender Navigator Configs"""
    bl_label = "Blender Navigator"
    bl_idname = "VIEW3D_PT_BlenderNav"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "screen"
    
 
    def draw(self, context):
        layout = self.layout
        wd = bpy.context.screen
        
        self.layout.prop(wd, "NavEnable")
        self.layout.prop(wd, "Drag_Sens")
       

def register():
    InitValues()
    bpy.utils.register_class(BlenderNavPanel)
    
    
#----------------------------------------------------------------------

# -----------------  Modal Timer --------------------------------------
# Classe Principal Executa executa a cada 1/120 segundos a função "Modal"
# para receber as funções pela rede

class RunModalTimer(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.run_nav"
    bl_label = "Blender Navigator Update"
        
    _timer = None
    _holdEnable = False;
    

    def modal(self, context, event):
        
        if(self._holdEnable != bpy.context.screen.NavEnable):
            self._holdEnable = bpy.context.screen.NavEnable
            
            if(self._holdEnable):
                StartReceive()
            else:
                udpReceive.close()            
        
        if(self._holdEnable and event.type == 'TIMER' ):
            ReceiveData()
            
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        wm = bpy.context.window_manager
        self._timer = wm.event_timer_add(1/120, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = bpy.context.window_manager
        wm.event_timer_remove(self._timer)
        return {'CANCELLED'}
    
#----------------------------------------------------------------------

# ------------------Bridge Command ------------------------------------

def FilterCommand(message):
    
    if("CMD_Drag" in message):
        msg = message.split(" ")
        DeltaValx = msg[1]
        DeltaValy = msg[2]
        RotaScreen(DeltaValx,DeltaValy,0)
        
    elif("CMD_Scale" in message):
        msg = message.split(" ")
        DeltaVal = msg[1]
        ZoomScreen(DeltaVal)
        
#----------------------------------------------------------------------

# ----------------- Transformations --------------------------------
def ZoomScreen(DeltaVal):
    sensivity = .05;
    
    try:
        area = bpy.context.area
        if(area.spaces.active.type == "VIEW_3D"):
            print(DeltaVal)
            area.spaces.active.region_3d.view_distance += (float(DeltaVal) * sensivity) 
            
    except:
            return

def RotaScreen(x,y,z):
    
    sensivity = .4;
    
    _x = float(y) * sensivity
    _y = float(x) * sensivity
    _z = float(z) * sensivity

    area = bpy.context.area
    
    try: # Evita erro em momentos que nao existe contexto
        if(area.spaces.active.type == "VIEW_3D"):
            #print(str(area) + ": " + str(area.spaces.active))
            rotation=area.spaces.active.region_3d.view_rotation
            
            rotFinal = rotation
            
            rot = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(_x))
            rotFinal = rotation * rot # Local Rotate
            
            rot = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(_y))
            rotFinal = rot * rotFinal # Global Rotate
            
            TargetRotate = mathutils.Quaternion()
            TargetRotate.x = rotFinal.x
            TargetRotate.y = rotFinal.y
            TargetRotate.z = rotFinal.z
            TargetRotate.w = rotFinal.w
            
            rotation.x = rotFinal.x
            rotation.y = rotFinal.y
            rotation.z = rotFinal.z
            rotation.w = rotFinal.w

            rotation.normalize()
    except:
        pass
# -----------------------------------------------------------------

# ----------------- UPD Data Controller  ---------------

def SendData():
    global udpSend
    udpSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSend.sendto ("Vitor".encode(), dest)
    udpSend.close()

def StartReceive():
    
    global udpReceive
    
    udpReceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpReceive.setblocking(0)
    udpReceive.bind(server)
    
def ReceiveData():
    try:
        data = udpReceive.recv(4096)
        if(data):
            FilterCommand(str(data.decode('utf-8')));
            
    except socket.error:
        #print("Nenhum dado")
        pass
#------------------------------------------------------    

# --------------Registers ----------------------   
def register():
    bpy.utils.register_class(BlenderNavPanel)
    bpy.utils.register_class(RunModalTimer)
    
    # ---------------------- Painel UI  Properties -------------_----------
    bpy.types.Screen.NavEnable = bpy.props.BoolProperty(name="Enable")
    bpy.types.Screen.Drag_Sens = bpy.props.FloatProperty(name="Drag_Sens", default = 0.4)

def unregister():
    bpy.utils.unregister_class(RunModalTimer)
    bpy.utils.unregister_class(BlenderNavPanel)

if __name__ == "__main__":
    register()
#--------------------------------------------------
bpy.ops.wm.run_nav()
    


