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

import math
from mathutils import Vector
import bpy
import bmesh
import bpy_extras.view3d_utils

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

SUNLIT_FIX_DIFF_CUBE_LOC = (0, -0.3, 0)

SUNLIT_NAME_PREPEND = "Sunlit"
SUNLIT_BASE_SPHERE_PREPEND = SUNLIT_NAME_PREPEND + "BaseSphere"
SUNLIT_DCUBE_PREPEND = SUNLIT_NAME_PREPEND + "DiffCube"
SUNLIT_SUN_BLINDS_PREPEND = SUNLIT_NAME_PREPEND + "Blinds"
SUNLIT_SENSOR_PLANE_PREPEND = SUNLIT_NAME_PREPEND + "Sensor"
SUNLIT_SUN_PREPEND = SUNLIT_NAME_PREPEND + "Light"
SUNLIT_ODISK_PREPEND = SUNLIT_NAME_PREPEND + "ODiskSensor"
SUNLIT_ODISK_BLINDS_PREPEND = SUNLIT_NAME_PREPEND + "ODiskBlinds"
SUNLIT_ODISK_SUN_PREPEND = SUNLIT_NAME_PREPEND + "ODiskLight"
SUNLIT_CAMERA_PREPEND = SUNLIT_NAME_PREPEND + "Camera"
SUNLIT_CAMERA_TTC_PREPEND = SUNLIT_NAME_PREPEND + "CameraTTC"

BONE_LAYER_ONLY_2 = (False, True, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    False, False)

SUNLIT_WGT_PREPEND = "SL_WGT_"
SUNLIT_WGT_CIRCLE_NAME = SUNLIT_WGT_PREPEND + "circle"
SUNLIT_WGT_CONE_NAME = SUNLIT_WGT_PREPEND + "cone"
SUNLIT_WGT_CUBE_NAME = SUNLIT_WGT_PREPEND + "cube"
SUNLIT_WGT_PLANE_NAME = SUNLIT_WGT_PREPEND + "plane"
SUNLIT_WGT_TRI_NAME = SUNLIT_WGT_PREPEND + "tri"
SUNLIT_WGT_TRI_VERTS = [
    (-1, 0, -0.6660254),
    (1, 0, -0.6660254),
    (0, 0, 1.0660254),
]

SUNLIT_BONE_SPHERE = "base_sphere"
SUNLIT_BONE_HT_SPHERE = [
    [0, 0, 0],
    [0, 0, 0.5],
]
SUNLIT_BONE_SUN_PIVOT = "sun_pivot"
SUNLIT_BONE_HT_SUN_PIVOT = [
    [0, 0, 0],
    [0, 0, 0.3],
]
SUNLIT_BONE_SUN_TARGET = "sun_pivot_target"
SUNLIT_BONE_HT_SUN_TARGET = [
    [0, 0, 0],
    [0, 0, 0.5],
]
SUNLIT_BONE_DIFF_CUBE = "diff_cube"
SUNLIT_BONE_HT_DIFF_CUBE = [
    [0, 0, 1.0],
    [0, 0, 1.5],
]
SUNLIT_BONE_SENSOR = "sensor_adjust"
SUNLIT_BONE_HT_SENSOR = [
    [0, 0, 1.02],
    [0, 0, 1.12],
]
SUNLIT_BONE_LIT_ADJUST = "light_adjust"
SUNLIT_BONE_HT_LIT_ADJUST = [
    [0, 0, 1.02],
    [0, 0, 1.5],
]

SUNLIT_BONE_ODISK = "occluding_disk"
SUNLIT_BONE_HT_ODISK = [
    [0, 0, 19.0],
    [0, 0, 20.0],
]
SUNLIT_BONE_ODISK_PIVOT = "occluding_disk_pivot"
SUNLIT_BONE_HT_ODISK_PIVOT = [
    [0, 0, 0],
    [0, 0, 0.35],
]
SUNLIT_BONE_ODISK_TARGET = "occluding_disk_pivot_target"
SUNLIT_BONE_HT_ODISK_TARGET = [
    [0, 0, 0],
    [0, 0, 0.5],
]
SUNLIT_BONE_ODISK_LIGHT = "occluding_disk_light"
SUNLIT_BONE_HT_ODISK_LIGHT = [
    [0, 0, 19],
    [0, 0, 20],
]

SUNLIT_BONE_ALL_NAMES = [
    SUNLIT_BONE_SPHERE,
    SUNLIT_BONE_SUN_PIVOT,
    SUNLIT_BONE_SUN_TARGET,
    SUNLIT_BONE_DIFF_CUBE,
    SUNLIT_BONE_SENSOR,
    SUNLIT_BONE_LIT_ADJUST,
    SUNLIT_BONE_ODISK,
    SUNLIT_BONE_ODISK_PIVOT,
    SUNLIT_BONE_ODISK_TARGET,
    SUNLIT_BONE_ODISK_LIGHT,
]
SUNLIT_BONE_MATCH_MIN = 3

SUNLIT_BASE_SPHERE_OFFSET = (0, -0.5, 0)
SUNLIT_DIFF_CUBE_OFFSET = (0, 0.5, 0)
SUNLIT_SUN_BLINDS_PLANE_OFFSET = (0, -0.5, 0)
SUNLIT_SENSOR_OFFSET = (0, -0.1, 0)
SUNLIT_SUN_OFFSET = (0, -0.48, 0)
SUNLIT_ODISK_OFFSET = (0, -1, 0)

SUNLIT_BASE_SPHERE_RADIUS = 1
SUNLIT_SENSOR_PLANE_RADIUS = 0.02
SUNLIT_SUN_BLINDS_PLANE_RADIUS = 1
SUNLIT_ODISK_RADIUS = 0.1

SUNLIT_MODNAME_SPHERE = "SunlitSphereBool"
SUNLIT_MODNAME_DC = "SunlitDiffCubeBool"
SUNLIT_MODNAME_B_WIRE = "SunlitBlindsWire"
SUNLIT_MODNAME_B_SOLID = "SunlitBlindsSolid"
SUNLIT_MODNAME_B_SIMPDEF = "SunlitBlindsSimpDef"

# number of lights to create
SUNLIT_NUM_SUN_LIGHTS = 1

SUNLIT_HEMI_SUN_POINTDIR_LIST = {
    "7": [
        (0, 0, 2),
        (1.75, 0, 1.45),
        (-1.75, 0, 1.45),
        (0.67, 1, 1.05),
        (-0.67, 1, 1.05),
        (0.67, -1, 1.05),
        (-0.67, -1, 1.05),
    ],
    "6": [
        (0, 0, 2),
        (2.02, 1.46, 1.7),
        (-0.77, 2.37, 1.7),
        (-2.49, 0, 1.7),
        (-0.77, -2.37, 1.7),
        (2.02, -1.46, 1.7),
    ],
    "5": [
        (0, 0, 2),
        (1.4, 0, 1.0),
        (-1.4, 0, 1.0),
        (0, 1.4, 1.0),
        (0, -1.4, 1.0),
    ],
    "4": [
        (0, 0, 2),
        (0, 1, 0.7),
        (-0.87, -0.5, 0.7),
        (0.87, -0.5, 0.7),
    ],
    "3": [
        (0, 1, 0.6),
        (-0.87, -0.5, 0.7),
        (0.87, -0.5, 0.7),
    ],
    "2": [
        (0, 1, 1),
        (0, -1, 1),
    ],
    "1": [
        (0, 0, 2),
    ],
}
SUNLIT_MAX_SUN_POINTDIR = 7
SUNLIT_EXTRA_POINTDIR = (0, 0, -1)

SUNLIT_FULL_SUN_POINTDIR_LIST = {
    "8": [
        (-1, -1, -1),
        (1, -1, -1),
        (-1, 1, -1),
        (1, 1, -1),
        (-1, -1, 1),
        (1, -1, 1),
        (-1, 1, 1),
        (1, 1, 1),
    ],
    "6": [
        (-2, 0, 0),
        (2, 0, 0),
        (0, -2, 0),
        (0, 2, 0),
        (0, 0, -2),
        (0, 0, 2),
    ],
    "5": [
        (0, 0, -2),
        (0, 0, 2),
        (0, 2, 0),
        (-1.732, -1, 0),
        (1.732, -1, 0),
    ],
    "4": [
        (-1, 0, -1),
        (1, 0, -1),
        (0, -1, 1),
        (0, 1, 1),
    ],
    "3": [
        (0, 2, 0),
        (-1.732, -1, 0),
        (1.732, -1, 0),
    ],
    "2": [
        (0, -2, 0),
        (0, 2, 0),
    ],
    "1": [
        (0, 0, 2),
    ],
}

SUNLIT_ODISK_POINT_AT_RADIUS = 3.0

SUNLIT_BLINDS_MAT_NAME = "SunlitBlindsMat"
SUNLIT_BAKE_MAT_NAME = "SunlitBakeMat"
SUNLIT_BAKE_IMG_NAME = "SunlitBakeImage"

def set_object_hide_render(ob, hide_state):
    ob.hide_render = hide_state

def set_object_list_hide_render(ob_list, hide_state):
    for ob in ob_list:
        set_object_hide_render(ob, hide_state)

def get_object_hide_render(ob):
    return ob.hide_render

