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

WE_XY_MAP_NAME = "xy_to_uv_map"
WE_XZED_MAP_NAME = "xzed_to_uv_map"

class OLuminWE_MobileBackground(bpy.types.Operator):
    """Enable movement of scene's background texture (e.g. HDRI texture) with drivers attaching it to currently active object"""
    bl_idname = "olumin_we.mobile_background"
    bl_label = "Mobile Background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object == None:
            self.report({'ERROR'}, "Cannot get active_object, make an object active and try again (e.g. click on a visible object)")
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

    # world output - final output
    node_output = tree_nodes.new(type="ShaderNodeOutputWorld")
    node_output.location = (409, 39)

    # background
    node_background = tree_nodes.new(type="ShaderNodeBackground")
    node_background.location = (219, 52)

    # environment texture
    node_environment = tree_nodes.new("ShaderNodeTexEnvironment")
    node_environment.location = (29, 106)

    # vector math
    node_vec_math = tree_nodes.new("ShaderNodeVectorMath")
    node_vec_math.location = (-161, 77)

    # input texture coordinates
    node_tex_coord = tree_nodes.new("ShaderNodeTexCoord")
    node_tex_coord.location = (-351, 119)

    # vector mapping
    node_vec_mapping = tree_nodes.new("ShaderNodeMapping")
    node_vec_mapping.vector_type = "POINT"
    node_vec_mapping.location = (-532, -136)

    # add drivers to the input to the Vector Mapping node, connected to active_object
    vec_mapping_fcurves = []
    # create tuples so a 'for' loop can be used
    vec_mapping_fcurves.append( (node_vec_mapping.inputs["Vector"].driver_add("default_value", 0), "location.x") )
    vec_mapping_fcurves.append( (node_vec_mapping.inputs["Vector"].driver_add("default_value", 1), "location.y") )
    vec_mapping_fcurves.append( (node_vec_mapping.inputs["Vector"].driver_add("default_value", 2), "location.z") )
    for fc, d_path in vec_mapping_fcurves:
        v = fc.driver.variables.new()
        v.name                 = "var"
        v.targets[0].id        = context.active_object
        v.targets[0].data_path = d_path
        fc.driver.expression = v.name

    # link the shader nodes
    tree_links = scn_w.node_tree.links
    tree_links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    tree_links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

    tree_links.new(node_vec_math.outputs["Vector"], node_environment.inputs["Vector"])

    # add Generated Vector (3 dimensional vector) to Vector Mapping node, Vector Mapping node uses drivers and
    # allows user input
    tree_links.new(node_tex_coord.outputs["Generated"], node_vec_math.inputs[0])
    tree_links.new(node_vec_mapping.outputs["Vector"], node_vec_math.inputs[1])

class OLuminWE_ObjectShaderXYZ_Map(bpy.types.Operator):
    """With selected objects, append a new shader to capture XYZ vertex coordinates and store them in two UV maps """ \
    """for resultant XYZ -> UVW mapping. E.g. Use when applying noise texture node to a mesh that will be deformed by """ \
    """shapekeys/simulation. Note: Widgets also created and hidden"""
    bl_idname = "olumin_we.object_shader_xyz_map"
    bl_label = "Object Shader XYZ"
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
            uv_map_xy, uv_map_xzed = create_xy_and_xzed_maps(obj)

            if scn.OLuminWE_NewMatPerObj:
                # create a completely new material shader and append material to each object
                mat_shader_per_obj = create_xyz_to_uvw_mat_shader(None, uv_map_xy.name, uv_map_xzed.name)
                obj.data.materials.append(mat_shader_per_obj)
            else:
                if scn.OLuminWE_AddToExisting and obj.active_material != None:
                    create_xyz_to_uvw_mat_shader(obj.active_material, uv_map_xy.name, uv_map_xzed.name)
                else:
                    # check if current combination of (uv_map_xy.name, uv_map_xzed.name) have been used, and get that material

                    xy_name_dictionary = grp_mat_shaders.get(uv_map_xy.name)
                    if xy_name_dictionary is None:
                        # create the dictionary linked to the unique uv_map_xy.name
                        grp_mat_shaders[uv_map_xy.name] = {}
                        xy_name_dictionary = grp_mat_shaders[uv_map_xy.name]
                    obj_mat_shader = xy_name_dictionary.get(uv_map_xzed.name)
                    if obj_mat_shader is None:
                        # create the mat because it wasn't found in the name combinations nested-dictionary
                        obj_mat_shader = create_xyz_to_uvw_mat_shader(None, uv_map_xy.name, uv_map_xzed.name)
                        # add the material to the nested-dictionary, for use later if needed
                        # this will reduce the amount of redundant material shaders created
                        xy_name_dictionary[uv_map_xzed.name] = obj_mat_shader
                        # append the new material shader
                        obj.data.materials.append(obj_mat_shader)
                    else:
                        # add the nodes to the pre-existing material shader
                        create_xyz_to_uvw_mat_shader(obj_mat_shader, uv_map_xy.name, uv_map_xzed.name)

        return {'FINISHED'}

