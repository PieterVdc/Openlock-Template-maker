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
# ----------------------------------------------------------

# ----------------------------------------------
# Define Addon info
# ----------------------------------------------
bl_info = {
    "name": "Dungeon Tile",
    "author": "PieterVdc",
    "location": "View3D > Add Mesh / Sidebar > Create Tab",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "description": "Generate templates for Tiles, walls etc for your 3D printed dungeon with ",
    "doc_url": "https://github.com/PieterVdc/Openlock-Template-maker/wiki",
    "warning": "WIP",
    "category": "Add Mesh"
    }

import sys
import os

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import importlib
    importlib.reload(floor_maker)
    importlib.reload(main_panel)
else:
    from . import floor_maker
    from . import main_panel


# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences

## noinspection PyUnresolvedReferences
from bpy.types import (
        Menu,
        VIEW3D_MT_mesh_add
        )


# ----------------------------------------------------------
# Registration
# ----------------------------------------------------------


class dungeontiles_MT_CustomMenuAdd(Menu):
    bl_idname = "VIEW3D_MT_mesh_custom_menu_add"
    bl_label = "dungeontiles"

    # noinspection PyUnusedLocal
    def draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator("mesh.dungeontiles_floor", text="Floor")
        self.layout.menu("VIEW3D_MT_mesh_decoration_add", text="Decoration props", icon="GROUP")

# --------------------------------------------------------------
# Register all operators and panels
# --------------------------------------------------------------

# Add to Add meshes menu
def DungeonTileMenu_func(self, context):
    layout = self.layout
    layout.separator()
    self.layout.menu("VIEW3D_MT_mesh_custom_menu_add", icon="GROUP")


classes = (
    dungeontiles_MT_CustomMenuAdd,
    floor_maker.dungeontiles_OT_Floor,
    floor_maker.dungeontiles_PT_FloorObjectgenerator,
    main_panel.dungeontiles_PT_Main
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    VIEW3D_MT_mesh_add.append(DungeonTileMenu_func)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    VIEW3D_MT_mesh_add.remove(DungeonTileMenu_func)

if __name__ == '__main__':
    register()
