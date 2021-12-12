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

# ----------------------------------------------------------
# Author: PieterVdc
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
import math
# noinspection PyUnresolvedReferences
from bpy.types import Operator, PropertyGroup, Object, Panel
from bpy.props import FloatProperty, BoolProperty, EnumProperty, FloatVectorProperty, CollectionProperty
from .tools import *


# ------------------------------------------------------------------
# Define operator class to create object
# ------------------------------------------------------------------
class dungeontiles_OT_Floor(Operator):
    bl_idname = "mesh.dungeontiles_floor"
    bl_label = "Floor"
    bl_description = "all floor variants"
    bl_category = 'View'
    bl_options = {'REGISTER', 'UNDO'}

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    # noinspection PyUnusedLocal
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Use Properties panel (N) to define parms", icon='INFO')

    # -----------------------------------------------------
    # Execute
    # -----------------------------------------------------
    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            create_object(self, context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "dungeontiles: Option only valid in Object mode")
            return {'CANCELLED'}


# ------------------------------------------------------------------------------
#
# Create main object. The other objects will be children of this.
#
# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
def create_object(self, context):
    # deselect all objects
    for o in bpy.data.objects:
        o.select_set(False)

    mainobject = create_Floor_data()

    # we select, and activate, main object
    mainobject.select_set(True)
    bpy.context.view_layer.objects.active = mainobject


# ------------------------------------------------------------------------------
#
# Update main mesh and children objects
#
# ------------------------------------------------------------------------------
# noinspection PyUnusedLocal
def update_object(self, context):
    # When we update, the active object is the main object
    o = bpy.context.active_object
    oldmesh = o.data
    oldname = o.data.name
    # Now we deselect that object to not delete it.
    o.select_set(False)
    # deselect all objects
    for obj in bpy.data.objects:
        obj.select_set(False)

    # -----------------------
    # remove all children
    # -----------------------
    # first granchild
    for child in o.children:
        remove_children(child)
        print("child:" + child.name)
    # now children of main object
    remove_children(o)

    mp = o.FloorObjectGenerator[0]
    mainobject = update_Floor_data(o,mp)
    # we select, and activate, main object
    mainobject.select_set(True)
    bpy.context.view_layer.objects.active = mainobject


# ------------------------------------------------------------------
# Define property group class to create or modify
# ------------------------------------------------------------------
class ObjectProperties(PropertyGroup):

    X: FloatProperty(
            name='Frame width',
            min=0.5, max=50,
            default=2, precision=1,
            step=50,
            description='Doorframe width', update=update_object,
            )
    Y: FloatProperty(
            name='Frame height',
            min=0.5, max=50,
             default=2, precision=1,
            step=50,
            description='Doorframe height', update=update_object,
            )
    handle: EnumProperty(
            name="Type",
            items=(
                ('1', "Rectangle", ""),
                ('2', "Round", ""),
                ),
            description="Type of Floor Tile",
            update=update_object,
            )


# Register
bpy.utils.register_class(ObjectProperties)
Object.FloorObjectGenerator= CollectionProperty(type=ObjectProperties)


# ------------------------------------------------------------------
# Define panel class to modify object
# ------------------------------------------------------------------
class dungeontiles_PT_FloorObjectgenerator(Panel):
    bl_idname = "OBJECT_PT_Floor_generator"
    bl_label = "Floor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Create'

    # -----------------------------------------------------
    # Verify if visible
    # -----------------------------------------------------
    @classmethod
    def poll(cls, context):
        o = context.object
        if o is None:
            return False
        if 'FloorObjectGenerator' not in o:
            return False
        else:
            return True

    # -----------------------------------------------------
    # Draw (create UI interface)
    # -----------------------------------------------------
    def draw(self, context):
        o = context.object
        # noinspection PyBroadException
        try:
            if 'FloorObjectGenerator' not in o:
                return
        except:
            return

        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label(text='Warning: Operator does not work in edit mode.', icon='ERROR')
        else:
            myobjdat = o.FloorObjectGenerator[0]
            space = bpy.context.space_data
            if not space.local_view:
                # Imperial units warning
                if bpy.context.scene.unit_settings.system == "IMPERIAL":
                    row = layout.row()
                    row.label(text="Warning: Imperial units not supported", icon='COLOR_RED')
                box = layout.box()
                row = box.row()
                row.prop(myobjdat, 'X')
                row.prop(myobjdat, 'Y')
                row = box.row()
                layout.prop(myobjdat, 'handle')

            else:
                row = layout.row()
                row.label(text="Warning: Operator does not work in local view mode", icon='ERROR')


