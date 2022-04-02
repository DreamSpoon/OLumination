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

class OLuminLC_SaturationPower(bpy.types.Operator):
    """With selected lights, adjust the Saturation value in the light's color with the mathematical 'power' \
    operation. Increase saturation with values below 1, decrease saturation with values above 1"""
    bl_idname = "olumin_lc.saturation_power"
    bl_label = "Saturation Power"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel_lights = get_lights_from_selected(context)
        for light in sel_lights:
            light.data.color.s = pow(light.data.color.s, context.scene.OLuminLC_SatPower)

        return {'FINISHED'}
