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
import math

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

XTU_XY_MAP_NAME = "xy_to_uv"
XTU_XZ_MAP_NAME = "xz_to_uv"
XTU_CAMERA_NAME_XY = "Camera.UVxy"
XTU_CAMERA_NAME_XZ = "Camera.UVxz"

# Offset by 0.5 in all dimensions, this seems to relate to:
#     (0.5, 0.5) is middle in UV coordinates, and
#     (0, 0, 0) is middle in XYZ coordinates.
CAM_START_LOCATION = (0.5, 0.5, 0.5)
CAM_START_ROTATION_XY = (0, 0, 0)
CAM_START_ROTATION_XZ = (math.radians(90), 0, 0)

class OLuminXTU_ObjectShaderXYZMap(bpy.types.Operator):
    """With selected objects, append a new shader to capture XYZ vertex coordinates and store them in two UV maps """ \
    """for resultant XYZ -> UVW mapping. E.g. Use when applying noise texture node to a mesh that will be deformed by """ \
    """shapekeys/simulation"""
    bl_idname = "olumin_xtu.object_shader_xyz_map"
    bl_label = "XYZ to UVW"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene

        existing_cam_xy = None
        existing_cam_xzed = None
        if scn.OLuminXTU_ReuseCameras:
            if scn.OLuminXTU_ReuseCameraNameXY != "":
                existing_cam_xy = bpy.data.objects.get(scn.OLuminXTU_ReuseCameraNameXY)
            if scn.OLuminXTU_ReuseCameraNameXZ != "":
                existing_cam_xzed = bpy.data.objects.get(scn.OLuminXTU_ReuseCameraNameXZ)

        prev_cam_xy = existing_cam_xy
        prev_cam_xzed = existing_cam_xzed

        # initialize the nested-dictionary of (string, string) combinations of (uv_map_xy.name, uv_map_xzed.name)
        # pointing to material shaders
        grp_mat_shaders = {}
        # used with "Add to Existing Material" to prevent spamming a single shader when multiple objects are selected
        already_added_to_shaders = []
        # with selected MESH objects, do the XYZ to UVW mapping process
        for obj in context.selected_objects:
            # cannot apply material to non-mesh objects
            if obj.type != "MESH":
                continue

            # get/create UV Maps for object, to be used as UVW
            uv_map_xy = None
            uv_map_xzed = None
            if scn.OLuminXTU_ReuseUVMaps:
                uv_map_xy = get_object_uv_map(obj, scn.OLuminXTU_ReuseUVNameXY)
                uv_map_xzed = get_object_uv_map(obj, scn.OLuminXTU_ReuseUVNameXZ)

            # create two UV maps on object 'obj', to be used for XYZ to UVW mapping via two UV Project modifiers on object 'obj'
            if uv_map_xy is None:
                uv_map_xy = create_object_uv_map(obj, get_unused_uv_map_name(obj, XTU_XY_MAP_NAME))
            if uv_map_xzed is None:
                uv_map_xzed = create_object_uv_map(obj, get_unused_uv_map_name(obj, XTU_XZ_MAP_NAME))

            # prevent errors
            if uv_map_xy is None or uv_map_xzed is None:
                print("Unable to create UV Maps on object: " + obj.name)
                continue
            # prevent reference problems/errors when uv_map_xy and uv_map_xzed are used later,
            # the UV map names are all that is needed
            saved_uv_map_xy_name = uv_map_xy.name
            saved_uv_map_xzed_name = uv_map_xzed.name

            cam_xy, cam_xzed = None, None
            if scn.OLuminXTU_ReuseCameras:
                cam_xy = prev_cam_xy
                cam_xzed = prev_cam_xzed
            if cam_xy == None:
                cam_xy = add_uv_project_camera(context, "XY")
                prev_cam_xy = cam_xy
            if cam_xzed == None:
                cam_xzed = add_uv_project_camera(context, "XZ")
                prev_cam_xzed = cam_xzed

            # --- object modifier code ---
            proj_mod_xy, proj_mod_xzed = add_object_uv_project_mods(obj, saved_uv_map_xy_name, saved_uv_map_xzed_name, cam_xy, cam_xzed)
            if scn.OLuminXTU_ApplyModifiers:
                apply_proj_modifiers(context, obj, scn.OLuminXTU_CopyHideModifiers, proj_mod_xy, proj_mod_xzed, \
                    saved_uv_map_xy_name, saved_uv_map_xzed_name, cam_xy, cam_xzed)
                # delete cameras if modifiers were not 'copied', and were applied only
                if not scn.OLuminXTU_CopyHideModifiers:
                    # if a pre-existing camera wasn't used, then delete the widget cam
                    if cam_xy != None and cam_xy != existing_cam_xy:
                        delete_widget_cam(cam_xy)
                    # if a pre-existing camera wasn't used, then delete the widget cam
                    if cam_xzed != None and cam_xzed != existing_cam_xzed:
                        delete_widget_cam(cam_xzed)
                    cam_xy = None
                    cam_xzed = None

            # if widget cameras were not deleted then ensure they are hidden from view
            if cam_xy != None:
                set_object_hide_view(cam_xy, True)
            if cam_xzed != None:
                set_object_hide_view(cam_xzed, True)

            # skip 'append shader' code for this object if not needed
            if not scn.OLuminXTU_AppendMaterial:
                continue

            #  --- shader material code ---
            if scn.OLuminXTU_NewMatPerObj:
                # create a completely new material shader and append material to each object
                mat_shader_per_obj = create_xyz_to_uvw_mat_shader(None, saved_uv_map_xy_name, saved_uv_map_xzed_name, \
                    scn.OLuminXTU_ColorTextureType)
                obj.data.materials.append(mat_shader_per_obj)
            else:
                # add to existing material shader if it exists, but not if it has already been added to
                # (in case multiple mesh objects with the same shader are selected when using this function)
                if scn.OLuminXTU_AddToExisting and obj.active_material != None and obj.active_material not in already_added_to_shaders:
                    create_xyz_to_uvw_mat_shader(obj.active_material, saved_uv_map_xy_name, saved_uv_map_xzed_name, \
                        scn.OLuminXTU_ColorTextureType)
                    already_added_to_shaders.append(obj.active_material)
                # otherwise, try to get previous material shader with UV map names matching this object's UV map names
                # (the XY and XZ 'UV Maps')
                else:
                    # check if current combination of (uv_map_xy.name, uv_map_xzed.name) have been used, and get
                    # that material

                    xy_name_dictionary = grp_mat_shaders.get(saved_uv_map_xy_name)
                    if xy_name_dictionary is None:
                        # create the dictionary linked to the unique uv_map_xy.name
                        grp_mat_shaders[saved_uv_map_xy_name] = {}
                        xy_name_dictionary = grp_mat_shaders[saved_uv_map_xy_name]
                    obj_mat_shader = xy_name_dictionary.get(saved_uv_map_xzed_name)
                    if obj_mat_shader is None:
                        # create the mat because it wasn't found in the name combinations nested-dictionary
                        obj_mat_shader = create_xyz_to_uvw_mat_shader(None, saved_uv_map_xy_name, saved_uv_map_xzed_name, \
                            scn.OLuminXTU_ColorTextureType)
                        # add the material to the nested-dictionary, for use later if needed
                        # this will reduce the amount of redundant material shaders created
                        xy_name_dictionary[saved_uv_map_xzed_name] = obj_mat_shader
                    # append the new material shader
                    obj.data.materials.append(obj_mat_shader)

        return {'FINISHED'}

