# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

LE_MATH_ADD = "ADD"
LE_MATH_MULTIPLY = "MULTIPLY"
LE_MATH_POWER = "POWER"
LE_MATH_SET = "SET"

class OLuminLE_MathLightEnergy(bpy.types.Operator):
    """With selected lights, adjust the light's energy value (only used in BlenderRender/EEVEE) with math function"""
    bl_idname = "olumin_le.math_light_energy"
    bl_label = "Apply Function"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel_lights = get_lights_from_selected(context)
        scn = context.scene
        if scn.OLuminLE_MathFunction == LE_MATH_ADD:
            for light in sel_lights:
                light.data.energy = light.data.energy + context.scene.OLuminLE_MathInputValue
        elif scn.OLuminLE_MathFunction == LE_MATH_MULTIPLY:
            for light in sel_lights:
                light.data.energy = light.data.energy * context.scene.OLuminLE_MathInputValue
        elif scn.OLuminLE_MathFunction == LE_MATH_POWER:
            for light in sel_lights:
                light.data.energy = pow(light.data.energy, context.scene.OLuminLE_MathInputValue)
        elif scn.OLuminLE_MathFunction == LE_MATH_SET:
            for light in sel_lights:
                light.data.energy = context.scene.OLuminLE_MathInputValue
        else:
            # the following code should never be called - just a debug print
            print("TODO: code to handle Math Light Energy with function: ")
            print(scn.OLuminLE_MathFunction)

        return {'FINISHED'}