def object_create_mesh(context, mesh_ob_name, mesh_verts):
    mesh_ob = bpy.data.meshes.new(mesh_ob_name+"_mesh")
    ob = bpy.data.objects.new(mesh_ob_name, mesh_ob)
    scene_link_object(context, ob)
    set_active_object(context, ob)
    select_object(ob)
    mesh_data = context.object.data
    bm = bmesh.new()
    for v_pos in mesh_verts:
        bm.verts.new(v_pos)
    bm.verts.ensure_lookup_table()

    bm.edges.new([bm.verts[0], bm.verts[1]])
    bm.edges.new([bm.verts[1], bm.verts[2]])
    bm.edges.new([bm.verts[2], bm.verts[0]])
    bm.faces.new([bm.verts[0], bm.verts[1], bm.verts[2]])

    bm.to_mesh(mesh_data)
    bm.free()
    return ob

def any_prepend_name_num(prepend_name, num):
    if num < 1:
        return prepend_name
    else:
        return prepend_name + '.' + str(num).zfill(3)

def obj_prepend_name_num(prepend_name, num):
    # test to find un-used prepend_name, within list of all objects' names
    for test_num in range(num, 999):
        test_obj_name = any_prepend_name_num(prepend_name, test_num)
        # if prepend_name not in the list then return the test_obj_name
        if bpy.data.objects.get(test_obj_name) is None:
            return test_obj_name

    # if no suitable prepend_name found after testing, then just return the string from the first attempt
    return any_prepend_name_num(prepend_name, num)

def get_num_from_name(name_str):
    length = len(name_str)
    if length > 4 and name_str[length-4] == '.':
        possible_digits = name_str[length-3:length]
        if possible_digits.isdigit():
            return int(possible_digits)
    return 0

# search all objects, by way of "bpy.data.objects", to get list of objects parented to obj
def get_objects_parented_to(obj, obj_name_prepend):
    found_obj_list = []
    for test_obj in bpy.data.objects:
        if test_obj.name.startswith(obj_name_prepend) and test_obj.parent == obj:
            found_obj_list.append(test_obj)
    return found_obj_list

# search all objects, by way of "bpy.data.objects", to get list of objects "bone parented" to armature's bone
def get_objects_parented_to_bone(armature, bone_name, obj_name_prepend):
    obj_list = []
    for ob in bpy.data.objects:
        if ob.name.startswith(obj_name_prepend) and ob.parent == armature and ob.parent_type == "BONE" and ob.parent_bone == bone_name:
            obj_list.append(ob)
    return obj_list

def get_rig_bone_num_for_obj(obj):
    if obj.parent == None or obj.parent_type != "BONE" or obj.parent_bone == "":
        return None
    return get_num_from_name(obj.parent_bone)

def get_sunlit_blinds_for_light(light_obj):
    light_num = get_rig_bone_num_for_obj(light_obj)
    if light_num is None:
        return None
    obj_list = []
    if light_obj.name.startswith(SUNLIT_SUN_PREPEND):
        obj_list = get_objects_parented_to_bone(light_obj.parent, any_prepend_name_num(SUNLIT_BONE_DIFF_CUBE, light_num), SUNLIT_SUN_BLINDS_PREPEND)
    elif light_obj.name.startswith(SUNLIT_ODISK_SUN_PREPEND):
        obj_list = get_objects_parented_to_bone(light_obj.parent, any_prepend_name_num(SUNLIT_BONE_ODISK, light_num), SUNLIT_ODISK_BLINDS_PREPEND)

    # hack: just return the first sunlit blinds found, there should be only one per light_obj
    if len(obj_list) < 1:
        return None
    return obj_list[0]

def get_sunlit_sensor_for_light(light_obj):
    light_num = get_rig_bone_num_for_obj(light_obj)
    if light_num is None:
        return None
    if is_sunlit_odisk(light_obj):
        obj_list = get_objects_parented_to_bone(light_obj.parent, any_prepend_name_num(SUNLIT_BONE_ODISK, light_num), SUNLIT_ODISK_PREPEND)
    else:
        obj_list = get_objects_parented_to_bone(light_obj.parent, any_prepend_name_num(SUNLIT_BONE_SENSOR, light_num), SUNLIT_SENSOR_PLANE_PREPEND)
    # hack: just return the first sunlit sensor found, there should be only one per light_obj
    if len(obj_list) < 1:
        return None
    return obj_list[0]

# Check for bones with names that match Sunlit Rig armature bone names.
# If armature's bone names reach minimum number of matches then return True.
def is_sunlit_armature(ob):
    b_name_match_count = 0
    if ob.type != "ARMATURE":
        return False
    for b_name in SUNLIT_BONE_ALL_NAMES:
        if ob.data.bones.get(b_name) != None:
            b_name_match_count += 1
            if b_name_match_count >= SUNLIT_BONE_MATCH_MIN:
                return True

def is_sunlit_odisk(ob):
    return ob.name.startswith(SUNLIT_ODISK_SUN_PREPEND)

def create_sunlit_armature(context, num_sun_lights, num_occluding_disks):
    widget_cube = create_widget_cube(context)
    widget_tri = create_widget_triangle(context)
    widget_plane = create_widget_plane(context)
    widget_cone = create_widget_cone(context)
    widget_circle = create_base_circle(context)

    old_3dview_mode = context.object.mode

    # create armature and enter EDIT mode
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    armature = context.active_object

    widget_cube.parent = armature
    widget_tri.parent = armature
    widget_plane.parent = armature
    widget_cone.parent = armature
    widget_circle.parent = armature

    # create bone to manipulate base sphere - the radius of sphere controls the distance to the blinds from the "origin"
    # sphere bone starts from initial bone "Bone", and is modified
    sphere_bone = armature.data.edit_bones[0]
    sphere_bone.name = SUNLIT_BONE_SPHERE
    # name may be different from SUNLIT_BONE_SPHERE, because of numbered duplicates, so get name now
    sphere_bone_name = sphere_bone.name
    sphere_bone.head = Vector(SUNLIT_BONE_HT_SPHERE[0])
    sphere_bone.tail = Vector(SUNLIT_BONE_HT_SPHERE[1])
    sphere_bone.layers = BONE_LAYER_ONLY_2

    # create bones for sun lights
    sun_bone_name_tuples = []
    for c in range(0, num_sun_lights):
        s_pivot_b_name = armature.data.edit_bones.new(name=SUNLIT_BONE_SUN_PIVOT)
        s_pivot_b_name.head = Vector(SUNLIT_BONE_HT_SUN_PIVOT[0])
        s_pivot_b_name.tail = Vector(SUNLIT_BONE_HT_SUN_PIVOT[1])
        s_pivot_b_name.layers = BONE_LAYER_ONLY_2

        s_targ_b_name = armature.data.edit_bones.new(name=SUNLIT_BONE_SUN_TARGET)
        s_targ_b_name.head = Vector(SUNLIT_BONE_HT_SUN_TARGET[0])
        s_targ_b_name.tail = Vector(SUNLIT_BONE_HT_SUN_TARGET[1])
        s_targ_b_name.show_wire = True

        diff_cube_b_name = armature.data.edit_bones.new(name=SUNLIT_BONE_DIFF_CUBE)
        diff_cube_b_name.head = Vector(SUNLIT_BONE_HT_DIFF_CUBE[0])
        diff_cube_b_name.tail = Vector(SUNLIT_BONE_HT_DIFF_CUBE[1])
        diff_cube_b_name.parent = s_pivot_b_name
        diff_cube_b_name.show_wire = True

        sensor_b_name = armature.data.edit_bones.new(name=SUNLIT_BONE_SENSOR)
        sensor_b_name.head = Vector(SUNLIT_BONE_HT_SENSOR[0])
        sensor_b_name.tail = Vector(SUNLIT_BONE_HT_SENSOR[1])
        sensor_b_name.parent = s_pivot_b_name
        sensor_b_name.show_wire = True

        lit_adjust_b_name = armature.data.edit_bones.new(name=SUNLIT_BONE_LIT_ADJUST)
        lit_adjust_b_name.head = Vector(SUNLIT_BONE_HT_LIT_ADJUST[0])
        lit_adjust_b_name.tail = Vector(SUNLIT_BONE_HT_LIT_ADJUST[1])
        lit_adjust_b_name.parent = s_pivot_b_name
        lit_adjust_b_name.show_wire = True

        sun_bone_name_tuples.append((s_pivot_b_name.name, s_targ_b_name.name, sensor_b_name.name, diff_cube_b_name.name, lit_adjust_b_name.name))

    # create bones for occluding disks
    odisk_bone_name_tuples = []
    for c in range(0, num_occluding_disks):
        odisk_pivot_b = armature.data.edit_bones.new(name=SUNLIT_BONE_ODISK_PIVOT)
        odisk_pivot_b.head = Vector(SUNLIT_BONE_HT_ODISK_PIVOT[0])
        odisk_pivot_b.tail = Vector(SUNLIT_BONE_HT_ODISK_PIVOT[1])
        odisk_pivot_b.layers = BONE_LAYER_ONLY_2

        odisk_target_b = armature.data.edit_bones.new(name=SUNLIT_BONE_ODISK_TARGET)
        odisk_target_b.head = Vector(SUNLIT_BONE_HT_ODISK_TARGET[0])
        odisk_target_b.tail = Vector(SUNLIT_BONE_HT_ODISK_TARGET[1])
        odisk_target_b.show_wire = True

        odisk_b = armature.data.edit_bones.new(name=SUNLIT_BONE_ODISK)
        odisk_b.head = Vector(SUNLIT_BONE_HT_ODISK[0])
        odisk_b.tail = Vector(SUNLIT_BONE_HT_ODISK[1])
        odisk_b.parent = odisk_pivot_b
        odisk_b.show_wire = True

        odisk_light_b = armature.data.edit_bones.new(name=SUNLIT_BONE_ODISK_LIGHT)
        odisk_light_b.head = Vector(SUNLIT_BONE_HT_ODISK_LIGHT[0])
        odisk_light_b.tail = Vector(SUNLIT_BONE_HT_ODISK_LIGHT[1])
        odisk_light_b.parent = odisk_pivot_b
        odisk_light_b.show_wire = True

        odisk_bone_name_tuples.append((odisk_pivot_b.name, odisk_target_b.name, odisk_b.name, odisk_light_b.name))
        c = c + 1

    # sun bone constraints and bone custom shapes
    bpy.ops.object.mode_set(mode='POSE')
    for s_pivot_b_name, s_targ_b_name, sensor_b_name, diff_cube_b_name, lit_adjust_b_name in sun_bone_name_tuples:
        sp_tt_const = armature.pose.bones[s_pivot_b_name].constraints.new(type='TRACK_TO')
        sp_tt_const.track_axis = "TRACK_Y"
        sp_tt_const.up_axis = "UP_Z"
        sp_tt_const.target = armature
        sp_tt_const.subtarget = s_targ_b_name

        diff_cube_tt_const = armature.pose.bones[diff_cube_b_name].constraints.new(type='TRACK_TO')
        diff_cube_tt_const.target = armature
        diff_cube_tt_const.subtarget = sphere_bone_name
        diff_cube_tt_const.track_axis = "TRACK_NEGATIVE_Y"
        diff_cube_tt_const.up_axis = "UP_Z"
        # Diff Cube bone: only Y axis is unlocked, so Blinds can be easily moved toward/away from the "origin"
        armature.pose.bones[diff_cube_b_name].lock_location[0] = True
        armature.pose.bones[diff_cube_b_name].lock_location[2] = True

        # Sensor bone: only Y axis is unlocked, so sensor can be easily moved toward/away from the "origin"
        armature.pose.bones[sensor_b_name].lock_location[0] = True
        armature.pose.bones[sensor_b_name].lock_location[2] = True

        # apply custom bone shapes to Sun Target, Sensor, and Blinds (apply to Blinds by way of Diff Cube),
        armature.pose.bones[s_targ_b_name].custom_shape = bpy.data.objects[widget_cube.name]
        armature.pose.bones[diff_cube_b_name].custom_shape = bpy.data.objects[widget_plane.name]
        armature.pose.bones[sensor_b_name].custom_shape = bpy.data.objects[widget_tri.name]
        armature.pose.bones[lit_adjust_b_name].custom_shape = bpy.data.objects[widget_cone.name]

    # occluding disk bone constraints and bone custom shapes
    for odisk_pivot_b_name, odisk_targ_b_name, odisk_b_name, odisk_light_b_name in odisk_bone_name_tuples:
        odisk_pivot_tt_const = armature.pose.bones[odisk_pivot_b_name].constraints.new(type='TRACK_TO')
        odisk_pivot_tt_const.track_axis = "TRACK_Y"
        odisk_pivot_tt_const.up_axis = "UP_Z"
        odisk_pivot_tt_const.target = armature
        odisk_pivot_tt_const.subtarget = odisk_targ_b_name

        armature.pose.bones[odisk_b_name].lock_location[0] = True
        armature.pose.bones[odisk_b_name].lock_location[2] = True

        armature.pose.bones[odisk_light_b_name].lock_location[0] = True
        armature.pose.bones[odisk_light_b_name].lock_location[2] = True

        armature.pose.bones[odisk_targ_b_name].custom_shape = bpy.data.objects[widget_cube.name]
        armature.pose.bones[odisk_b_name].custom_shape = bpy.data.objects[widget_circle.name]
        armature.pose.bones[odisk_light_b_name].custom_shape = bpy.data.objects[widget_cone.name]

    bpy.ops.object.mode_set(mode=old_3dview_mode)

    return armature, sphere_bone_name, sun_bone_name_tuples, odisk_bone_name_tuples

