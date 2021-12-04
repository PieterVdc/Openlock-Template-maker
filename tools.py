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
# support routines and general functions
# Author: PieterVdc
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
from os import path


# --------------------------------------------------------------------
# Set normals
# True= faces to inside
# False= faces to outside
# --------------------------------------------------------------------
def set_normals(myobject, direction=False):
    bpy.context.view_layer.objects.active = myobject
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    # recalculate outside normals
    bpy.ops.mesh.normals_make_consistent(inside=direction)
    # go object mode again
    bpy.ops.object.editmode_toggle()


# --------------------------------------------------------------------
# Remove doubles
# --------------------------------------------------------------------
def remove_doubles(myobject):
    bpy.context.view_layer.objects.active = myobject
    # go edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    # select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    # remove
    bpy.ops.mesh.remove_doubles()
    # go object mode again
    bpy.ops.object.editmode_toggle()


# --------------------------------------------------------------------
# Add modifier (boolean)
# --------------------------------------------------------------------
def set_modifier_boolean(myobject, bolobject):
    bpy.context.view_layer.objects.active = myobject
    if bpy.context.view_layer.objects.active.name == myobject.name:
        bpy.ops.object.modifier_add(type='BOOLEAN')
        mod = myobject.modifiers[len(myobject.modifiers) - 1]
        mod.operation = 'DIFFERENCE'
        mod.object = bolobject



# --------------------------------------------------------------------
# Parent object (keep positions)
# --------------------------------------------------------------------
def parentobject(parentobj, childobj):
    # noinspection PyBroadException
    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = parentobj
        parentobj.select_set(True)
        childobj.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        return True
    except:
        return False


# ------------------------------------------------------------------------------
# Remove all children objects
# ------------------------------------------------------------------------------
def remove_children(myobject):
    # Remove children
    for child in myobject.children:
        # noinspection PyBroadException
        try:
            # noinspection PyBroadException
            try:
                # remove child relationship
                for grandchild in child.children:
                    grandchild.parent = None
                # remove modifiers
                for mod in child.modifiers:
                    bpy.ops.object.modifier_remove(name=mod.name)
            except:
                pass
            # clear child data
            if child.type == 'MESH':
                old = child.data
                child.select_set(True)
                bpy.ops.object.delete()
                bpy.data.meshes.remove(old)
            if child.type == 'CURVE':
                child.select_set(True)
                bpy.ops.object.delete()
        except:
            pass


# --------------------------------------------------------------------
# Get all parents
# --------------------------------------------------------------------
def get_allparents(myobj):
    obj = myobj
    mylist = []
    while obj.parent is not None:
        mylist.append(obj)
        objp = obj.parent
        obj = objp

    mylist.append(obj)

    return mylist