# ------------------------------------------------------------------------------
# Create Floor
# All custom values are passed using self container (self.myvariable)
# ------------------------------------------------------------------------------
def create_Floor_data():

    tempMesh = bpy.data.meshes.new("TempMesh")
    myobject = bpy.data.objects.new("FloorObject", tempMesh)
    myobject.FloorObjectGenerator.add()
    mp = myobject.FloorObjectGenerator[0]
    
    myobject.location = bpy.context.scene.cursor.location
    bpy.context.collection.objects.link(myobject)
    
    myobject = update_Floor_data(myobject,mp)
    
    return myobject
    
    # ------------------------------------------------------------------------------
# Create Floor
# All custom values are passed using self container (self.myvariable)
# ------------------------------------------------------------------------------
def update_Floor_data(myobject,mp):

    mydata = Floor_model_01(mp.X, mp.Y)
    
    verts = mydata[0]
    faces = mydata[1]
    
    old_mesh = myobject.data
    old_mesh.name = "old_mesh"
    
    mymesh = bpy.data.meshes.new("FloorMesh")
    
    mymesh.from_pydata(verts, [], faces)
    mymesh.update(calc_edges=True)
    myobject.data = mymesh
    
    # Translate to Floorframe and parent
    myobject.lock_rotation = (True, True, False)
    myobject.lock_location = (False, False, True)
    
    set_normals(myobject)
    
    removeMeshFromMemory(old_mesh.name)
    myobject.modifiers.clear()
    createBoolObjects(myobject,mp)
    
    return myobject


def removeMeshFromMemory (passedMeshName):
    # Extra test because this can crash Blender.
    mesh = bpy.data.meshes[passedMeshName]
    try:
        mesh.user_clear()
        can_continue = True
    except:
        can_continue = False
    
    if can_continue == True:
        try:
            bpy.data.meshes.remove(mesh)
            result = True
        except:
            result = False
    else:
        result = False
        
    return result
    
# ------------------------------------------------------------------------------
# Create OpenlockBool
# All custom values are passed using self container (self.myvariable)
# ------------------------------------------------------------------------------
def createBoolObjects(floorObject,mp):
    
    XnumBoolObjects = int(mp.X * 2) - 1
    YnumBoolObjects = int(mp.Y * 2) - 1

    
    for X in range(XnumBoolObjects):
        create_OpenLockBool_data(floorObject,X*12.7+5.7                ,0         ,0)   
        print(X)
    for Y in range(YnumBoolObjects):
        create_OpenLockBool_data(floorObject,mp.X*25.4                 ,Y*12.7+5.7,0.5 * math.pi)
        print(Y)
    for X in range(XnumBoolObjects):
        create_OpenLockBool_data(floorObject,mp.X*25.4 - (X*12.7) - 5.7,mp.Y*25.4       ,math.pi)  
        print(X)
    for Y in range(YnumBoolObjects):
        create_OpenLockBool_data(floorObject,0                         ,mp.Y*25.4 - (Y * 12.7)-5.7,1.5 * math.pi)
        print(Y)
    
# ------------------------------------------------------------------------------
# Create OpenlockBool
# All custom values are passed using self container (self.myvariable)
# ------------------------------------------------------------------------------
def create_OpenLockBool_data(floorObject,X,Y,rotation):
    
    mydata = OpenLock_Clip_Bool_Floor_model()
    
    verts = mydata[0]
    faces = mydata[1]

    boolMesh = bpy.data.meshes.new("ClipBool")
    boolObject = bpy.data.objects.new("ClipBool", boolMesh)
    boolObject.location = (X,Y,0)
    boolObject.rotation_mode = 'XYZ'
    boolObject.rotation_euler = (0,0,rotation)
    bpy.context.collection.objects.link(boolObject)
    boolMesh.from_pydata(verts, [], faces)
    boolMesh.update(calc_edges=True)

    boolObject.parent = floorObject
    boolObject.lock_rotation = (True, True, True)
    boolObject.lock_location = (True, True, True)
    set_modifier_boolean(floorObject,boolObject)
    boolObject.display_type = 'WIRE'
    return boolObject