def create_widget_cube(context):
    widget_cube = create_object_cube(context, SUNLIT_WGT_CUBE_NAME, 0.1, (0, 0, 0))
    set_object_display_type(widget_cube, "WIRE")
    set_object_hide_view(widget_cube, True)
    set_object_hide_render(widget_cube, True)
    return widget_cube

def create_widget_triangle(context):
    old_3dview_mode = context.object.mode
    widget_tri = create_object_plane(context, SUNLIT_WGT_TRI_NAME, 1, (0, 0, 0), False)
    bpy.ops.object.mode_set(mode="EDIT")
    mesh_data = widget_tri.data
    bm = bmesh.from_edit_mesh(mesh_data)
    bmesh_delete_verts(bm, bm.verts)
    # add triangle vertexes
    for v_pos in SUNLIT_WGT_TRI_VERTS:
        bm.verts.new(v_pos)
    # ensure that vertexes can be indexed, e.g. bm.verts[1]
    bm.verts.ensure_lookup_table()
    # add edges
    bm.edges.new([bm.verts[0], bm.verts[1]])
    bm.edges.new([bm.verts[1], bm.verts[2]])
    bm.edges.new([bm.verts[2], bm.verts[0]])
    # add triangle face
    bm.faces.new([bm.verts[0], bm.verts[1], bm.verts[2]])
    # update mesh object, and free bmesh to prevent further access to bm
    bmesh.update_edit_mesh(mesh=mesh_data, destructive=True)
    bm.free()
    bpy.ops.object.mode_set(mode=old_3dview_mode)
    set_object_display_type(widget_tri, "WIRE")
    set_object_hide_view(widget_tri, True)
    set_object_hide_render(widget_tri, True)
    return widget_tri

def create_widget_plane(context):
    widget_plane = create_object_plane(context, SUNLIT_WGT_PLANE_NAME, 0.33, (0, 0, 0), False)
    widget_plane.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    set_object_display_type(widget_plane, "WIRE")
    set_object_hide_view(widget_plane, True)
    set_object_hide_render(widget_plane, True)
    return widget_plane

