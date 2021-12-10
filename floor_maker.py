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
    myobject.lock_location = (True, True, True)
    
    set_normals(myobject)
    
    removeMeshFromMemory(old_mesh.name)
    
    return myobject


def removeMeshFromMemory (passedMeshName):
    # Extra test because this can crash Blender.
    mesh = bpy.data.meshes[passedMeshName]
    print(passedMeshName)
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
def create_OpenLockBool_data(self, myframe):

    mydata = OpenLock_Clip_Bool_Floor_model(self.X, self.Y)
    
    verts = mydata[0]
    faces = mydata[1]

    mymesh = bpy.data.meshes.new("ClipBool")
    myobject = bpy.data.objects.new("ClipBool", mymesh)

    myobject.location = bpy.context.scene.cursor.location
    bpy.context.collection.objects.link(myobject)

    mymesh.from_pydata(verts, [], faces)
    mymesh.update(calc_edges=True)

    # Translate to Floorframe and parent
    myobject.parent = myframe
    myobject.lock_rotation = (True, True, False)
    myobject.lock_location = (True, True, True)

    return myobject

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

    # Vertex
    myvertex = [(0,   0, BOOL_BOTTOM_HEIGHT),
                (0,   2, BOOL_BOTTOM_HEIGHT),
                (1,   2, BOOL_BOTTOM_HEIGHT),
                (2,   5, BOOL_BOTTOM_HEIGHT),
                (2,   6, BOOL_BOTTOM_HEIGHT),
                (12,  6, BOOL_BOTTOM_HEIGHT),
                (12,  5, BOOL_BOTTOM_HEIGHT),
                (11,  2, BOOL_BOTTOM_HEIGHT),
                (10,  2, BOOL_BOTTOM_HEIGHT),
                (10,  0, BOOL_BOTTOM_HEIGHT),
                (0,   0, BOOL_TOP_HEIGHT),
                (0,   2, BOOL_TOP_HEIGHT),
                (1,   2, BOOL_TOP_HEIGHT),
                (2,   5, BOOL_TOP_HEIGHT),
                (2,   6, BOOL_TOP_HEIGHT),
                (12,  6, BOOL_TOP_HEIGHT),
                (12,  5, BOOL_TOP_HEIGHT),
                (11,  2, BOOL_TOP_HEIGHT),
                (10,  2, BOOL_TOP_HEIGHT),
                (10,  0, BOOL_TOP_HEIGHT)]

    # Faces
    myfaces = [(0, 1, 10, 11), (1, 2, 11, 12), (2, 3, 12, 13), (3, 4, 13, 14), (4, 5, 14, 15),
               (5, 6, 15, 16), (6, 7, 16, 17), (7, 8, 17, 18), (8, 9, 18, 19),(0, 1, 18, 19),(0,1,2,3,4,5,6,7,8,9),(10,11,12,13,14,15,16,17,18,19)]

    return myvertex, myfaces
