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
from pickle import NONE

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

WE_XY_MAP_NAME = "xy_to_uv_map"
WE_XZED_MAP_NAME = "xzed_to_uv_map"

class OLuminWE_MobileBackground(bpy.types.Operator):
    """Enable movement of the world background environment texture (e.g. HDRI texture), by connecting it to camera location.""" \
    """Select camera before using this function, because active object is used to drive apparent movement of background"""
    bl_idname = "olumin_we.mobile_background"
    bl_label = "Mobile Background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object == None:
            self.report({'ERROR'}, "Cannot get active_object, select a visible object (e.g. camera) and try again")
            return {'CANCELLED'}
        create_mobile_background(context)

        return {'FINISHED'}

# delete all existing nodes in environment shader, and replace with mobile background nodes
def create_mobile_background(context):
    scn_w = context.scene.world
    # ensure environment shader uses nodes, because we will create nodes to make mobile environment shader
    scn_w.use_nodes = True
    tree_nodes = scn_w.node_tree.nodes
    # delete all nodes from the initial environment shader setup
    tree_nodes.clear()

    # material shader nodes
    new_nodes = {}

    node = tree_nodes.new(type="ShaderNodeVectorMath")
    node.location = (-161.0, 77.0)
    new_nodes["Vector Math"] = node

    node = tree_nodes.new(type="ShaderNodeTexCoord")
    node.location = (-379.728, 138.901)
    new_nodes["Texture Coordinate"] = node

    node = tree_nodes.new(type="ShaderNodeMapping")
    node.location = (-380.074, -114.44)
    new_nodes["Mapping"] = node

    node = tree_nodes.new(type="ShaderNodeTexEnvironment")
    node.location = (35.629, 102.683)
    new_nodes["Environment Texture"] = node

    node = tree_nodes.new(type="ShaderNodeBackground")
    node.location = (479.566, 171.551)
    new_nodes["Background"] = node

    node = tree_nodes.new(type="ShaderNodeOutputWorld")
    node.location = (646.363, 167.949)
    new_nodes["World Output"] = node

    # add EEVEE stuff
    if bpy.app.version >= (2,80,0):
        node = tree_nodes.new(type="ShaderNodeMixShader")
        node.location = (614.089, -81.285)
        new_nodes["Mix Shader"] = node

        node = tree_nodes.new(type="ShaderNodeOutputWorld")
        node.location = (787.293, -97.521)
        new_nodes["World Output.001"] = node

        node = tree_nodes.new(type="ShaderNodeLightPath")
        node.location = (162.052, -129.775)
        new_nodes["Light Path"] = node

        node = tree_nodes.new(type="ShaderNodeBackground")
        node.location = (412.171, -180.072)
        new_nodes["Background.001"] = node

        node = tree_nodes.new(type="ShaderNodeBackground")
        node.location = (406.071, -27.986)
        new_nodes["Background.002"] = node

    # links between nodes
    tree_links = scn_w.node_tree.links
    tree_links.new(new_nodes["Environment Texture"].outputs[0], new_nodes["Background"].inputs[0])
    tree_links.new(new_nodes["Background"].outputs[0], new_nodes["World Output"].inputs[0])
    tree_links.new(new_nodes["Vector Math"].outputs[0], new_nodes["Environment Texture"].inputs[0])
    tree_links.new(new_nodes["Texture Coordinate"].outputs[0], new_nodes["Vector Math"].inputs[0])
    tree_links.new(new_nodes["Mapping"].outputs[0], new_nodes["Vector Math"].inputs[1])

    # add EEVEE stuff
    if bpy.app.version >= (2,80,0):
        tree_links.new(new_nodes["Light Path"].outputs[0], new_nodes["Mix Shader"].inputs[0])
        tree_links.new(new_nodes["Environment Texture"].outputs[0], new_nodes["Background.001"].inputs[0])
        tree_links.new(new_nodes["Environment Texture"].outputs[0], new_nodes["Background.002"].inputs[0])
        tree_links.new(new_nodes["Background.001"].outputs[0], new_nodes["Mix Shader"].inputs[2])
        tree_links.new(new_nodes["Background.002"].outputs[0], new_nodes["Mix Shader"].inputs[1])
        tree_links.new(new_nodes["Mix Shader"].outputs[0], new_nodes["World Output.001"].inputs[0])

    # add drivers to the input to the Vector Mapping node, connected to active_object
    vec_mapping_fcurves = []
    # create tuples so a 'for' loop can be used
    vec_mapping_fcurves.append( (new_nodes["Mapping"].inputs["Vector"].driver_add("default_value", 0), "location.x") )
    vec_mapping_fcurves.append( (new_nodes["Mapping"].inputs["Vector"].driver_add("default_value", 1), "location.y") )
    vec_mapping_fcurves.append( (new_nodes["Mapping"].inputs["Vector"].driver_add("default_value", 2), "location.z") )
    for fc, d_path in vec_mapping_fcurves:
        v = fc.driver.variables.new()
        v.name                 = "var"
        v.targets[0].id        = context.active_object
        v.targets[0].data_path = d_path
        fc.driver.expression = v.name

