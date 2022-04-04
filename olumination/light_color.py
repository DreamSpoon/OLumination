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
from pickle import NONE

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

class OLuminLC_ColorMath(bpy.types.Operator):
    """With selected lights, adjust components of light's color with mathematical operation. E.g. math """ \
    """function Power will increase saturation with values less than 1, and decrease saturation with values greater than 1"""
    bl_idname = "olumin_lc.math_light_color"
    bl_label = "Color Math"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene

        # prevent code injection attacks by segregating input from code execution from string : TODO test this
        cc = scn.OLuminLC_MathColorComponent
        # segregate the incoming color component string from the outgoing color component string to prevent code
        # injection attacks
        color_comp = ""
        if cc == "R":
            color_comp = "r"
        elif cc == "G":
            color_comp = "g"
        elif cc == "B":
            color_comp = "b"
        elif cc == "H":
            color_comp = "h"
        elif cc == "S":
            color_comp = "s"
        elif cc == "V":
            color_comp = "v"
        else:
            self.report({'ERROR'}, "Unable to determine light's color component to use for math.")
            return {'CANCELLED'}

        sel_lights = get_lights_from_selected(context)
        m_func = scn.OLuminLC_MathFunction
        if m_func == "ADD":
            apply_light_color_math_add(sel_lights, color_comp, scn.OLuminLC_MathInputValue)
        elif m_func == "MULTIPLY":
            apply_light_color_math_multiply(sel_lights, color_comp, scn.OLuminLC_MathInputValue)
        elif m_func == "POWER":
            apply_light_color_math_power(sel_lights, color_comp, scn.OLuminLC_MathInputValue)
        elif m_func == "SET":
            apply_light_color_math_set(sel_lights, color_comp, scn.OLuminLC_MathInputValue)
        else:
            self.report({'ERROR'}, "Unable to determine math function to apply with light's color.")
            return {'CANCELLED'}

        return {'FINISHED'}

def apply_light_color_math_add(sel_lights, cc, math_input_value):
    # prevent code injection attack through cc string: TODO test this
    if len(cc) == 1:
        for light in sel_lights:
            exec("light.data.color." + cc + " += math_input_value")

def apply_light_color_math_multiply(sel_lights, cc, math_input_value):
    # prevent code injection attack through cc string: TODO test this
    if len(cc) == 1:
        for light in sel_lights:
            exec("light.data.color." + cc + " *= math_input_value")

def apply_light_color_math_power(sel_lights, cc, math_input_value):
    # second equality test is to prevent code injection attack through cc string: TODO test this
    if math_input_value >= 0 and len(cc) == 1:
        for light in sel_lights:
            cc_as_number = None
            # get floating point number of light.data.color.color_component and assign to cc_as_number
            exec("cc_as_number = light.data.color." + cc)
            # cannot raise zero to a negative power, checking for integer and floating point with 'or'
            if math_input_value < 0 and (cc_as_number == 0 or cc_as_number == 0.0):
                continue
            # calculate light color component raised to the power of math_input_value
            exec("light.data.color." + cc + " = pow(light.data.color." + cc + ", math_input_value)")

def apply_light_color_math_set(sel_lights, cc, math_input_value):
    # prevent code injection attack through cc string: TODO test this
    if len(cc) == 1:
        for light in sel_lights:
            exec("light.data.color." + cc + " = math_input_value")