def delete_widget_cam(wgt_cam):
    bpy.ops.object.select_all(action='DESELECT')
    select_object(wgt_cam)
    bpy.ops.object.delete()

def get_unused_uv_map_name(obj, base_map_name):
    if get_object_uv_map(obj, base_map_name) is None:
        return base_map_name
    for test_num in range(1, 999):
        test_map_name = base_map_name + '.' + str(test_num).zfill(3)
        if get_object_uv_map(obj, test_map_name) is None:
            return test_map_name
    return None

# create material shader nodes, to interact with two UV maps (the XYZ to UVW map)
def create_xyz_to_uvw_mat_shader(prev_mat_shader, xy_uvmap_name, xzed_uvmap_name, color_texture_node_type):
    mat_shader = None
    tree_nodes = None
    # create new material shader if no previous material shader given
    if prev_mat_shader == None:
        mat_shader = bpy.data.materials.new(name="xyz_to_uvw_mat")
        mat_shader.use_nodes = True
        # delete all nodes from the initial object shader setup, if pre-existing material shader is not given
        tree_nodes = mat_shader.node_tree.nodes
        tree_nodes.clear()
    else:
        mat_shader = prev_mat_shader
        mat_shader.use_nodes = True
        tree_nodes = mat_shader.node_tree.nodes

    # initialize variables
    new_nodes = {}

    # material shader nodes
    node = tree_nodes.new(type="ShaderNodeOutputMaterial")
    node.location = (426, 112)
    new_nodes["Material Output"] = node

    node = tree_nodes.new(type="ShaderNodeCombineXYZ")
    node.location = (-580, 61)
    new_nodes["Combine XYZ"] = node

    # vector to color node is special, because it is variable
    node = tree_nodes.new(type=color_texture_node_type)
    node.location = (40, 104)
    new_nodes[color_texture_node_type] = node

    node = tree_nodes.new(type="ShaderNodeBsdfPrincipled")
    node.location = (224, 204)
    new_nodes["Principled BSDF"] = node

    node = tree_nodes.new(type="ShaderNodeUVMap")
    node.location = (-954, 62)
    node.uv_map = xy_uvmap_name
    new_nodes["UV Map"] = node

    node = tree_nodes.new(type="ShaderNodeUVMap")
    node.location = (-952, -65)
    node.uv_map = xzed_uvmap_name
    new_nodes["UV Map.001"] = node

    node = tree_nodes.new(type="ShaderNodeSeparateXYZ")
    node.location = (-748, 84)
    new_nodes["Separate XYZ.001"] = node

    node = tree_nodes.new(type="ShaderNodeSeparateXYZ")
    node.location = (-750, -40)
    new_nodes["Separate XYZ"] = node

    node = tree_nodes.new(type="ShaderNodeMapping")
    node.location = (-360, 120)
    new_nodes["Mapping"] = node

    # links between nodes
    tree_links = mat_shader.node_tree.links
    tree_links.new(new_nodes["UV Map.001"].outputs[0], new_nodes["Separate XYZ"].inputs[0])
    tree_links.new(new_nodes["UV Map"].outputs[0], new_nodes["Separate XYZ.001"].inputs[0])
    tree_links.new(new_nodes["Separate XYZ.001"].outputs[0], new_nodes["Combine XYZ"].inputs[0])
    tree_links.new(new_nodes["Separate XYZ.001"].outputs[1], new_nodes["Combine XYZ"].inputs[1])
    tree_links.new(new_nodes["Principled BSDF"].outputs[0], new_nodes["Material Output"].inputs[0])
    tree_links.new(new_nodes["Separate XYZ"].outputs[1], new_nodes["Combine XYZ"].inputs[2])
    tree_links.new(new_nodes[color_texture_node_type].outputs[0], new_nodes["Principled BSDF"].inputs[0])
    tree_links.new(new_nodes["Combine XYZ"].outputs[0], new_nodes["Mapping"].inputs[0])
    tree_links.new(new_nodes["Mapping"].outputs[0], new_nodes[color_texture_node_type].inputs[0])

    return mat_shader

