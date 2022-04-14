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
    if bpy.app.version >= (2,80,0):
        node.target = "CYCLES"
    new_nodes["World Output"] = node

    # add EEVEE stuff
    if bpy.app.version >= (2,80,0):
        node = tree_nodes.new(type="ShaderNodeMixShader")
        node.location = (614.089, -81.285)
        new_nodes["Mix Shader"] = node

        node = tree_nodes.new(type="ShaderNodeOutputWorld")
        node.location = (787.293, -97.521)
        new_nodes["World Output.001"] = node
        node.target = "EEVEE"

        node = tree_nodes.new(type="ShaderNodeLightPath")
        node.location = (162.052, -129.775)
        new_nodes["Light Path"] = node

        node = tree_nodes.new(type="ShaderNodeBackground")
        node.location = (412.171, -180.072)
        new_nodes["Background.001"] = node

        node = tree_nodes.new(type="ShaderNodeBackground")
        node.location = (406.071, -27.986)
        node.inputs[1].default_value = 0.1
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
