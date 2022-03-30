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

PROXY_METRIC_PREPEND_NAME = "ProxyMetric"
OLUMIN_PM_METARIG_PREPEND = PROXY_METRIC_PREPEND_NAME + "Rig"
OLUMIN_PM_EMPTY_PREPEND = PROXY_METRIC_PREPEND_NAME + "Empty"

def create_empty_object(context, empty_name, empty_type, empty_loc):
    bpy.ops.object.empty_add(type=empty_type, location=empty_loc)
    new_obj = context.active_object
    new_obj.name = empty_name
    return new_obj

def create_simple_human_metarig(context, rig_name):
    # function is part of Rigify, and Rigify might not be enabled on the user's system, so check for function's
    # existence before calling it
    if "armature_basic_human_metarig_add" not in dir(bpy.ops.object):
        return None
    bpy.ops.object.armature_basic_human_metarig_add()
    new_obj = context.active_object
    new_obj.name = rig_name
    return new_obj

class OLuminPM_CreateSimpleHumanProxy(bpy.types.Operator):
    """Select the occluding disk sun lights of the currently selected Sunlit Rig(s)"""
    bl_idname = "olumin_pm.create_proxy_metric_simple_human"
    bl_label = "Simple Human Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        metarig_obj = create_simple_human_metarig(context, OLUMIN_PM_METARIG_PREPEND)
        if metarig_obj is None:
            self.report({'ERROR'}, "Unable to continue. Enable Rigify addon in User Preferences, and try again.")
            return {'CANCELLED'}
        metarig_obj.lock_location[0] = True
        metarig_obj.lock_location[1] = True

        empty_obj = create_empty_object(context, OLUMIN_PM_EMPTY_PREPEND, "PLAIN_AXES", (0, 0, 0))
        empty_obj.lock_location[2] = True

        metarig_obj.parent = empty_obj
        return {'FINISHED'}