class OLuminWE_ObjectShaderXYZ_Map(bpy.types.Operator):
    """With selected objects, append a new shader to capture XYZ vertex coordinates and store them in two UV maps """ \
    """for resultant XYZ -> UVW mapping. E.g. Use when applying noise texture node to a mesh that will be deformed by """ \
    """shapekeys/simulation"""
    bl_idname = "olumin_we.object_shader_xyz_map"
    bl_label = "XYZ to UVW"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene

        # initialize the nested-dictionary of (string, string) combinations of (uv_map_xy.name, uv_map_xzed.name)
        # pointing to material shaders
        grp_mat_shaders = {}
        for obj in context.selected_objects:
            # cannot apply material to non-mesh objects
            if obj.type != "MESH":
                continue
            uv_map_xy, uv_map_xzed = create_xy_and_xzed_uv_maps(obj)
            # prevent errors
            if uv_map_xy is None or uv_map_xzed is None:
                print("Unable to create UV Maps on object: " + obj.name)
                continue

            # --- object modifier code ---
            cam_xy, cam_xzed = add_uv_project_cameras(context)
            proj_mod_xy, proj_mod_xzed = add_object_uv_project_mods(obj, uv_map_xy, uv_map_xzed, cam_xy, cam_xzed)
            if scn.OLuminWE_ApplyModifiers:
                apply_proj_modifiers(context, obj, scn.OLuminWE_CopyHideModifiers, proj_mod_xy, proj_mod_xzed, \
                    uv_map_xy, uv_map_xzed, cam_xy, cam_xzed)
                # delete cameras if modifiers were not 'copied', and were applied only
                if not scn.OLuminWE_CopyHideModifiers:
                    delete_widget_cams(cam_xy, cam_xzed)
                    cam_xy = None
                    cam_xzed = None
            # if widget cameras were not deleted then hide them from view
            if cam_xy != None:
                set_object_hide_view(cam_xy, True)
            if cam_xzed != None:
                set_object_hide_view(cam_xzed, True)

            #  --- shader material code ---
            if scn.OLuminWE_NewMatPerObj:
                # create a completely new material shader and append material to each object
                mat_shader_per_obj = create_xyz_to_uvw_mat_shader(None, uv_map_xy.name, uv_map_xzed.name, \
                    scn.OLuminWE_ColorTextureType)
                obj.data.materials.append(mat_shader_per_obj)
            else:
                if scn.OLuminWE_AddToExisting and obj.active_material != None:
                    create_xyz_to_uvw_mat_shader(obj.active_material, uv_map_xy.name, uv_map_xzed.name, \
                        scn.OLuminWE_ColorTextureType)
                else:
                    # check if current combination of (uv_map_xy.name, uv_map_xzed.name) have been used, and get
                    # that material

                    xy_name_dictionary = grp_mat_shaders.get(uv_map_xy.name)
                    if xy_name_dictionary is None:
                        # create the dictionary linked to the unique uv_map_xy.name
                        grp_mat_shaders[uv_map_xy.name] = {}
                        xy_name_dictionary = grp_mat_shaders[uv_map_xy.name]
                    obj_mat_shader = xy_name_dictionary.get(uv_map_xzed.name)
                    if obj_mat_shader is None:
                        # create the mat because it wasn't found in the name combinations nested-dictionary
                        obj_mat_shader = create_xyz_to_uvw_mat_shader(None, uv_map_xy.name, uv_map_xzed.name, \
                            scn.OLuminWE_ColorTextureType)
                        # add the material to the nested-dictionary, for use later if needed
                        # this will reduce the amount of redundant material shaders created
                        xy_name_dictionary[uv_map_xzed.name] = obj_mat_shader
                        # append the new material shader
                        obj.data.materials.append(obj_mat_shader)
                    else:
                        # add the nodes to the pre-existing material shader
                        create_xyz_to_uvw_mat_shader(obj_mat_shader, uv_map_xy.name, uv_map_xzed.name, \
                            scn.OLuminWE_ColorTextureType)

        return {'FINISHED'}