def add_uv_project_camera(context, proj_type):
    if proj_type == "XY":
        bpy.ops.object.camera_add(location=CAM_START_LOCATION, rotation=CAM_START_ROTATION_XY)
        cam_xy = context.active_object
        cam_xy.name = XTU_CAMERA_NAME_XY
        cam_xy.data.type = "ORTHO"
        cam_xy.data.ortho_scale = 1.0
        return cam_xy
    elif proj_type == "XZ":
        bpy.ops.object.camera_add(location=CAM_START_LOCATION, rotation=CAM_START_ROTATION_XZ)
        cam_xzed = context.active_object
        cam_xzed.name = XTU_CAMERA_NAME_XZ
        cam_xzed.data.type = "ORTHO"
        cam_xzed.data.ortho_scale = 1.0
        return cam_xzed
    return None

# project the XYZ coordinates to UVW coordinates
# two UV maps give 4 coordinates (1 is wasted!), and use 3 coordinates to store (X, Y, Z) as (U1, V1, U2)
def add_object_uv_project_mods(obj, uv_map_xy_name, uv_map_xzed_name, cam_xy, cam_xzed):
    # (U1, V1)
    b_mod_xy = obj.modifiers.new("UVProject.XY", "UV_PROJECT")
    b_mod_xy.uv_layer = uv_map_xy_name
    b_mod_xy.aspect_x = 1.0
    b_mod_xy.aspect_y = 1.0
    b_mod_xy.scale_x = 1.0
    b_mod_xy.scale_y = 1.0
    b_mod_xy.projectors[0].object = cam_xy

    # (U2, V2)
    b_mod_xzed = obj.modifiers.new("UVProject.XZ", "UV_PROJECT")
    b_mod_xzed.uv_layer = uv_map_xzed_name
    b_mod_xzed.aspect_x = 1.0
    b_mod_xzed.aspect_y = 1.0
    b_mod_xzed.scale_x = 1.0
    b_mod_xzed.scale_y = 1.0
    b_mod_xzed.projectors[0].object = cam_xzed

    return b_mod_xy, b_mod_xzed

