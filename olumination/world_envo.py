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

# bpy.context.scene.world.node_tree.nodes

if bpy.app.version < (2,80,0):
    from .imp_v27 import *
else:
    from .imp_v28 import *

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