def delete_widget_cams(cam_xy, cam_xzed):
    bpy.ops.object.select_all(action='DESELECT')
    select_object(cam_xy)
    select_object(cam_xzed)
    bpy.ops.object.delete()

# create two UV maps on object 'obj', to be used for XYZ to UVW mapping via two UV Project modifiers on object 'obj'
def create_xy_and_xzed_uv_maps(obj):
    xy_map_name = get_unused_uv_map_name(obj, WE_XY_MAP_NAME)
    xy_uvmap = create_object_uv_map(obj, xy_map_name)
    xzed_map_name = get_unused_uv_map_name(obj, WE_XZED_MAP_NAME)
    xzed_uvmap = create_object_uv_map(obj, xzed_map_name)
    return xy_uvmap, xzed_uvmap

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

def add_uv_project_cameras(context):
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
    cam_xy = context.active_object
    cam_xy.data.type = "ORTHO"
    cam_xy.data.ortho_scale = 1.0
    # Offset by 0.5 in all dimensions, this seems to relate to:
    #     (0.5, 0.5) is middle in UV coordinates, and
    #     (0, 0, 0) is middle in XYZ coordinates.
    cam_xy.location = (0.5, 0.5, 0.5)

    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    cam_xzed = context.active_object
    cam_xzed.data.type = "ORTHO"
    cam_xzed.data.ortho_scale = 1.0
    cam_xzed.location = (0.5, 0.5, 0.5)

    return cam_xy, cam_xzed

# project the XYZ coordinates to UVW coordinates
# two UV maps give 4 coordinates (1 is wasted!), and use 3 coordinates to store (X, Y, Z) as (U1, V1, U2)
def add_object_uv_project_mods(obj, uv_map_xy, uv_map_xzed, cam_xy, cam_xzed):
    # (U1, V1)
    b_mod_xy = obj.modifiers.new("UVProject.XY", "UV_PROJECT")
    b_mod_xy.uv_layer = uv_map_xy.name
    b_mod_xy.aspect_x = 1.0
    b_mod_xy.aspect_y = 1.0
    b_mod_xy.scale_x = 1.0
    b_mod_xy.scale_y = 1.0
    b_mod_xy.projectors[0].object = cam_xy

    # (U2, V2)
    b_mod_xzed = obj.modifiers.new("UVProject.XZ", "UV_PROJECT")
    b_mod_xzed.uv_layer = uv_map_xzed.name
    b_mod_xzed.aspect_x = 1.0
    b_mod_xzed.aspect_y = 1.0
    b_mod_xzed.scale_x = 1.0
    b_mod_xzed.scale_y = 1.0
    b_mod_xzed.projectors[0].object = cam_xzed

    return b_mod_xy, b_mod_xzed

def apply_proj_modifiers(context, obj, copy_hide_modifiers, proj_mod_xy, proj_mod_xzed, uv_map_xy, uv_map_xzed, \
    cam_xy, cam_xzed):
    set_active_object(context, obj)

    # apply last modifier first
    bpy.ops.object.modifier_apply(modifier=proj_mod_xzed.name)
    bpy.ops.object.modifier_apply(modifier=proj_mod_xy.name)

    if copy_hide_modifiers:
        # re-create them, instead of copying - haha!
        b_mod_xy, b_mod_xzed = add_object_uv_project_mods(obj, uv_map_xy, uv_map_xzed, cam_xy, cam_xzed)
        # hide them
        b_mod_xy.show_viewport = False
        b_mod_xy.show_render = False
        b_mod_xzed.show_viewport = False
        b_mod_xzed.show_render = False