def create_widget_cone(context):
    bpy.ops.mesh.primitive_cone_add(radius1=0.2, radius2=0, depth = 0.4, location=(0, 0, 0))
    widget_cone = context.active_object
    widget_cone.name = SUNLIT_WGT_CONE_NAME
    widget_cone.rotation_euler = (math.radians(270), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    set_object_display_type(widget_cone, "WIRE")
    set_object_hide_view(widget_cone, True)
    set_object_hide_render(widget_cone, True)
    return widget_cone

def create_base_circle(context):
    bpy.ops.mesh.primitive_circle_add(radius=0.3, location=(0, 0, 0))
    widget_circle = context.active_object
    widget_circle.rotation_euler = (math.radians(270), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    widget_circle.name = SUNLIT_WGT_CIRCLE_NAME
    set_object_display_type(widget_circle, "WIRE")
    set_object_hide_view(widget_circle, True)
    set_object_hide_render(widget_circle, True)
    return widget_circle

def is_sunlit_rig_widget(obj):
    return obj.name.startswith(SUNLIT_WGT_PREPEND)

# "rig" includes armature object, widget objects, and objects parented to the armature (e.g. meshes, lights)
def create_sunlit_rig(context, hemisphere_only, num_suns, num_sphere_subdiv, num_occluding_disks, odisk_include_sun,
        default_sun_energy, default_sun_angle, default_odisk_sun_energy, default_odisk_sun_angle, allow_drivers,
        sun_sensor_image_width, sun_sensor_image_height, odisk_sensor_image_width, odisk_sensor_image_height,
        sun_blinds_len, odisk_blinds_len):
    # create sl_armature to combine/control objects
    sl_armature, sphere_bone_name, sun_bone_name_tuples, odisk_bone_name_tuples = create_sunlit_armature(context,
        num_suns, num_occluding_disks)

    # create base sphere, with which sun blinds planes will intersect
    base_sphere = create_object_icosphere(context, obj_prepend_name_num(SUNLIT_BASE_SPHERE_PREPEND, 0), num_sphere_subdiv,
        SUNLIT_BASE_SPHERE_RADIUS, SUNLIT_BASE_SPHERE_OFFSET)
    base_sphere.parent = sl_armature
    base_sphere.parent_type = "BONE"
    base_sphere.parent_bone = sphere_bone_name
    # create "difference cubes" (diff cubes for short) that will be used in booleans to carve out "blinds planes"
    diff_cubes_list = create_sunlit_diff_cubes(context, sl_armature, sun_bone_name_tuples, SUNLIT_DCUBE_PREPEND)
    sensor_planes = create_sunlit_planes(context, sl_armature, sun_bone_name_tuples, SUNLIT_SENSOR_PLANE_PREPEND,
        SUNLIT_SENSOR_PLANE_RADIUS, SUNLIT_SENSOR_OFFSET, False)
    for plane in sensor_planes:
        create_sensor_material_on_obj(plane, sun_sensor_image_width, sun_sensor_image_height)
    create_sun_lights(context, sl_armature, sun_bone_name_tuples, SUNLIT_SUN_PREPEND,
        SUNLIT_SUN_OFFSET, default_sun_energy, default_sun_angle)

    # create sun_blinds_list
    sun_blinds_list = create_sunlit_planes(context, sl_armature, sun_bone_name_tuples, SUNLIT_SUN_BLINDS_PREPEND,
        SUNLIT_SUN_BLINDS_PLANE_RADIUS, SUNLIT_SUN_BLINDS_PLANE_OFFSET, True)
    add_blinds_material_to_obj_list(sun_blinds_list)
    # create sun_blinds_list' object modifiers
    create_sphere_plane_booleans(base_sphere, sun_blinds_list)
    create_plane_diff_cube_booleans(sun_blinds_list, diff_cubes_list)
    add_extrude_bools_to_sun_blinds(sun_blinds_list, sl_armature, sun_blinds_len, allow_drivers)

    if num_suns > 0:
        if hemisphere_only:
            # setup lighting default pointing directions, if light pointing data is found
            if str(num_suns) in SUNLIT_HEMI_SUN_POINTDIR_LIST:
                point_direction_list = SUNLIT_HEMI_SUN_POINTDIR_LIST[str(num_suns)]
            # default of max number of suns pointing directions list to work with
            else:
                point_direction_list = SUNLIT_HEMI_SUN_POINTDIR_LIST[str(SUNLIT_MAX_SUN_POINTDIR)]
        else:
            if str(num_suns) in SUNLIT_FULL_SUN_POINTDIR_LIST:
                point_direction_list = SUNLIT_FULL_SUN_POINTDIR_LIST[str(num_suns)]
            # use Fibonacci sphere if number not in preset list
            else:
                point_direction_list = get_fibonacci_sphere_points(num_suns, 2.0)

        set_point_at_locations(context, sl_armature, sun_bone_name_tuples, point_direction_list,
            SUNLIT_EXTRA_POINTDIR)

        fix_diff_cube_bone_loc(context, sl_armature, sun_bone_name_tuples, SUNLIT_FIX_DIFF_CUBE_LOC)

    # The bone setups and parenting were done in worldspace with Z axis as the up axis, but inside the sl_armature the
    # Y axis is the up axis - so fix it.
    # deselect all, then select only the sl_armature and fix the rotation
    #bpy.ops.object.select_all(action='DESELECT')
    #set_active_object(context, sl_armature)
    #select_object(sl_armature)
    sl_armature.rotation_euler = (math.radians(270), 0, 0)
    #bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # hide objects that distract the user and/or should not be rendered
    set_object_list_hide_view(diff_cubes_list, True)
    set_object_list_hide_render(diff_cubes_list, True)
    set_object_hide_view(base_sphere, True)
    set_object_hide_render(base_sphere, True)
    set_object_list_hide_view(sun_blinds_list, True)

    # create occluding disks and set their default pointing directions
    if num_occluding_disks > 0:
        odisk_list, odisk_blinds_list = create_occluding_disks(context, sl_armature, odisk_bone_name_tuples, odisk_include_sun,
            default_odisk_sun_energy, default_odisk_sun_angle, allow_drivers, odisk_sensor_image_width, odisk_sensor_image_height,
            odisk_blinds_len)
        set_odisk_point_at_locations(context, sl_armature, odisk_bone_name_tuples)
        set_object_list_hide_view(odisk_blinds_list, True)

    # create camera, to use for setting ODisk sizes
    create_sunlit_rig_camera(context, sl_armature)

def create_sunlit_rig_camera(context, sl_armature):
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    rig_cam = context.active_object
    rig_cam.name = SUNLIT_CAMERA_PREPEND
    rig_cam.parent = sl_armature
    set_object_hide_view(rig_cam, True)
    tt_const = rig_cam.constraints.new(type="TRACK_TO")
    tt_const.name = SUNLIT_CAMERA_TTC_PREPEND
    tt_const.track_axis = "TRACK_NEGATIVE_Z"
    tt_const.up_axis = "UP_Y"

def set_sunlit_cam_odisk_target(sl_armature, odisk_num):
    cam_list = get_objects_parented_to(sl_armature, SUNLIT_CAMERA_PREPEND)
    obj_list = get_objects_parented_to_bone(sl_armature, any_prepend_name_num(SUNLIT_BONE_ODISK, odisk_num), SUNLIT_ODISK_PREPEND)
    if len(cam_list) < 1 or len(obj_list) < 1:
        print("cam is None or obj_target is None")
        return

    tt_const = cam_list[0].constraints.get(SUNLIT_CAMERA_TTC_PREPEND)
    if tt_const != None:
        tt_const.target = obj_list[0]

def get_fibonacci_sphere_points(num_points, sphere_radius):
    points = []
    phi = math.pi * (3. - math.sqrt(5.))        # golden angle in radians
    for i in range(num_points):
        y = 1 - (i / float(num_points - 1)) * 2 # y goes from 1 to -1
        latitude_radius = math.sqrt(1 - y * y)  # radius at y (radius of circle that would form latitude line on a sphere of radius=1)
        theta = phi * i                         # golden angle increment
        x = math.cos(theta) * latitude_radius
        z = math.sin(theta) * latitude_radius
        points.append((x*sphere_radius, y*sphere_radius, z*sphere_radius))
    return points

def create_sunlit_planes(context, sl_arm, bone_tuples, prepend_str, p_radius, loc, is_blinds):
    planes = []

    c = 0
    for s_pivot_b, s_targ_b, sensor_b, diff_cube_b, lit_adjust_b in bone_tuples:
        # calculate UVs for the plane object if it is not a "blinds" object
        calc_uvs = not is_blinds
        # create the plane with the given options
        new_obj = create_object_plane(context, obj_prepend_name_num(prepend_str, c), p_radius, loc, calc_uvs)
        new_obj.rotation_euler = (math.radians(270), 0, 0)
        new_obj.parent = sl_arm
        new_obj.parent_type = "BONE"
        if is_blinds:
            new_obj.parent_bone = diff_cube_b
        else:
            new_obj.parent_bone = sensor_b
        planes.append(new_obj)
        c = c + 1

    return planes

def create_sunlit_diff_cubes(context, sl_arm, sun_bone_name_tuples, prepend_str):
    diff_cubes = []

    c = 0
    for s_pivot_b, s_targ_b, sensor_b, diff_cube_b, lit_adjust_b in sun_bone_name_tuples:
        new_obj = create_object_cube(context, obj_prepend_name_num(prepend_str, c), 1, SUNLIT_DIFF_CUBE_OFFSET)
        context.active_object.parent = sl_arm
        context.active_object.parent_type = "BONE"
        context.active_object.parent_bone = diff_cube_b

        diff_cubes.append(context.active_object)
        c = c + 1

    return diff_cubes

def create_sun_lights(context, sl_arm, sun_bone_name_tuples, prepend_str, loc, sun_energy, sun_angle):
    lights = []

    c = 0
    for s_pivot_b, s_targ_b, sensor_b, diff_cube_b, lit_adjust_b in sun_bone_name_tuples:
        sun_light = create_object_light(context, obj_prepend_name_num(prepend_str, c), "SUN", 1, loc)
        sun_light.rotation_euler = (math.radians(270), 0, 0)
        sun_light.data.energy = sun_energy
        #sun_light.data.angle = sun_angle
        sun_light.parent = sl_arm
        sun_light.parent_type = "BONE"
        sun_light.parent_bone = lit_adjust_b
        lights.append(sun_light)
        c = c + 1

    return lights

def set_point_at_locations(context, sl_arm, bone_tuples, loc_list, extra_loc):
    old_3dview_mode = context.object.mode
    set_active_object(context, sl_arm)
    bpy.ops.object.mode_set(mode='POSE')
    c = 0
    for s_pivot_b, s_targ_b, sensor_b, diff_cube_b, lit_adjust_b in bone_tuples:
        if c >= len(loc_list):
            sl_arm.pose.bones[s_targ_b].location = extra_loc
        else:
            sl_arm.pose.bones[s_targ_b].location = loc_list[c]
        c = c + 1
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def fix_diff_cube_bone_loc(context, sl_arm, bone_tuples, fix_loc):
    old_3dview_mode = context.object.mode
    set_active_object(context, sl_arm)
    bpy.ops.object.mode_set(mode='POSE')
    for s_pivot_b, s_targ_b, sensor_b, diff_cube_b, lit_adjust_b in bone_tuples:
            sl_arm.pose.bones[diff_cube_b].location = fix_loc
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def add_boolean_mod(mod_obj, target_obj, mod_name, bool_op):
    b_mod = mod_obj.modifiers.new(mod_name, "BOOLEAN")
    b_mod.operation = bool_op
    b_mod.object = target_obj

def create_sphere_plane_booleans(sphere_obj, planes_obj_list):
    for plane in planes_obj_list:
        add_boolean_mod(plane, sphere_obj, SUNLIT_MODNAME_SPHERE, "INTERSECT")

def create_plane_diff_cube_booleans(planes_obj_list, diff_cube_obj_list):
    p = 0
    for plane in planes_obj_list:
        dc = 0
        for diff_cube in diff_cube_obj_list:
            # only add the boolean modifier if the difference cube is not attached to this plane,
            # assuming the planes and diff cubes are in the same order in their respective arrays
            if dc != p:
                add_boolean_mod(plane, diff_cube, SUNLIT_MODNAME_DC, "DIFFERENCE")
            dc = dc + 1
        p = p + 1

def add_extrude_bools_to_sun_blinds(blinds_plane_list, sl_armature, sun_blinds_len, allow_drivers):
    c = 0
    for plane in blinds_plane_list:
        w_mod = plane.modifiers.new(SUNLIT_MODNAME_B_WIRE, "WIREFRAME")
        w_mod.thickness = 0

        s_mod = plane.modifiers.new(SUNLIT_MODNAME_B_SOLID, "SOLIDIFY")
        s_mod.thickness = sun_blinds_len
        s_mod.offset = 1 - (2 / sun_blinds_len)

        bone_num =  get_rig_bone_num_for_obj(plane)
        if allow_drivers:
            add_regular_blinds_drivers(s_mod, sl_armature, any_prepend_name_num(SUNLIT_BONE_DIFF_CUBE, bone_num),
                sun_blinds_len)

        object_add_modifier_taper(plane, SUNLIT_MODNAME_B_SIMPDEF, sun_blinds_len)
        c = c + 1

def get_blinds_material():
    blinds_mat = bpy.data.materials.get(SUNLIT_BLINDS_MAT_NAME)
    if blinds_mat is None:
        blinds_mat = bpy.data.materials.new(name=SUNLIT_BLINDS_MAT_NAME)
        set_mat_diffuse_color(blinds_mat, (0, 0, 0, 0))
    return blinds_mat

def add_blinds_material_to_obj(obj):
    blinds_mat = get_blinds_material()
    obj.data.materials.append(blinds_mat)

def add_blinds_material_to_obj_list(obj_list):
    blinds_mat = get_blinds_material()
    for ob in obj_list:
        ob.data.materials.append(blinds_mat)

# Create a two-sided material for sensor, so this code can be used for regular sensors and "occluding disk sensor":
#    -diffuse shader on front face
#    -zero shader (disconnected shader) on back face
def create_sensor_material_on_obj(ob, sun_sensor_image_width, sun_sensor_image_height):
    # new material for each object, because each sensor, or "bake plane", needs separate image for bake
    new_bake_mat = bpy.data.materials.new(name=SUNLIT_BAKE_MAT_NAME)
    new_bake_mat.use_nodes = True

    # ---
    # Add mix shader with Backfacing input from Input-Geometry material node, to make the back-facing material dark,
    # and the front-facing material becomes the sensor material:

    # material shader nodes
    tree_nodes = new_bake_mat.node_tree.nodes
    tree_nodes.clear()
    new_nodes = {}

    node = tree_nodes.new(type="ShaderNodeOutputMaterial")
    node.location = (340, 612)
    new_nodes["Material Output"] = node

    node = tree_nodes.new(type="ShaderNodeNewGeometry")
    node.location = (-82, 628)
    new_nodes["Geometry"] = node

    node = tree_nodes.new(type="ShaderNodeBsdfDiffuse")
    node.location = (-188, 384)
    new_nodes["Diffuse BSDF"] = node

    node = tree_nodes.new(type="ShaderNodeTexCoord")
    node.location = (-752, 102)
    new_nodes["Texture Coordinate"] = node

    node = tree_nodes.new(type="ShaderNodeTexImage")
    node.location = (-552, 242)
    # new image for each new material
    node.image = bpy.data.images.new(name=SUNLIT_BAKE_IMG_NAME, width=sun_sensor_image_width,
        height=sun_sensor_image_height, alpha=False)
    image_pack_image(node.image)
    new_nodes["Image Texture"] = node

    node = tree_nodes.new(type="ShaderNodeMixShader")
    node.location = (150, 500)
    new_nodes["Mix Shader"] = node

    # links between nodes
    tree_links = new_bake_mat.node_tree.links
    tree_links.new(new_nodes["Mix Shader"].outputs[0], new_nodes["Material Output"].inputs[0])
    tree_links.new(new_nodes["Geometry"].outputs[6], new_nodes["Mix Shader"].inputs[0])
    tree_links.new(new_nodes["Diffuse BSDF"].outputs[0], new_nodes["Mix Shader"].inputs[1])
    tree_links.new(new_nodes["Texture Coordinate"].outputs[2], new_nodes["Image Texture"].inputs[0])
    #
    # ---

    # add new sensor material to object
    ob.data.materials.append(new_bake_mat)

def get_shader_node_mat_output(nodes_list):
    for node in nodes_list:
        if node.type == "OUTPUT_MATERIAL":
            return node
    return None

def create_occluding_disks(context, sl_arm, odisk_bone_name_tuples, odisk_include_sun, odisk_sun_energy,
        odisk_sun_angle, add_odisk_taper_driver, odisk_sensor_image_width, odisk_sensor_image_height, odisk_blinds_len):
    odisk_list = []
    odisk_blinds_list = []

    c = 0
    for odisk_pivot_bone_name, odisk_targ_bone_name, odisk_bone_name, odisk_lit_adjust_bone_name in odisk_bone_name_tuples:
        # create occluding disk from filled in circle
        bpy.ops.mesh.primitive_circle_add(radius=SUNLIT_ODISK_RADIUS, calc_uvs=True, fill_type='NGON',
            location=SUNLIT_ODISK_OFFSET)
        odisk = context.active_object
        odisk.name = obj_prepend_name_num(SUNLIT_ODISK_PREPEND, c)
        odisk.rotation_euler = (math.radians(270), 0, 0)
        odisk.parent = sl_arm
        odisk.parent_type = "BONE"
        odisk.parent_bone = odisk_bone_name
        create_sensor_material_on_obj(odisk, odisk_sensor_image_width, odisk_sensor_image_height)

        # create blinds to go with occluding disk
        bpy.ops.mesh.primitive_circle_add(radius=SUNLIT_ODISK_RADIUS, fill_type='NGON', location=SUNLIT_ODISK_OFFSET)
        odisk_blinds = context.active_object
        odisk_blinds.name = obj_prepend_name_num(SUNLIT_ODISK_BLINDS_PREPEND, c)
        odisk_blinds.rotation_euler = (math.radians(270), 0, 0)
        odisk_blinds.parent = sl_arm
        odisk_blinds.parent_type = "BONE"
        odisk_blinds.parent_bone = odisk_bone_name
        w_mod = odisk_blinds.modifiers.new(SUNLIT_MODNAME_B_WIRE, "WIREFRAME")
        w_mod.thickness = 0
        s_mod = odisk_blinds.modifiers.new(SUNLIT_MODNAME_B_SOLID, "SOLIDIFY")
        s_mod.offset = 1
        s_mod.thickness = odisk_blinds_len
        d_mod = object_add_modifier_taper(odisk_blinds, SUNLIT_MODNAME_B_SIMPDEF, 0.052)
        if add_odisk_taper_driver:
            add_odisk_blinds_taper_driver(d_mod, sl_arm, odisk_bone_name, odisk_blinds_len)

        add_blinds_material_to_obj(odisk_blinds)

        if odisk_include_sun:
            # create Sun to attach to occluding disk
            odisk_sun = create_object_light(context, obj_prepend_name_num(SUNLIT_ODISK_SUN_PREPEND, c), "SUN", 1, SUNLIT_ODISK_OFFSET)
            odisk_sun.rotation_euler = (math.radians(270), 0, 0)
            odisk_sun.data.energy = odisk_sun_energy
            #odisk_sun.data.anle = odisk_sun_angle
            odisk_sun.parent = sl_arm
            odisk_sun.parent_type = "BONE"
            odisk_sun.parent_bone = odisk_lit_adjust_bone_name
            set_light_angular_diameter(odisk_sun, odisk_sun_angle)

        odisk_list.append(odisk)
        odisk_blinds_list.append(odisk_blinds)

        c = c + 1

    return odisk_list, odisk_blinds_list

def add_regular_blinds_drivers(solid_mod, armature, diff_cube_bone_name, blinds_length):
    d = solid_mod.driver_add("thickness").driver
    v1 = d.variables.new()
    v1.name                 = "var1"
    v1.targets[0].id        = armature
    v1.targets[0].data_path = "pose.bones[\""+diff_cube_bone_name+"\"].location.y"
    d.expression = str(blinds_length) + "  * (1 + " + v1.name+")"

def add_odisk_blinds_taper_driver(source_modifier, armature, odisk_bone_name, odisk_blinds_len):
    d = source_modifier.driver_add("factor").driver
    v1 = d.variables.new()
    v1.name                 = "var1"
    v1.targets[0].id        = armature
    v1.targets[0].data_path = "pose.bones[\""+odisk_bone_name+"\"].scale.x"
    v2 = d.variables.new()
    v2.name                 = "var2"
    v2.targets[0].id        = armature
    v2.targets[0].data_path = "pose.bones[\""+odisk_bone_name+"\"].scale.y"
    # multiply by 11/300, verified this by scaling up the ODisk sensor bone
    d.expression = "sqrt("+v1.name+" * "+v1.name+" + "+v2.name+" * "+v2.name+") * " + str(odisk_blinds_len * 11 / 300)

def set_odisk_point_at_locations(context, sl_arm, odisk_bone_name_tuples):
    old_3dview_mode = context.object.mode
    set_active_object(context, sl_arm)

    bpy.ops.object.mode_set(mode='POSE')
    total = len(odisk_bone_name_tuples)
    c = 0
    for odisk_pivot_b_name, odisk_target_b_name, odisk_b_name, odisk_lit_adjust_bone_name in odisk_bone_name_tuples:
        sl_arm.pose.bones[odisk_target_b_name].location[0] = math.cos(c / total * 2 * math.pi) * SUNLIT_ODISK_POINT_AT_RADIUS
        sl_arm.pose.bones[odisk_target_b_name].location[1] = math.sin(c / total * 2 * math.pi) * SUNLIT_ODISK_POINT_AT_RADIUS
        sl_arm.pose.bones[odisk_target_b_name].location[2] = 0
        c = c + 1
    bpy.ops.object.mode_set(mode=old_3dview_mode)

def bake_sunlit_sensors(context, sensors, sensor_bake_samples, lights_to_hide):
    if len(sensors) < 1:
        return
    render_hide_lit_data = hide_render_lights(True, lights_to_hide)
    bake_sunlit_sensor_images(context, sensors, sensor_bake_samples)
    undo_hide_render_lights(render_hide_lit_data)

def bake_select_sunlit_sensors(context, sensor_bake_samples, hide_all_lights):
    if hide_all_lights:
        lights = get_all_lights()
    else:
        lights = get_sunlit_suns_from_selected(context)
    sensors = get_sunlit_sensors_from_selected(context)
    # "hidden from render" meshes will cause error if baked, so ignore them - and raise warning
    vis_sensors = []
    warnings = []
    for s in sensors:
        if get_object_hide_render(s):
            warnings.append("Sunlit Image Sensor Mesh not baked, make mesh 'render visible' before baking, mesh named: " + s.name)
        else:
            vis_sensors.append(s)
    bake_sunlit_sensors(context, vis_sensors, sensor_bake_samples, lights)
    return warnings

def bake_sunlit_armature_list_sensors(context, sensor_bake_samples, hide_all_lights, armature_list):
    if hide_all_lights:
        lights = get_all_lights()
    else:
        lights = get_sunlit_suns_from_selected(context)
    sensors = []
    for armature in armature_list:
        sensors = sensors + get_sunlit_regular_sensors_from_armature(armature) + get_sunlit_odisk_sensors_from_armature(armature)
    vis_sensors = []
    warnings = []
    for s in sensors:
        if get_object_hide_render(s):
            warnings.append("Sunlit Image Sensor Mesh not baked, make mesh 'render visible' before baking, mesh named: " + s.name)
        else:
            vis_sensors.append(s)
    bake_sunlit_sensors(context, sensors, sensor_bake_samples, lights)
    return warnings

def hide_render_lights(new_hide_state, lights):
    hide_light_data = []

    # save old states
    for lit in lights:
        # append a tuple to store the old light object and it's state
        hide_light_data.append((lit, get_object_hide_render(lit)))
        # hide the light object from render pass
        set_object_hide_render(lit, new_hide_state)

    # return old states of lights
    return hide_light_data

def undo_hide_render_lights(hide_light_data):
    # restore old states
    for (lit, lit_hide_render_state) in hide_light_data:
        set_object_hide_render(lit, lit_hide_render_state)

# Important Note:
# If a HDRI is being baked to Sun lights, then all other light sources will adversely affect the bake to image process.
# To get a clean bake (i.e. no unwanted light), ensure all scene lights are turned off (i.e. hide lights from render)
# before baking to image.
def bake_sunlit_sensor_images(context, obj_list, sensor_bake_samples):
    if len(obj_list) < 1:
        return
    bpy.ops.object.select_all(action='DESELECT')
    select_objects(obj_list)
    # set active object to an object that will be baked, so that bpy,ops.object.bake does not error with 'incorrect context'
    set_active_object(context, obj_list[0])

    old_use_pass_direct = context.scene.render.bake.use_pass_direct
    old_use_pass_indirect = context.scene.render.bake.use_pass_indirect
    old_use_pass_color = context.scene.render.bake.use_pass_color
    context.scene.render.bake.use_pass_direct = True
    context.scene.render.bake.use_pass_indirect = True
    context.scene.render.bake.use_pass_color = False

    prev_samples = context.scene.cycles.samples
    context.scene.cycles.samples = sensor_bake_samples
    bpy.ops.object.bake(type="DIFFUSE")
    context.scene.cycles.samples = prev_samples

    context.scene.render.bake.use_pass_direct = old_use_pass_direct
    context.scene.render.bake.use_pass_indirect = old_use_pass_indirect
    context.scene.render.bake.use_pass_color = old_use_pass_color

def set_sun_color_data(keyframe_color, sample_width_pct, sample_height_pct, odisk_sample_width_pct, odisk_sample_height_pct, sun_lights):
    for light in sun_lights:
        sensor = get_sunlit_sensor_for_light(light)
        if sensor is None:
            continue
        plane_img = get_sunlit_bake_image_for_plane(sensor)
        if plane_img is None:
            continue

        # set sun color
        if is_sunlit_odisk:
            set_light_color(light, get_color_sample_from_image(plane_img,
                math.floor(plane_img.size[0] * odisk_sample_width_pct),
                math.floor(plane_img.size[1] * odisk_sample_height_pct)))
        else:
            set_light_color(light, get_color_sample_from_image(plane_img,
                math.floor(plane_img.size[0] * sample_width_pct),
                math.floor(plane_img.size[1] * sample_height_pct)))

        # add keyframe if needed
        if keyframe_color:
            keyframe_light_color(light)

# rectangle sample, sample width and height given in pixels
def get_color_sample_from_image(img, sample_w, sample_h):
    # prevent error of sampling outside image pixels
    if sample_w > img.size[0]:
        sample_w = img.size[0]
    if sample_h > img.size[1]:
        sample_h = img.size[1]
    num_pixels = sample_w * sample_h

    # sample centered at middle of image pixels
    mid_x = math.floor(img.size[0] / 2)
    mid_y = math.floor(img.size[1] / 2)

    # get average color sample from image pixels, and average to get avg_sample_color
    asc = (0, 0, 0)
    low_x = mid_x-math.floor(sample_w/2)
    low_y = mid_y-math.floor(sample_h/2)
    for y in range(low_y, low_y+sample_h):
        for x in range(low_x, low_x+sample_w):
            # multiply by 4 because RGBA
            px_offset = (y * img.size[0] + x) * 4
            asc = (asc[0]+img.pixels[px_offset], asc[1]+img.pixels[px_offset+1], asc[2]+img.pixels[px_offset+2])
    # return sample average
    return (asc[0] / num_pixels, asc[1] / num_pixels, asc[2] / num_pixels)

def set_select_sun_color_data(context, keyframe_color, sample_width_pct, sample_height_pct, odisk_sample_width_pct,
        odisk_sample_height_pct):
    set_sun_color_data(keyframe_color, sample_width_pct, sample_height_pct, odisk_sample_width_pct, odisk_sample_height_pct,
        get_sunlit_suns_from_selected(context))

def set_sunlit_armature_sun_color_data(keyframe_color, sample_width_pct, sample_height_pct, odisk_sample_width_pct,
        odisk_sample_height_pct, armature):
    set_sun_color_data(keyframe_color, sample_width_pct, sample_height_pct, odisk_sample_width_pct, odisk_sample_height_pct,
        get_sunlit_suns_from_armature(armature))

def set_sunlit_sun_angular_diameter(context, light_list, keyframe_angular_diameter):
    for light in light_list:
        # if center point is not found, then skip this light
        if light.parent is None or is_sunlit_armature(light.parent) == False:
            continue
        center_point = light.parent.matrix_world.to_translation()
        blinds = get_sunlit_blinds_for_light(light)
        if blinds is None:
            continue
        ad = get_light_angular_diameter_from_blinds(context, center_point, blinds)
        set_light_angular_diameter(light, ad)
        if keyframe_angular_diameter:
            keyframe_light_angular_diameter(light)

def get_sunlit_center_for_light(light):
    # if no armature from which to get center point, then skip this light
    if light.parent is None:
        return None
    return light.parent.location

# Get the angular diameter of the light (i.e. max angle difference of light coming from sun, relative to original
# sun light object's angle).
# Do this by finding the max difference in angle between the "walls" of a "blinds" object.
# i.e. Get the reverse cosine of the max dot product between center_point and end points of blinds.
#     Also, improve the process by getting vectors for directions of vertexes from the center_point, and calculating
#     the distance halfway between min and max in order to filter out unneeded/error-causing vertexes. Halfway is just
#     a good, easy way to filter between wrong vertexes (near vertexes), and correct vertexes (far away vertexes).
def get_light_angular_diameter_from_blinds(context, center_point, mesh_obj):
    obj_mod_mesh = get_mesh_post_modifiers(context, mesh_obj)
    # calculate delta for each vertex, and get statistical min/max magnitudes
    v_deltas = []
    min_delta_mag = -1
    max_delta_mag = -1
    for v in obj_mod_mesh.vertices:
        vert_world_location = matrix_vector_mult(mesh_obj.matrix_world, v.co)
        delta = vert_world_location - center_point
        if min_delta_mag == -1 or delta.magnitude <= min_delta_mag:
            min_delta_mag = delta.magnitude
        if max_delta_mag == -1 or delta.magnitude >= max_delta_mag:
            max_delta_mag = delta.magnitude
        v_deltas.append(delta)
    bpy.data.meshes.remove(obj_mod_mesh)
    # filter out vertexes that are too close to be usable for angle calcs
    final_deltas = []
    filter_mag = (min_delta_mag + max_delta_mag) / 2
    for delta in v_deltas:
        # filter out vertexes that are too close
        if delta.magnitude < filter_mag:
            continue
        final_deltas.append(delta.normalized())
    # get dot products between all combinations of deltas, and find the lowest dot product
    # TODO improve efficiency because currently this is a O(n^2) solution; terrible
    lowest_dot = 1
    for first_delta in final_deltas:
        for second_delta in final_deltas:
            d = first_delta.dot(second_delta)
            if d < lowest_dot:
                lowest_dot = d
    # return the inverse cosine of the lowest dot product value; this is the highest angle value
    return math.acos(lowest_dot)

def get_sunlit_objects_from_selected(context, name_prepend_str):
    obj_list = []
    # get objects from selected objects list, by name - where name contains the bake plane prepend
    for ob in context.selected_objects:
        if ob.name.startswith(name_prepend_str):
            obj_list.append(ob)
    return obj_list

def get_sunlit_suns_from_selected(context):
    return get_sunlit_objects_from_selected(context, SUNLIT_SUN_PREPEND) + get_sunlit_objects_from_selected(context, SUNLIT_ODISK_SUN_PREPEND)

def get_sunlit_sensors_from_selected(context):
    return get_sunlit_objects_from_selected(context, SUNLIT_SENSOR_PLANE_PREPEND) + get_sunlit_objects_from_selected(context, SUNLIT_ODISK_PREPEND)

def get_sunlit_objects_from_armature(armature, bone_name, obj_name_prepend):
    total_obj_list = []
    for bone in armature.data.bones:
        if not bone.name.startswith(bone_name):
            continue
        obj_list = get_objects_parented_to_bone(armature, bone.name, obj_name_prepend)
        total_obj_list = total_obj_list + obj_list
    return total_obj_list

def get_sunlit_suns_from_armature(armature):
    return get_sunlit_objects_from_armature(armature, SUNLIT_BONE_LIT_ADJUST, SUNLIT_SUN_PREPEND) + \
        get_sunlit_objects_from_armature(armature, SUNLIT_BONE_ODISK_LIGHT, SUNLIT_ODISK_SUN_PREPEND)

def get_sunlit_regular_sensors_from_armature(armature):
    return get_sunlit_objects_from_armature(armature, SUNLIT_BONE_SENSOR, SUNLIT_SENSOR_PLANE_PREPEND)

def get_sunlit_odisk_sensors_from_armature(armature):
    return get_sunlit_objects_from_armature(armature, SUNLIT_BONE_ODISK, SUNLIT_ODISK_PREPEND)

def get_sunlit_regular_lights_from_armature(armature):
    return get_sunlit_objects_from_armature(armature, SUNLIT_BONE_LIT_ADJUST, SUNLIT_SUN_PREPEND)

def get_sunlit_odisk_lights_from_armature(armature):
    return get_sunlit_objects_from_armature(armature, SUNLIT_BONE_ODISK, SUNLIT_ODISK_SUN_PREPEND)

# pack all images with names that contain the bake image prepend name
def pack_all_sunlit_images():
    for image in bpy.data.images:
        if SUNLIT_BAKE_IMG_NAME in image.name:
            image_pack_image(image)

def pack_select_sunlit_images(context):
    planes = get_sunlit_sensors_from_selected(context)
    for plane in planes:
        image = get_sunlit_bake_image_for_plane(plane)
        data_image = bpy.data.images.get(image.name)
        #data_image.pack(as_png=True)
        data_image.pack()

def get_sunlit_bake_image_for_plane(plane):
    if plane.active_material is None:
        return None
    if plane.active_material.node_tree is None:
        return None
    # find a Image Texture node where node's image name contains bake image name prepend
    for node in plane.active_material.node_tree.nodes:
        if node.type != "TEX_IMAGE":
            continue
        if node.image is None:
            continue
        if SUNLIT_BAKE_IMG_NAME in node.image.name:
            return node.image

class OLuminSL_CreateRig(bpy.types.Operator):
    """Create Sunlit rig based on the following rig create options"""
    bl_idname = "olumin_sl.create_sunlit_rig"
    bl_label = "Create Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # materials creation errors occur in Blender Render, so only works in Cycles
        scn = context.scene
        if bpy.app.version < (2,80,0) and (scn.render.engine == "BLENDER_RENDER" or scn.render.engine == "BLENDER_GAME"):
            self.report({'ERROR'}, "Cannot create Sunlig Rig in Blender Render or Blender Game render modes, change " +
                "render engine to CYCLES and try again.")
            return {'CANCELLED'}
        create_sunlit_rig(context, scn.OLuminSL_Hemisphere, scn.OLuminSL_SunCount, scn.OLuminSL_BaseSphereSubdiv,
            scn.OLuminSL_ODiskCount, scn.OLuminSL_ODiskIncludeSun, scn.OLuminSL_SunEnergy, scn.OLuminSL_SunInitAngle,
            scn.OLuminSL_ODiskSunEnergy, scn.OLuminSL_ODiskSunInitAngle, scn.OLuminSL_AllowDrivers,
            scn.OLuminSL_SunImageWidth, scn.OLuminSL_SunImageHeight, scn.OLuminSL_ODiskSunImageWidth,
            scn.OLuminSL_ODiskSunImageHeight, scn.OLuminSL_SunBlindsLen, scn.OLuminSL_ODiskSunBlindsLen)
        return {'FINISHED'}

class OLuminSL_FixRigVisibility(bpy.types.Operator):
    """Hide widget objects used by all Sunlit Rigs. Use this if 'unhide all' was applied, and some weird things """ \
    """are showing on Sunlit Rig. "Blinds" objects are shown for visually checking amount of angular diameter """ \
    """given to each Sunlit sun light"""
    bl_idname = "olumin_sl.fix_rig_visibility"
    bl_label = "Fix All Rig Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        all_obj_list = get_all_objects_list(context)
        for obj in all_obj_list:
            # hide any Sunlig Rig widget objects that are found
            if is_sunlit_rig_widget(obj):
                set_object_hide_view(obj, True)
                set_object_hide_render(obj, True)
            # the rest of the code in this for loop is for Sunlit Rig armatures only
            if not is_sunlit_armature(obj):
                continue
            # get objects and hide them from view
            sphere_list = get_sunlit_objects_from_armature(obj, SUNLIT_BONE_SPHERE, SUNLIT_BASE_SPHERE_PREPEND)
            set_object_list_hide_view(sphere_list, True)
            set_object_list_hide_render(sphere_list, True)
            cube_list = get_sunlit_objects_from_armature(obj, SUNLIT_BONE_DIFF_CUBE, SUNLIT_DCUBE_PREPEND)
            set_object_list_hide_view(cube_list, True)
            set_object_list_hide_render(cube_list, True)
            # if hiding blinds, then hide regular blinds and ODisk blinds
            # this code will also un-hide blinds if "Hide Blinds Too" is disabled
            blinds_list = get_sunlit_objects_from_armature(obj, SUNLIT_BONE_DIFF_CUBE, SUNLIT_SUN_BLINDS_PREPEND)
            set_object_list_hide_view(blinds_list, scn.OLuminSL_HideBlindsToo)
            set_object_list_hide_render(blinds_list, False)
            od_blinds_list = get_sunlit_objects_from_armature(obj, SUNLIT_BONE_ODISK, SUNLIT_ODISK_BLINDS_PREPEND)
            set_object_list_hide_view(od_blinds_list, scn.OLuminSL_HideBlindsToo)
            set_object_list_hide_render(od_blinds_list, False)

            sensor_list = get_sunlit_objects_from_armature(obj, SUNLIT_BONE_SENSOR, SUNLIT_SENSOR_PLANE_PREPEND)
            set_object_list_hide_view(sensor_list, False)
            set_object_list_hide_render(sensor_list, False)

            od_sensor_list = get_sunlit_objects_from_armature(obj, SUNLIT_BONE_ODISK, SUNLIT_ODISK_PREPEND)
            set_object_list_hide_view(od_sensor_list, False)
            set_object_list_hide_render(od_sensor_list, False)

            rig_cam_list = get_objects_parented_to(obj, SUNLIT_CAMERA_PREPEND)
            for rig_cam in rig_cam_list:
                set_object_hide_view(rig_cam, True)

        return {'FINISHED'}

class OLuminSL_BakeSelectedSensors(bpy.types.Operator):
    """Bake Sunlit Rig sensor images for selected sensors only. These images will be sampled when computing the """ \
    """light color of the rig's suns"""
    bl_idname = "olumin_sl.bake_selected_sensors"
    bl_label = "Bake Selected Sensors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        if scn.render.engine != "CYCLES":
            self.report({'ERROR'}, "Change render engine to CYCLES, and try again.")
            return {'CANCELLED'}
        warn_list = bake_select_sunlit_sensors(context, scn.OLuminSL_BakeSamples, scn.OLuminSL_BakeHideAllLights)
        if len(warn_list) == 0:
            for warn in warn_list:
                self.report({'WARNING'}, warn)
        return {'FINISHED'}

class OLuminSL_BakeRigSensors(bpy.types.Operator):
    """Bake Sunlit Rig sensor images for sensors of selected rigs only. These images will be sampled when """ \
    """computing the light color of the rig's suns"""
    bl_idname = "olumin_sl.bake_rig_sensors"
    bl_label = "Bake Rig Sensors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        if scn.render.engine != "CYCLES":
            self.report({'ERROR'}, "Change render engine to CYCLES, and try again.")
            return {'CANCELLED'}
        sunlit_arms = []
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                sunlit_arms.append(ob)
        warn_list = bake_sunlit_armature_list_sensors(context, scn.OLuminSL_BakeSamples,
            scn.OLuminSL_BakeHideAllLights, sunlit_arms)
        if len(warn_list) == 0:
            for warn in warn_list:
                self.report({'WARNING'}, warn)
        return {'FINISHED'}

class OLuminSL_SensorImagePack(bpy.types.Operator):
    """Pack ALL (not just selected sensors) sensor images to current Blend file. Use this if sensor images are """ \
    """changed, e.g. use this after baking sensor images. Changes to sensor images are lost when exiting Blender if """ \
    """changes are not packed"""
    bl_idname = "olumin_sl.image_pack"
    bl_label = "Pack Sensor Images"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        pack_all_sunlit_images()
        return {'FINISHED'}

class OLuminSL_SetSelectSunColor(bpy.types.Operator):
    """Set color of suns attached to selected sensor planes"""
    bl_idname = "olumin_sl.select_sensors_to_sun_color"
    bl_label = "Set Select Sun Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        set_select_sun_color_data(context, scn.OLuminSL_KeyframeColor, scn.OLuminSL_SensorSampleWidthPct,
            scn.OLuminSL_SensorSampleHeightPct, scn.OLuminSL_ODiskSensorSampleWidthPct,
            scn.OLuminSL_ODiskSensorSampleHeightPct)
        return {'FINISHED'}

class OLuminSL_SetRigSunColor(bpy.types.Operator):
    """Set color of suns attached to sensor planes of selected rigs"""
    bl_idname = "olumin_sl.rig_sensors_to_sun_color"
    bl_label = "Set Rig Sun Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                set_sunlit_armature_sun_color_data(scn.OLuminSL_KeyframeColor, scn.OLuminSL_SensorSampleWidthPct,
                    scn.OLuminSL_SensorSampleHeightPct, scn.OLuminSL_ODiskSensorSampleWidthPct,
                    scn.OLuminSL_ODiskSensorSampleHeightPct, ob)
        return {'FINISHED'}

