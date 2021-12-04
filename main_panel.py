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
# Main panel for different Dungeon Tiles general actions
# Author: PieterVdc
#
# ----------------------------------------------------------
# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
import bgl
from bpy.types import Operator, Panel, SpaceView3D
from math import sqrt, fabs, pi, asin
from .tools import *


# ------------------------------------------------------------------
# Define panel class for main functions.
# ------------------------------------------------------------------
class dungeontiles_PT_Main(Panel):
    bl_idname = "dungeontiles_PT_main"
    bl_label = "Dungeon Tiles"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Create"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    # ------------------------------
    # Draw UI
    # ------------------------------
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        myobj = context.object

        # ------------------------------
        # Elements Buttons
        # ------------------------------
        box = layout.box()
        box.label(text="Elements", icon='GROUP')
        row = box.row()
        row.operator("mesh.dungeontiles_floor")
        row = box.row()
        row.operator("mesh.dungeontiles_floor",text="Walls")
        row = box.row()
        row.operator("mesh.dungeontiles_floor",text="Roofs")
        row = box.row()
        row.operator("mesh.dungeontiles_floor",text="Clip Caps")
        row = box.row()
        row.operator("mesh.dungeontiles_floor",text="Clips")
        row = box.row()
        row.operator("mesh.dungeontiles_floor",text="Others")
