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

class OLuminLE_MathLightEnergy(bpy.types.Operator):
    """With selected lights, adjust the light's energy value (only used in BlenderRender/EEVEE) with math function"""
    bl_idname = "olumin_le.math_light_energy"
    bl_label = "Apply Function"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel_lights = get_lights_from_selected(context)
        scn = context.scene
        math_function = scn.OLuminLE_MathFunction
        math_input_value = scn.OLuminLE_MathInputValue
        if math_function == "ADD":
            for light in sel_lights:
                light.data.energy = light.data.energy + math_input_value
        elif math_function == "MULTIPLY":
            for light in sel_lights:
                light.data.energy = light.data.energy * math_input_value
        elif math_function == "POWER":
            for light in sel_lights:
                # cannot raise zero to a negative power, checking for integer and floating point with 'or'
                if math_input_value < 0 and (light.data.energy == 0 or light.data.energy == 0.0):
                    continue
                light.data.energy = pow(light.data.energy, math_input_value)
        elif math_function == "SET":
            for light in sel_lights:
                light.data.energy = math_input_value
        else:
            # the following code should never be called - just a debug print
            self.report({'ERROR'}, "Unable to determine math function to apply with light's energy.")
            return {'CANCELLED'}

        return {'FINISHED'}