class OLuminSL_SetSelectSunAngle(bpy.types.Operator):
    """Set angular diameter, for selected sun lights, based on the max angular diameter of their respective blinds. """ \
    """Angular diamater of blinds as seen from viewpoint of a camera located at the origin (in object space) of the """ \
    """rig"""
    bl_idname = "olumin_sl.select_blinds_angle_to_sun_angle"
    bl_label = "Set Select Angular Diameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_sunlit_sun_angular_diameter(context, get_sunlit_suns_from_selected(context),
            context.scene.OLuminSL_KeyframeAngle)
        return {'FINISHED'}

class OLuminSL_SetRigSunAngle(bpy.types.Operator):
    """Set angular diameter, for sun lights of selected Sunlit Rig, based on the max angular diameter of their """ \
    """respective blinds. Angular diamater of blinds as seen from viewpoint of a camera located at the origin (in """ \
    """object space) of the rig"""
    bl_idname = "olumin_sl.rig_blinds_angle_to_sun_angle"
    bl_label = "Set Rig Angular Diameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                set_sunlit_sun_angular_diameter(context, get_sunlit_suns_from_armature(ob),
                    context.scene.OLuminSL_KeyframeAngle)
        return {'FINISHED'}

class OLuminSL_SelectVisibleRigs(bpy.types.Operator):
    """Select all Sunlit Rigs that are not hidden"""
    bl_idname = "olumin_sl.select_visible_rigs"
    bl_label = "Select Visible Rigs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        all_obj_list = get_all_objects_list(context)
        for obj in all_obj_list:
            if not get_object_hide_view(obj) and is_sunlit_armature(obj):
                select_object(obj)
        return {'FINISHED'}

