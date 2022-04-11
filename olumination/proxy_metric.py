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

PM_NAME_PREPEND = "ProxyMetric"
PM_METARIG_PREPEND = PM_NAME_PREPEND + "Rig"
PM_EMPTY_PREPEND = PM_NAME_PREPEND + "Empty"
PM_BASE_CIRCLE_NAME = PM_NAME_PREPEND + "BaseCircle"

class OLuminPM_CreateSimpleHumanProxy(bpy.types.Operator):
    """Use human rig (Rigify addon) to estimate distance to ground plane, sizes of objects, etc. in HDRIs. """ \
    """Proxy Metric can be used to detect/analyze geometry by comparing human size to apparent size of image object"""
    bl_idname = "olumin_pm.create_proxy_metric_simple_human"
    bl_label = "Simple Human Proxy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if create_proxy_simple_human(context) is None:
            self.report({'ERROR'}, "Unable to continue. Enable Rigify addon in User Preferences, and try again.")
            return {'CANCELLED'}
        return {'FINISHED'}

def create_proxy_simple_human(context):
    metarig_obj = create_simple_human_metarig(context, PM_METARIG_PREPEND)
    if metarig_obj is None:
        return None
    metarig_obj.lock_location[0] = True
    metarig_obj.lock_location[1] = True

    empty_obj = create_empty_object(context, PM_EMPTY_PREPEND, "PLAIN_AXES", (0, 0, 0))
    empty_obj.lock_location[2] = True

    metarig_obj.parent = empty_obj

    wgt_circle = create_base_circle(context, PM_BASE_CIRCLE_NAME)
    wgt_circle.parent = metarig_obj

    # return root object
    return empty_obj

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

def create_base_circle(context, circle_name):
    bpy.ops.mesh.primitive_circle_add(radius=0.1875, location=(0, 0, 0), fill_type="NGON")
    widget_circle = context.active_object
    widget_circle.name = circle_name
    return widget_circle

class OLuminPM_DropVertex(bpy.types.Operator):
    """Create a vertex at location of Base Circle of selected Proxy Metric (select any part of Proxy Metric and """ \
    """Base Circle object will be found automatically)"""
    bl_idname = "olumin_pm.drop_vertex"
    bl_label = "Drop Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        a = 1

    def execute(self, context):
        print("drop vertex executed")
        return {'FINISHED'}