def apply_proj_modifiers(context, obj, copy_hide_modifiers, proj_mod_xy, proj_mod_xzed, uv_map_xy_name, uv_map_xzed_name, \
    cam_xy, cam_xzed):
    set_active_object(context, obj)

    bpy.ops.object.modifier_apply(modifier=proj_mod_xy.name)
    bpy.ops.object.modifier_apply(modifier=proj_mod_xzed.name)

    if copy_hide_modifiers:
        # re-create them, instead of copying - easier
        b_mod_xy, b_mod_xzed = add_object_uv_project_mods(obj, uv_map_xy_name, uv_map_xzed_name, cam_xy, cam_xzed)
        # hide them
        b_mod_xy.show_viewport = False
        b_mod_xy.show_render = False
        b_mod_xzed.show_viewport = False
        b_mod_xzed.show_render = False

class OLuminXTU_FixXYZCameras(bpy.types.Operator):
    """Fix all XYZ to UVW cameras: visibility (and location, rotation)"""
    bl_idname = "olumin_xtu.fix_xyz_cameras"
    bl_label = "Fix XYZ Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        all_obj_list = get_all_objects_list(context)
        for obj in all_obj_list:
            # hide any camera objects with name matching XYZ to UVW standard camera name
            # TODO instead of using sloppy 'startswith' string check, check for ends with .001 or .002, etc.
            if obj.type == "CAMERA" and (obj.name.startswith(XTU_CAMERA_NAME_XY) or obj.name.startswith(XTU_CAMERA_NAME_XZ)):
                set_object_hide_view(obj, True)
                if context.scene.OLuminXTU_FixCamAll:
                    if obj.name.startswith(XTU_CAMERA_NAME_XY):
                        obj.location = CAM_START_LOCATION
                        obj.rotation_mode = "XYZ"
                        obj.rotation_euler = CAM_START_ROTATION_XY
                    elif obj.name.startswith(XTU_CAMERA_NAME_XZ):
                        obj.location = CAM_START_LOCATION
                        obj.rotation_mode = "XYZ"
                        obj.rotation_euler = CAM_START_ROTATION_XZ
        return {'FINISHED'}