class OLuminSL_SelectAllRigs(bpy.types.Operator):
    """Select all Sunlit Rigs, hidden and visible"""
    bl_idname = "olumin_sl.select_all_rigs"
    bl_label = "Select All Rigs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        all_obj_list = get_all_objects_list(context)
        for obj in all_obj_list:
            if is_sunlit_armature(obj):
                select_object(obj)
        return {'FINISHED'}

class OLuminSL_SelectRigRegularSensors(bpy.types.Operator):
    """Select the regular sun sensors of the currently selected Sunlit Rig(s)"""
    bl_idname = "olumin_sl.select_rig_regular_sensors"
    bl_label = "Select Regular Sensors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        to_select_list = []
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                to_select_list = to_select_list + get_sunlit_regular_sensors_from_armature(ob)
        select_objects(to_select_list)
        return {'FINISHED'}

class OLuminSL_SelectRigODiskSensors(bpy.types.Operator):
    """Select the Occluding Disk sensors of the currently selected Sunlit Rig(s)"""
    bl_idname = "olumin_sl.select_rig_odisk_sensors"
    bl_label = "Select ODisk Sensors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        to_select_list = []
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                to_select_list = to_select_list + get_sunlit_odisk_sensors_from_armature(ob)
        select_objects(to_select_list)
        return {'FINISHED'}

