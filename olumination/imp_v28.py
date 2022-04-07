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

COLOR_TEXTURE_TYPES = [
    ("ShaderNodeTexBrick", "Brick Texture", "", 1),
    ("ShaderNodeTexChecker", "Checker Texture", "", 2),
    ("ShaderNodeTexCoord", "TexCoord Texture", "", 3),
    ("ShaderNodeTexEnvironment", "Environment Texture", "", 4),
    ("ShaderNodeTexGradient", "Gradient Texture", "", 5),
    ("ShaderNodeTexIES", "IES Texture", "", 6),
    ("ShaderNodeTexImage", "Image Texture", "", 7),
    ("ShaderNodeTexMagic", "Magic Texture", "", 8),
    ("ShaderNodeTexMusgrave", "Musgrave Texture", "", 9),
    ("ShaderNodeTexNoise", "Noise Texture", "", 10),
    ("ShaderNodeTexPointDensity", "Point Density Texture", "", 11),
    ("ShaderNodeTexSky", "Sky Texture", "", 12),
    ("ShaderNodeTexVoronoi", "Voronoi Texture", "", 13),
    ("ShaderNodeTexWave", "Wave Texture", "", 14),
    ("ShaderNodeTexWhiteNoise", "White Noise Texture", "", 15),
]

# this function also works to multiply Quaternion * Vector
def matrix_vector_mult(m, v):
    return m @ v

def get_mesh_post_modifiers(context, obj):
    depsgraph = context.evaluated_depsgraph_get()
    object_eval = obj.evaluated_get(depsgraph)
    return bpy.data.meshes.new_from_object(object_eval)

def create_object_cube(cube_name, cube_size, cube_loc):
    bpy.ops.mesh.primitive_cube_add(size=cube_size*2, location=cube_loc)
    new_obj = bpy.context.active_object
    new_obj.name = cube_name
    return new_obj

def create_object_plane(plane_name, plane_size, plane_loc, plane_calc_uvs):
    bpy.ops.mesh.primitive_plane_add(size=plane_size*2, calc_uvs=plane_calc_uvs, location=plane_loc)
    new_obj = bpy.context.active_object
    new_obj.name = plane_name
    return new_obj

def create_object_icosphere(sphere_name, num_sphere_subdiv, sphere_radius, sphere_loc):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=num_sphere_subdiv, radius=sphere_radius, location=sphere_loc)
    new_obj = bpy.context.active_object
    new_obj.name = sphere_name
    return new_obj

def create_object_light(light_name, light_type, light_radius, light_loc):
    bpy.ops.object.light_add(type=light_type, radius=light_radius, location=light_loc)
    new_obj = bpy.context.active_object
    new_obj.name = light_name
    return new_obj

def object_add_modifier_taper(obj, modifier_name, t_factor):
    d_mod = obj.modifiers.new(modifier_name, "SIMPLE_DEFORM")
    d_mod.deform_method = "TAPER"
    d_mod.factor = t_factor
    d_mod.deform_axis = "Z"
    return d_mod

def set_object_hide_view(obj, hide_val):
    obj.hide_set(hide_val)

def get_object_hide_view(obj):
    return obj.hide_viewport

def set_object_list_hide_view(obj_list, hide_state):
    for obj in obj_list:
        set_object_hide_view(obj, hide_state)

def set_object_display_type(obj, display_type):
    obj.display_type = display_type

def set_active_object(context, ob):
    context.view_layer.objects.active = ob

def select_object(ob):
    ob.select_set(True)

def deselect_object(ob):
    ob.select_set(False)

def select_objects(ob_list):
    for ob in ob_list:
        select_object(ob)

def deselect_objects(ob_list):
    for ob in ob_list:
        deselect_object(ob)

def scene_link_object(context, ob):
    context.scene.collection.objects.link(ob)

def get_all_objects_list():
    a_list = []
    for c in range(len(bpy.data.collections)):
        for i in range(len(bpy.data.collections[c].all_objects)):
            a_list.append(bpy.data.collections[c].all_objects[i])
    return a_list

def get_lights_from_selected(context):
    obj_list = []
    for obj in context.selected_objects:
        if obj.type == "LIGHT":
            obj_list.append(obj)
    return obj_list

def get_all_lights():
    obj_list = []
    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            obj_list.append(obj)
    return obj_list

def set_light_color(light, color):
    bpy.data.lights[light.data.name].color = color

def set_mat_diffuse_color(mat, mat_diffuse_RGBA):
    mat.diffuse_color = (mat_diffuse_RGBA[0], mat_diffuse_RGBA[1], mat_diffuse_RGBA[2], mat_diffuse_RGBA[3])
    mat.specular_intensity = 0
    mat.roughness = 0

def keyframe_light_color(light_obj):
    light_obj.data.keyframe_insert("color")

def set_light_angular_diameter(light, angular_diameter):
    light.data.angle = angular_diameter

def keyframe_light_angular_diameter(light_obj):
    light_obj.data.keyframe_insert("angle")

def image_pack_image(img):
    img.pack()