# ----------------------------------------------
# Floor Box
# ----------------------------------------------
def Floor_model_01(X, Y):

    FLOOR_HEIGHT = 7
    maxx = X * 25.4
    maxy = Y * 25.4

    # Vertex
    myvertex = [(0,    0,    0),
                (0,    maxy, 0),
                (maxx, maxy, 0),
                (maxx, 0,    0),
                (0,    0,    FLOOR_HEIGHT),
                (0,    maxy, FLOOR_HEIGHT),
                (maxx, maxy, FLOOR_HEIGHT),
                (maxx, 0,    FLOOR_HEIGHT)]

    # Faces
    myfaces = [(4, 5, 1, 0), (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3), (0, 1, 2, 3),
               (7, 6, 5, 4)]

    return myvertex, myfaces
    
# ----------------------------------------------
# OpenLock Clip Bool Floor
# ----------------------------------------------
def OpenLock_Clip_Bool_Floor_model():

    BOOL_BOTTOM_HEIGHT = 1.4
    BOOL_TOP_HEIGHT = 5.6
    
    SUPPORT_LAYER1_HEIGHT = 1.9
    SUPPORT_LAYER2_HEIGHT = 3
    SUPPORT_LAYER3_HEIGHT = 3.5
    SUPPORT_LAYER4_HEIGHT = 4
    SUPPORT_LAYER5_HEIGHT = 5.1
    SUPPORT_DEPTH         = 2
    SUPPORT_X_1_1 = 3.9
    SUPPORT_X_1_2 = 4.1
    SUPPORT_X_1_3 = 5.1
    SUPPORT_X_1_4 = 5.3
    SUPPORT_X_2_1 = 8.9
    SUPPORT_X_2_2 = 9.1
    SUPPORT_X_2_3 = 10.1
    SUPPORT_X_2_4 = 10.3





    # Vertex
    myvertex = [(0,   -.1, BOOL_BOTTOM_HEIGHT),
                (0,   2, BOOL_BOTTOM_HEIGHT),
                (1,   2, BOOL_BOTTOM_HEIGHT),
                (2,   5, BOOL_BOTTOM_HEIGHT),
                (2,   6, BOOL_BOTTOM_HEIGHT),
                (12,  6, BOOL_BOTTOM_HEIGHT),
                (12,  5, BOOL_BOTTOM_HEIGHT),
                (13,  2, BOOL_BOTTOM_HEIGHT),
                (14,  2, BOOL_BOTTOM_HEIGHT),
                (14,  -.1, BOOL_BOTTOM_HEIGHT),#10
                (0,   -.1, BOOL_TOP_HEIGHT),
                (0,   2, BOOL_TOP_HEIGHT),
                (1,   2, BOOL_TOP_HEIGHT),
                (2,   5, BOOL_TOP_HEIGHT),
                (2,   6, BOOL_TOP_HEIGHT),
                (12,  6, BOOL_TOP_HEIGHT),
                (12,  5, BOOL_TOP_HEIGHT),
                (13,  2, BOOL_TOP_HEIGHT),    
                (14,  2, BOOL_TOP_HEIGHT),
                (14,  -.1, BOOL_TOP_HEIGHT),
                
                (SUPPORT_X_1_2,-.1,BOOL_BOTTOM_HEIGHT),#20
                (SUPPORT_X_1_1,-.1,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_1_1,-.1,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_1_2,-.1,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_1_1,-.1,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_1_1,-.1,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_1_2,-.1,BOOL_TOP_HEIGHT),
                (SUPPORT_X_1_3,-.1,BOOL_BOTTOM_HEIGHT),#27
                (SUPPORT_X_1_4,-.1,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_1_4,-.1,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_1_3,-.1,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_1_4,-.1,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_1_4,-.1,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_1_3,-.1,BOOL_TOP_HEIGHT),
                (SUPPORT_X_1_2,SUPPORT_DEPTH,BOOL_BOTTOM_HEIGHT),#34
                (SUPPORT_X_1_1,SUPPORT_DEPTH,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_1_1,SUPPORT_DEPTH,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_1_2,SUPPORT_DEPTH,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_1_1,SUPPORT_DEPTH,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_1_1,SUPPORT_DEPTH,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_1_2,SUPPORT_DEPTH,BOOL_TOP_HEIGHT),
                (SUPPORT_X_1_3,SUPPORT_DEPTH,BOOL_BOTTOM_HEIGHT),#41
                (SUPPORT_X_1_4,SUPPORT_DEPTH,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_1_4,SUPPORT_DEPTH,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_1_3,SUPPORT_DEPTH,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_1_4,SUPPORT_DEPTH,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_1_4,SUPPORT_DEPTH,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_1_3,SUPPORT_DEPTH,BOOL_TOP_HEIGHT),
                
                (SUPPORT_X_2_2,-.1,BOOL_BOTTOM_HEIGHT),#48
                (SUPPORT_X_2_1,-.1,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_2_1,-.1,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_2_2,-.1,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_2_1,-.1,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_2_1,-.1,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_2_2,-.1,BOOL_TOP_HEIGHT),
                (SUPPORT_X_2_3,-.1,BOOL_BOTTOM_HEIGHT),#55
                (SUPPORT_X_2_4,-.1,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_2_4,-.1,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_2_3,-.1,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_2_4,-.1,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_2_4,-.1,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_2_3,-.1,BOOL_TOP_HEIGHT),
                (SUPPORT_X_2_2,SUPPORT_DEPTH,BOOL_BOTTOM_HEIGHT),#62
                (SUPPORT_X_2_1,SUPPORT_DEPTH,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_2_1,SUPPORT_DEPTH,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_2_2,SUPPORT_DEPTH,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_2_1,SUPPORT_DEPTH,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_2_1,SUPPORT_DEPTH,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_2_2,SUPPORT_DEPTH,BOOL_TOP_HEIGHT),
                (SUPPORT_X_2_3,SUPPORT_DEPTH,BOOL_BOTTOM_HEIGHT),#69
                (SUPPORT_X_2_4,SUPPORT_DEPTH,SUPPORT_LAYER1_HEIGHT),
                (SUPPORT_X_2_4,SUPPORT_DEPTH,SUPPORT_LAYER2_HEIGHT),
                (SUPPORT_X_2_3,SUPPORT_DEPTH,SUPPORT_LAYER3_HEIGHT),
                (SUPPORT_X_2_4,SUPPORT_DEPTH,SUPPORT_LAYER4_HEIGHT),
                (SUPPORT_X_2_4,SUPPORT_DEPTH,SUPPORT_LAYER5_HEIGHT),
                (SUPPORT_X_2_3,SUPPORT_DEPTH,BOOL_TOP_HEIGHT)
                
                
                ]

    # Faces
    myfaces = [(10,11,1,0), (11,12,2,1), (12,13,3,2), (13,14,4,3), (14,15,5,4),
               (15,16,6,5), (16,17,7,6), (17,18,8,7), (18,19,9,8),
               (2,3,4,5,6,7,69,62,41,34),
               (40,47,68,75,17,16,15,14,13,12),
               
               (0,1,2,34,20),(27,41,62,48),(7,8,9,55,69),
               (26,40,12,11,10),(54,68,47,33),(75,61,19,18,17),
               
               (10,0,20,21,22,23,24,25,26),
               (41,42,43,44,45,46,47,40,39,38,37,36,35,34),
               (69,70,71,72,73,74,75,68,67,66,65,64,63,62),
               (48,49,50,51,52,53,54,33,32,31,30,29,28,27),
               (9,19,61,60,59,58,57,56,55),
                              
               (34,35,21,20),(35,36,22,21),(36,37,23,22),(37,38,24,23),(38,39,25,24),(39,40,26,25),
               (27,28,42,41),(28,29,43,42),(29,30,44,43),(30,31,45,44),(31,32,46,45),(32,33,47,46),
               (62,63,49,48),(63,64,50,49),(64,65,51,50),(65,66,52,51),(66,67,53,52),(67,68,54,53),
               (55,56,70,69),(56,57,71,70),(57,58,72,71),(58,59,73,72),(59,60,74,73),(60,61,75,74)
               
               
               
               
               
               
               
               ]

    return myvertex, myfaces