class OLuminSL_SelectRigRegularLights(bpy.types.Operator):
    """Select the regular sun lights of the currently selected Sunlit Rig(s)"""
    bl_idname = "olumin_sl.select_rig_regular_lights"
    bl_label = "Select Regular Lights"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        to_select_list = []
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                to_select_list = to_select_list + get_sunlit_regular_lights_from_armature(ob)
        select_objects(to_select_list)
        return {'FINISHED'}

class OLuminSL_SelectRigODiskLights(bpy.types.Operator):
    """Select the occluding disk sun lights of the currently selected Sunlit Rig(s)"""
    bl_idname = "olumin_sl.select_rig_odisk_lights"
    bl_label = "Select ODisk Lights"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        to_select_list = []
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                to_select_list = to_select_list + get_sunlit_odisk_lights_from_armature(ob)
        select_objects(to_select_list)
        return {'FINISHED'}

class OLuminSL_PointRegularFromView(bpy.types.Operator):
    """Point the Regular sun light in the same direction as the current viewport view direction / camera view """ \
    """direction. Sun light numbers are zero-indexed, so '0' is the first ODisk, '1' is the second ODisk, etc"""
    bl_idname = "olumin_sl.point_regular_from_view"
    bl_label = "Set Regular Direction from View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        rv3d = context.region_data
        view_dir = matrix_vector_mult(rv3d.view_rotation, Vector((0, 0, -1)))

        regular_num = scn.OLuminSL_RegularNumPointFromView
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                point_target_bone = ob.pose.bones.get(any_prepend_name_num(SUNLIT_BONE_SUN_TARGET, regular_num))
                if point_target_bone is None:
                    continue
                # reverse direction if needed
                mult = 1
                if scn.OLuminSL_ReverseLightPointDirection:
                    mult = -1
                point_target_bone.location[0] = view_dir[0] * 2 * mult
                point_target_bone.location[1] = view_dir[1] * 2 * mult
                point_target_bone.location[2] = view_dir[2] * 2 * mult

        return {'FINISHED'}