def create_xy_and_xzed_maps(obj):
    xy_uvmap = obj.data.uv_textures.new(name=WE_XY_MAP_NAME)
    xzed_uvmap = obj.data.uv_textures.new(name=WE_XZED_MAP_NAME)
    return xy_uvmap, xzed_uvmap

def create_xyz_to_uvw_mat_shader(prev_mat_shader, xy_uvmap_name, xzed_uvmap_name):
    mat_shader = prev_mat_shader
    if mat_shader == None:
        mat_shader = bpy.data.materials.new(name="xyz_to_uvw_mat")
    mat_shader.use_nodes = True
    tree_nodes = mat_shader.node_tree.nodes

    if prev_mat_shader == None:
        # delete all nodes from the initial object shader setup, if pre-existing material shader is not given
        tree_nodes.clear()

    new_nodes = {}

    node = tree_nodes.new(type="ShaderNodeOutputMaterial")
    node.location = (405.141, 106.707)
    new_nodes["Material Output"] = node

    node = tree_nodes.new(type="ShaderNodeBsdfPrincipled")
    node.location = (203.51, 197.018)
    new_nodes["Principled BSDF"] = node

    node = tree_nodes.new(type="ShaderNodeTexEnvironment")
    node.location = (18.404, 98.668)
    new_nodes["Environment Texture"] = node

    node = tree_nodes.new(type="ShaderNodeCombineXYZ")
    node.location = (-171.596, 54.975)
    new_nodes["Combine XYZ"] = node

    node = tree_nodes.new(type="ShaderNodeUVMap")
    node.location = (-545.431, 56.321)
    node.uv_map = xy_uvmap_name
    new_nodes["UV Map"] = node

    node = tree_nodes.new(type="ShaderNodeUVMap")
    node.location = (-543.758, -71.373)
    node.uv_map = xzed_uvmap_name
    new_nodes["UV Map.001"] = node

    node = tree_nodes.new(type="ShaderNodeSeparateXYZ")
    node.location = (-340.174, 77.177)
    new_nodes["Separate XYZ"] = node

    node = tree_nodes.new(type="ShaderNodeSeparateXYZ")
    node.location = (-340.712, -46.002)
    new_nodes["Separate XYZ.001"] = node

    tree_links = mat_shader.node_tree.links
    tree_links.new(new_nodes["UV Map"].outputs[0], new_nodes["Separate XYZ"].inputs[0])
    tree_links.new(new_nodes["UV Map.001"].outputs[0], new_nodes["Separate XYZ.001"].inputs[0])
    tree_links.new(new_nodes["Separate XYZ"].outputs[0], new_nodes["Combine XYZ"].inputs[0])
    tree_links.new(new_nodes["Separate XYZ"].outputs[1], new_nodes["Combine XYZ"].inputs[1])
    tree_links.new(new_nodes["Separate XYZ.001"].outputs[1], new_nodes["Combine XYZ"].inputs[2])
    tree_links.new(new_nodes["Combine XYZ"].outputs[0], new_nodes["Environment Texture"].inputs[0])
    tree_links.new(new_nodes["Environment Texture"].outputs[0], new_nodes["Principled BSDF"].inputs[0])
    tree_links.new(new_nodes["Principled BSDF"].outputs[0], new_nodes["Material Output"].inputs[0])

    return mat_shader
