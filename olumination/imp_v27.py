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

def matrix_vector_mult(m, v):
    return m * v

def get_mesh_post_modifiers(obj):
    return obj.to_mesh(bpy.context.scene, True, 'PREVIEW')

def create_object_cube(cube_name, cube_size, cube_loc):
    bpy.ops.mesh.primitive_cube_add(radius=cube_size, location=cube_loc)
    new_obj = bpy.context.active_object
    new_obj.name = cube_name
    return new_obj

def create_object_plane(plane_name, plane_size, plane_loc, plane_calc_uvs):
    bpy.ops.mesh.primitive_plane_add(radius=plane_size, calc_uvs=plane_calc_uvs, location=plane_loc)
    new_obj = bpy.context.active_object
    new_obj.name = plane_name
    return new_obj

def create_object_icosphere(sphere_name, num_sphere_subdiv, sphere_radius, sphere_loc):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=num_sphere_subdiv, size=sphere_radius, location=sphere_loc)
    new_obj = bpy.context.active_object
    new_obj.name = sphere_name
    return new_obj

def create_object_light(light_name, light_type, light_radius, light_loc):
    bpy.ops.object.lamp_add(type=light_type, radius=light_radius, location=light_loc)
    new_obj = bpy.context.active_object
    new_obj.name = light_name
    return new_obj

def object_add_modifier_taper(obj, modifier_name, t_factor):
    d_mod = obj.modifiers.new(modifier_name, "SIMPLE_DEFORM")
    d_mod.deform_method = "TAPER"
    d_mod.factor = t_factor
    return d_mod

def set_object_hide_view(obj, hide_state):
    obj.hide = hide_state

def get_object_hide_view(obj):
    return obj.hide

def set_object_list_hide_view(obj_list, hide_state):
    for obj in obj_list:
        set_object_hide_view(obj, hide_state)

def set_object_display_type(obj, display_type):
    obj.draw_type = display_type

def set_active_object(context, ob):
    context.scene.objects.active = ob

def select_object(ob):
    ob.select = True

def deselect_object(ob):
    ob.select = False

def select_objects(ob_list):
    for ob in ob_list:
        select_object(ob)

def deselect_objects(ob_list):
    for ob in ob_list:
        deselect_object(ob)

def scene_link_object(context, ob):
    context.scene.objects.link(ob)

def set_object_hide(obj, hide_val):
    obj.hide = hide_val

def get_all_objects_list():
    a_list = []
    for i in range(len(bpy.context.scene.objects)):
        a_list.append(bpy.context.scene.objects[i])
    return a_list

def set_light_color(light, color):
    bpy.data.lamps[light.data.name].color = color

# TODO finish this
def keyframe_light_color(light):
    print("TODO: Add keyframe to light color of light " + light.name)

# TODO finish this
def set_light_angular_diameter(light, lit_max_angle):
    print("TODO: Set light angular diameter of light " + light.name)

# TODO finish this
def keyframe_light_angular_diameter(light):
    print("TODO: Add keyframe to angular diameter of light " + light.name)

def set_mat_diffuse_color(mat, mat_diffuse_RGBA):
    mat.diffuse_color = (mat_diffuse_RGBA[0], mat_diffuse_RGBA[1], mat_diffuse_RGBA[2])

def keyframe_light_color(light_obj):
    light_obj.data.keyframe_insert("color", 0)
    light_obj.data.keyframe_insert("color", 1)
    light_obj.data.keyframe_insert("color", 2)

def set_light_angular_diameter(light, angular_diameter):
    print()

def keyframe_light_angular_diameter(light_obj):
    print()

def image_pack_image(img):
    img.pack(as_png=True)