class OLuminSL_PointODiskFromView(bpy.types.Operator):
    """Point the ODisk sun light in the same direction as the current viewport view direction / camera view """ \
    """direction. ODisk numbers are zero-indexed, so '0' is the first ODisk, '1' is the second ODisk, etc"""
    bl_idname = "olumin_sl.point_odisk_from_view"
    bl_label = "Set ODisk Direction from View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        rv3d = context.region_data
        view_dir = matrix_vector_mult(rv3d.view_rotation, Vector((0, 0, -1)))

        odisk_num = scn.OLuminSL_ODiskNumPointFromView
        for ob in context.selected_objects:
            if is_sunlit_armature(ob):
                point_target_bone = ob.pose.bones.get(any_prepend_name_num(SUNLIT_BONE_ODISK_TARGET, odisk_num))
                if point_target_bone is None:
                    continue
                # reverse direction if needed
                mult = 1
                if scn.OLuminSL_ReverseLightPointDirection:
                    mult = -1
                point_target_bone.location[0] = view_dir[0] * 2 * mult
                point_target_bone.location[1] = view_dir[1] * 2 * mult
                point_target_bone.location[2] = view_dir[2] * 2 * mult

        return {'FINISHED'}

class OLuminSL_PointCamAtODisk(bpy.types.Operator):
    """Use this to help matching background sun size with ODisk size. Point Sunlit Rig's test camera at ODisk """ \
    """given by ODisk number. ODisk numbers are zero-indexed, so '0' is the first ODisk, '1' is the second ODisk, etc"""
    bl_idname = "olumin_sl.point_cam_at_odisk"
    bl_label = "Point Cam at ODisk"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        act_ob = context.active_object
        if not is_sunlit_armature(act_ob):
            print("not sunlit armature, no looks")
            return {'FINISHED'}
        set_sunlit_cam_odisk_target(act_ob, context.scene.OLuminSL_ODiskNumPointFromView)
        return {'FINISHED'}
