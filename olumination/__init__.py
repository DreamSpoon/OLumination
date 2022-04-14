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

# OLumination
# v0.1
# Blender Addon
# Tools to help with HDRI environment lighting, and EEVEE and cycles lighting generally.
# Sunlit Rig
# Create Sunlit Rig for make benefit glorious illumination of EEVEE-standard scenes, by automating the
# process of adding multiple "Sun" type lights to simulate lighting from HDRI backgrounds.
# Note: EEVEE-standard scene lighting is currently limited to a maximum of 8 independent sun light objects
#       (any extra sun lights will be ignored by EEVEE).

bl_info = {
    "name": "OLumination",
    "description": "Tools for use with EEVEE and Cycles lighting, including HDRI environment lighting in EEVEE.",
    "author": "Dave",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View 3D -> Tools -> OLumin",
    "category": "Lighting",
}

import math
import bpy

from .sunlit_rig import (OLuminSL_CreateRig, OLuminSL_FixRigVisibility, OLuminSL_BakeSelectedSensors,
    OLuminSL_BakeRigSensors, OLuminSL_SensorImagePack, OLuminSL_SetSelectSunColor, OLuminSL_SetRigSunColor,
    OLuminSL_SetSelectSunAngle, OLuminSL_SetRigSunAngle, OLuminSL_SelectVisibleRigs, OLuminSL_SelectAllRigs,
    OLuminSL_SelectRigRegularSensors, OLuminSL_SelectRigODiskSensors, OLuminSL_SelectRigRegularLights,
    OLuminSL_SelectRigODiskLights, OLuminSL_PointRegularFromView, OLuminSL_PointODiskFromView, OLuminSL_PointCamAtODisk)
from .proxy_metric import (OLuminPM_CreateSimpleHumanProxy, OLuminPM_DropVertex)
from .light_color import OLuminLC_ColorMath
from .light_energy import OLuminLE_MathLightEnergy
from .world_envo import OLuminWE_MobileBackground
from .xyz_to_uvw import (OLuminXTU_ObjectShaderXYZMap, OLuminXTU_FixXYZCameras,
    XTU_CAMERA_NAME_XY, XTU_CAMERA_NAME_XZ, XTU_XY_MAP_NAME, XTU_XZ_MAP_NAME)

AngularDiameterEnabled = False
if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"
    AngularDiameterEnabled = True

class OLUMIN_PT_SunlitRigCreate(bpy.types.Panel):
    bl_label = "Sunlit Rig Create"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Create Rig")
        box.prop(scn, "OLuminSL_CreateAdvancedOptions")
        box.operator("olumin_sl.create_sunlit_rig")
        if scn.OLuminSL_CreateAdvancedOptions:
            box.prop(scn, "OLuminSL_BaseSphereSubdiv")
        box.prop(scn, "OLuminSL_Hemisphere")
        box.prop(scn, "OLuminSL_SunCount")
        box.prop(scn, "OLuminSL_SunEnergy")
        box.prop(scn, "OLuminSL_SunInitAngle")
        if scn.OLuminSL_CreateAdvancedOptions:
            box.prop(scn, "OLuminSL_SunImageWidth")
            box.prop(scn, "OLuminSL_SunImageHeight")
            box.prop(scn, "OLuminSL_SunBlindsLen")
        box.prop(scn, "OLuminSL_ODiskCount")
        box.prop(scn, "OLuminSL_ODiskIncludeSun")
        box.prop(scn, "OLuminSL_ODiskSunEnergy")
        box.prop(scn, "OLuminSL_ODiskSunInitAngle")
        if scn.OLuminSL_CreateAdvancedOptions:
            box.prop(scn, "OLuminSL_ODiskSunImageWidth")
            box.prop(scn, "OLuminSL_ODiskSunImageHeight")
            box.prop(scn, "OLuminSL_ODiskSunBlindsLen")
            box.prop(scn, "OLuminSL_AllowDrivers")

class OLUMIN_PT_SunlitRigOther(bpy.types.Panel):
    bl_label = "Sunlit Rig Other"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        box = layout.box()
        box.prop(scn, "OLuminSL_OtherAdvancedOptions")
        box = layout.box()
        box.operator("olumin_sl.fix_rig_visibility")
        box.prop(scn, "OLuminSL_HideBlindsToo")
        box = layout.box()
        box.label(text="Point Light with View Center")
        box.operator("olumin_sl.point_regular_from_view")
        box.prop(scn, "OLuminSL_RegularNumPointFromView")
        box.operator("olumin_sl.point_odisk_from_view")
        box.prop(scn, "OLuminSL_ODiskNumPointFromView")
        box.prop(scn, "OLuminSL_ReverseLightPointDirection")
        box.operator("olumin_sl.point_cam_at_odisk")
        box = layout.box()
        box.label(text="Rig Sensor Input")
        box.operator("olumin_sl.bake_selected_sensors")
        box.operator("olumin_sl.bake_rig_sensors")
        box.prop(scn, "OLuminSL_BakeSamples")
        box.prop(scn, "OLuminSL_BakeHideAllLights")
        box.operator("olumin_sl.image_pack")
        box = layout.box()
        box.label(text="Rig Sun Output")
        box.operator("olumin_sl.select_sensors_to_sun_color")
        box.operator("olumin_sl.rig_sensors_to_sun_color")
        box.prop(scn, "OLuminSL_KeyframeColor")
        if scn.OLuminSL_OtherAdvancedOptions:
            box.prop(scn, "OLuminSL_SensorSampleWidthPct")
            box.prop(scn, "OLuminSL_SensorSampleHeightPct")
            box.prop(scn, "OLuminSL_ODiskSensorSampleWidthPct")
            box.prop(scn, "OLuminSL_ODiskSensorSampleHeightPct")
        if AngularDiameterEnabled:
            box.operator("olumin_sl.select_blinds_angle_to_sun_angle")
            box.operator("olumin_sl.rig_blinds_angle_to_sun_angle")
            box.prop(scn, "OLuminSL_KeyframeAngle")
        box = layout.box()
        box.label(text="Sunlit Rig Select")
        box.operator("olumin_sl.select_visible_rigs")
        box.operator("olumin_sl.select_all_rigs")
        box.label(text="Sunlit Rig Object Select")
        box.operator("olumin_sl.select_rig_regular_sensors")
        box.operator("olumin_sl.select_rig_odisk_sensors")
        box.operator("olumin_sl.select_rig_regular_lights")
        box.operator("olumin_sl.select_rig_odisk_lights")

class OLUMIN_PT_LightColor(bpy.types.Panel):
    bl_label = "EEVEE Light Color"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Adjust Selected Lights")
        box.operator("olumin_lc.math_light_color")
        box.prop(scn, "OLuminLC_MathFunction")
        box.prop(scn, "OLuminLC_MathColorComponent")
        box.prop(scn, "OLuminLC_MathInputValue")

class OLUMIN_PT_LightEnergy(bpy.types.Panel):
    bl_label = "EEVEE Light Energy"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Adjust Selected Lights")
        box.operator("olumin_le.math_light_energy")
        box.prop(scn, "OLuminLE_MathFunction")
        box.prop(scn, "OLuminLE_MathInputValue")

class OLUMIN_PT_ProxyMetric(bpy.types.Panel):
    bl_label = "Proxy Metric"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Create Proxy Metric")
        box.operator("olumin_pm.create_proxy_metric_simple_human")

class OLUMIN_PT_WorldEnvo(bpy.types.Panel):
    bl_label = "World Envo"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="World Material Shader")
        box.operator("olumin_we.mobile_background")

class OLUMIN_PT_XYZ_to_UVW(bpy.types.Panel):
    bl_label = "XYZ to UVW"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        box = layout.box()
        box.label(text="Object Material Shader")
        box.operator("olumin_xtu.fix_xyz_cameras")
        box.prop(scn, "OLuminXTU_FixCamAll")

        box.operator("olumin_xtu.object_shader_xyz_map")

        box.prop(scn, "OLuminXTU_AppendMaterial")
        sub1 = box.column()
        sub1.active = scn.OLuminXTU_AppendMaterial
        sub1.prop(scn, "OLuminXTU_ColorTextureType")
        sub1.prop(scn, "OLuminXTU_NewMatPerObj")
        # add to existing is only available if not forced to create new material per selected object
        sub2 = box.column()
        sub2.active = (not scn.OLuminXTU_NewMatPerObj) and scn.OLuminXTU_AppendMaterial
        sub2.prop(scn, "OLuminXTU_AddToExisting")

        box.label(text="Modifiers")
        box.prop(scn, "OLuminXTU_ApplyModifiers")
        sub = box.column()
        sub.active = scn.OLuminXTU_ApplyModifiers
        sub.prop(scn, "OLuminXTU_CopyHideModifiers")
        box.prop(scn, "OLuminXTU_ReuseCameras")
        sub = box.column()
        sub.active = scn.OLuminXTU_ReuseCameras
        sub.prop(scn, "OLuminXTU_ReuseCameraNameXY")
        sub.prop(scn, "OLuminXTU_ReuseCameraNameXZ")
        box.prop(scn, "OLuminXTU_ReuseUVMaps")

        sub = box.column()
        sub.active = scn.OLuminXTU_ReuseUVMaps
        sub.prop(scn, "OLuminXTU_ReuseUVNameXY")
        sub.prop(scn, "OLuminXTU_ReuseUVNameXZ")

class OLUMIN_MT_menu(bpy.types.Menu):
    bl_idname = 'olumin_MT_menu_cls'
    bl_label = 'OLumination operators'

    def draw(self, context):
        layout = self.layout
        layout.operator(OLuminPM_DropVertex.bl_idname)

def menu_MT_func(self, context):
    self.layout.menu(OLUMIN_MT_menu.bl_idname)

classes = [
    OLUMIN_PT_SunlitRigCreate,
    OLuminSL_CreateRig,
    OLUMIN_PT_SunlitRigOther,
    OLuminSL_FixRigVisibility,
    OLuminSL_BakeSelectedSensors,
    OLuminSL_BakeRigSensors,
    OLuminSL_SensorImagePack,
    OLuminSL_SetSelectSunColor,
    OLuminSL_SetRigSunColor,
    OLuminSL_SetSelectSunAngle,
    OLuminSL_SetRigSunAngle,
    OLuminSL_SelectVisibleRigs,
    OLuminSL_SelectAllRigs,
    OLuminSL_SelectRigRegularSensors,
    OLuminSL_SelectRigODiskSensors,
    OLuminSL_SelectRigRegularLights,
    OLuminSL_SelectRigODiskLights,
    OLuminSL_PointRegularFromView,
    OLuminSL_PointODiskFromView,
    OLuminSL_PointCamAtODisk,
    OLUMIN_PT_LightColor,
    OLuminLC_ColorMath,
    OLUMIN_PT_LightEnergy,
    OLuminLE_MathLightEnergy,
    OLUMIN_PT_ProxyMetric,
    OLuminPM_CreateSimpleHumanProxy,
    OLuminPM_DropVertex,
    OLUMIN_PT_WorldEnvo,
    OLuminWE_MobileBackground,
    OLUMIN_PT_XYZ_to_UVW,
    OLuminXTU_ObjectShaderXYZMap,
    OLuminXTU_FixXYZCameras,
    OLUMIN_MT_menu,
]

def register():
    bpy.types.VIEW3D_MT_object.append(menu_MT_func)
    for cls in classes:
        bpy.utils.register_class(cls)
    register_props()

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_MT_func)
    for cls in classes:
        bpy.utils.unregister_class(cls)

def register_props():
    bts = bpy.types.Scene
    bp = bpy.props

    bts.OLuminSL_CreateAdvancedOptions = bp.BoolProperty(name="Advanced Options", description="Show advanced options " +
        "for Sunlig Rig Create panel", default=False)
    bts.OLuminSL_AllowDrivers = bp.BoolProperty(name="Allow Drivers", description="Allow drivers to be used for " +
        "automatically adjusting object Modifier fields. The drawback to enabling this this option is that it " +
        "requires 'Reload Trusted' or 'Make Trusted' when loading .Blend files in some versions of Blender",
        default=True)

    bts.OLuminSL_BaseSphereSubdiv = bp.IntProperty(name="Base Subdiv", description="Base icosphere subidivision " +
        "count. The 'base sphere' used to project the Regular sun blinds is an icosphere object, this is the " +
        "icosphere subdivision count", default=4, min=1)

    bts.OLuminSL_Hemisphere = bp.BoolProperty(name="Hemisphere", description="Create hemisphere Sunlit Rig to " +
        "capture one half of the environment (360d of longitude, 90d of latitiude)", default=True)
    bts.OLuminSL_SunCount = bp.IntProperty(name="Sun Count", description="Number of regular suns to create with " +
        "Sunlit Rig", default=7, min=0)
    bts.OLuminSL_SunEnergy = bp.FloatProperty(name="Sun Energy", description="Initial energy value of Sunlit Rig " +
        "regular suns", default=1.0, min=0.0)
    bts.OLuminSL_SunInitAngle = bp.FloatProperty(name="Sun Angle", description="Initial angular "
        "diameter (in degrees) of regular sun object(s)", default=math.radians(90), min=0.0, subtype="ANGLE")
    bts.OLuminSL_SunImageWidth = bp.IntProperty(name="Sun Image Width", description="Width (in pixels) of regular " +
        "sensor image to use for color image baking", default=16, min=0, subtype="PIXEL")
    bts.OLuminSL_SunImageHeight = bp.IntProperty(name="Sun Image Height", description="Height (in pixels) of regular " +
        "sensor image to use for color image baking", default=16, min=0, subtype="PIXEL")
    bts.OLuminSL_SunBlindsLen = bp.FloatProperty(name="Sun Blinds Length", description="Length (in meters) of dark " +
        "blinds used when baking sensor images", default=15.0, min=0.0, subtype="DISTANCE")

    bts.OLuminSL_ODiskCount = bp.IntProperty(name="ODisk Count", description="Number of Occluding Disks (ODisks) " +
        "to create. ODisks are used to block out the bright sun area of an HDRI, and add a specialized sun object to " +
        "replace blocked out sun pixels (or brightest spot) of the HDRI environment. \"Specialized\" sun object is " +
        "(usually) brighter than regular sun object, and has a smaller angular diameter", default=1, min=0)
    bts.OLuminSL_ODiskIncludeSun = bp.BoolProperty(name="ODisk Sun Create", description="Create sun object with each " +
        "ODisk", default=True)
    bts.OLuminSL_ODiskSunEnergy = bp.FloatProperty(name="ODisk Sun Energy", description="Initial energy value of " +
        "Sunlit Rig Occluding Disk (ODisk) suns", default=2.0, min=0.0)
    bts.OLuminSL_ODiskSunInitAngle = bp.FloatProperty(name="ODisk Sun Angle", description="Initial angular "
        "diameter (in degrees) of Occluding Disk (ODisk) sun object(s)", default=math.radians(0.5), min=0.0, subtype="ANGLE")
    bts.OLuminSL_ODiskSunImageWidth = bp.IntProperty(name="ODisk Sun Image Width", description="Width (in pixels) of " +
        "Occluding Disk (ODisk) sensor image to use for color image baking", default=16, min=0, subtype="PIXEL")
    bts.OLuminSL_ODiskSunImageHeight = bp.IntProperty(name="ODisk Sun Image Height", description="Height (in pixels) " +
        "of Occluding Disk (ODisk) sensor image to use for color image baking", default=16, min=0, subtype="PIXEL")
    bts.OLuminSL_ODiskSunBlindsLen = bp.FloatProperty(name="ODisk Sun Blinds Length", description="Length (in meters)" +
        " of dark Occluding Disk (ODisk) sun blinds used when baking sensor images", default=1.0, min=0.0,
        subtype="DISTANCE")

    bts.OLuminSL_OtherAdvancedOptions = bp.BoolProperty(name="Advanced Options", description="Show advanced options " +
        "for Sunlig Rig Other panel", default=False)

    bts.OLuminSL_HideBlindsToo = bp.BoolProperty(name="Hide Blinds", description="Hide blinds objects from view " +
        "(blinds will still be visible in renders)", default=True)

    bts.OLuminSL_BakeSamples = bp.IntProperty(name="Custom Bake Samples", description="Render sample value to use " +
        "while baking sensor images only. Cycles render sample count is temporarily changed during sensor image bake",
        default=128, min=1)
    bts.OLuminSL_BakeHideAllLights = bp.BoolProperty(name="Bake Hide All Lights", description="Hide all lights (not " +
        "just lights attached to Sunlit Rig) before baking sensor images", default=True)

    bts.OLuminSL_KeyframeColor = bp.BoolProperty(name="Keyframe Color", description="Add keyframe when setting " +
        "sun color, to enable animation of suns. E.g. Add keyframes when major changes in environment lighting " +
        "occur, such as lightning strikes, day to night changes, etc", default=False)
    bts.OLuminSL_KeyframeAngle = bp.BoolProperty(name="Keyframe Angular Diameter", description="Add keyframe when setting " +
        "sun angular diameter, to enable animation of suns. E.g. Add keyframes when a bright light gets " +
        "larger/smaller in the environment's lighting, like a sun going supernova, etc",
        default=False)
    bts.OLuminSL_SensorSampleWidthPct = bp.FloatProperty(name="Width Sample Pct", description="Regular sun sensor " +
        "image width (in percent of image width) to sample when computing regular sun object's color",
        subtype="PERCENTAGE", default=0.75, min=0.0, max=1.0)
    bts.OLuminSL_SensorSampleHeightPct = bp.FloatProperty(name="Height Sample Pct", description="Regular sun sensor " +
        "image height (in percent of image height) to sample when computing regular sun object's color",
        subtype="PERCENTAGE", default=0.75, min=0.0, max=1.0)
    bts.OLuminSL_ODiskSensorSampleWidthPct = bp.FloatProperty(name="ODisk Width Sample Pct",
        description="Occluding Disk sun sensor image width (in percent of image width) to sample when computing " +
        "ODisk sun object's color", subtype="PERCENTAGE", default=0.5, min=0.0, max=1.0)
    bts.OLuminSL_ODiskSensorSampleHeightPct = bp.FloatProperty(name="ODisk Height Sample Pct",
        description="Occluding Disk sun sensor image height (in percent of image height) to sample when computing " +
        "ODisk sun object's color", subtype="PERCENTAGE", default=0.5, min=0.0, max=1.0)

    bts.OLuminSL_RegularNumPointFromView = bp.IntProperty(name="Regular Sun Index", description="Index of regular " +
        "sun for which pointing direction must be aligned with view center direction", default=0, min=0)
    bts.OLuminSL_ODiskNumPointFromView = bp.IntProperty(name="ODisk Index", description="Index of ODisk for which " +
        "pointing direction must be aligned with view center direction", default=0, min=0)

    bts.OLuminSL_ReverseLightPointDirection = bp.BoolProperty(name="Reverse Light Point Direction",
        description="Reverse the regular 'point at' direction, so light points away from view/camera center",
        default=False)

    bts.OLuminLC_MathFunction = bp.EnumProperty(
        items = [
            ("ADD", "Add", "light.color.component = light.color.component + input.value"),
            ("MULTIPLY", "Multiply", "light.color.component = light.color.component * input.value"),
            ("POWER", "Power", "'light.color.component' is raised to the power 'input.value', or in Python math: " +
                 "pow(light.color.component, input.value)"),
            ("SET", "Set", "light.color.component = input.value"),
        ],
        name = "Math Function",
        description = "Math function to apply with selected light(s) color component, and with math Input Value, " +
            "to selected light(s) color component",
        default = 'POWER')
    bts.OLuminLC_MathColorComponent = bp.EnumProperty(
        # TODO: include groups of components, e.g. RG, RB, GB
        items = [
            ("R", "Red", "math_operation(light.color.r, input.value)"),
            ("G", "Green", "math_operation(light.color.g, input.value)"),
            ("B", "Blue", "math_operation(light.color.b, input.value)"),
            ("H", "Hue", "math_operation(light.color.h, input.value)"),
            ("S", "Saturation", "math_operation(light.color.s, input.value)"),
            ("V", "Value", "math_operation(light.color.v, input.value)"),
        ],
        name = "Color Component",
        description = "Color component of selected light(s) to use with math function",
        default = 'S')
    bts.OLuminLC_MathInputValue = bp.FloatProperty(name="Input Value", description="The color component of the " +
        "selected light(s) will be math'ed with this number, according to Math Function", default=0.5)

    bts.OLuminLE_MathFunction = bp.EnumProperty(
        items = [
            ("ADD", "Add", "light.energy = light.energy + input.value"),
            ("MULTIPLY", "Multiply", "light.energy = light.energy * input.value"),
            ("POWER", "Power", "'light.energy' is raised to the power 'input.value', or in Python math: " +
                 "pow(light.energy, input.value)"),
            ("SET", "Set", "light.energy = input.value"),
        ],
        name = "Math Function",
        description = "Math function to apply with selected light(s) energy, and with math Input Value, to selected " +
        "light(s) energy",
        default = 'MULTIPLY')
    bts.OLuminLE_MathInputValue = bp.FloatProperty(name="Input Value", description="The energy value of the " +
        "selected light(s) will be math'ed with this number, according to Math Function", default=1.0)

    bts.OLuminXTU_FixCamAll = bp.BoolProperty(name="Fix location", description="If enabled, selected cameras' " +
        "rotations and locations will also be reset to defaults", default=True)

    bts.OLuminXTU_AppendMaterial = bp.BoolProperty(name="Append Material", description="If enabled, a simple " +
        "material is created to demonstrate usage of the XYZ to UVW map, by way of the two UV Maps", default=True)

    bts.OLuminXTU_ColorTextureType =  bp.EnumProperty(name="Color Texture Type", description="Type of node to " +
        "create for color input to Principled BSDF", items=COLOR_TEXTURE_TYPES, default="ShaderNodeTexNoise")
    bts.OLuminXTU_NewMatPerObj = bp.BoolProperty(name="Material per Object", description="Create a new material " +
        "shader for each object, instead of grouping object shaders, i.e. each object's material shader is " +
        "independent of all other objects' material shader(s)", default=False)
    bts.OLuminXTU_AddToExisting = bp.BoolProperty(name="Add to Existing Material", description="If enabled, try to " +
        "add shader nodes to object's currently active material. If not enabled, create a new material shader on " +
        "the object, appended after current material(s) on the object", default=False)
    bts.OLuminXTU_ApplyModifiers = bp.BoolProperty(name="Apply Modifiers", description="Apply 'UV Project' " +
        "modifiers to the UV Maps. I.e. Doing this will save a copy of the XYZ coordinates of each vertex into " +
        "the two UV Maps (XY and XZ maps)", default=True)
    bts.OLuminXTU_CopyHideModifiers = bp.BoolProperty(name="Copy and Hide Modifiers", description="Enable this to " +
        "keep a copy of the UV Project modifiers on the selected object(s) after applying them once", default=True)

    bts.OLuminXTU_ReuseCameras = bp.BoolProperty(name="Re-use Cameras", description="Try to re-use existing cameras " +
        "(found by name) for projecting XYZ to UVW onto selected object(s)", default=True)
    bts.OLuminXTU_ReuseCameraNameXY = bp.StringProperty(name="'XY' Cam name", description="Name of camera to use for " +
        "'XY' projection, as part of the XYZ to UVW projection process", default=XTU_CAMERA_NAME_XY)
    bts.OLuminXTU_ReuseCameraNameXZ = bp.StringProperty(name="'XZ' Cam name", description="Name of camera to use for " +
        "'XZ' projection, as part of the XYZ to UVW projection process", default=XTU_CAMERA_NAME_XZ)

    bts.OLuminXTU_ReuseUVMaps = bp.BoolProperty(name="Re-use UV Maps", description="Try to re-use existing UV Maps" +
        "(found by name) for projecting XYZ to UVW onto selected object(s)", default=False)
    bts.OLuminXTU_ReuseUVNameXY = bp.StringProperty(name="'XY' UV Map name", description="Name of UV Map to re-use " +
        "for 'XY' projection, as part of the XYZ to UVW projection process", default=XTU_XY_MAP_NAME)
    bts.OLuminXTU_ReuseUVNameXZ = bp.StringProperty(name="'XZ' UV Map name", description="Name of UV Map to re-use " +
        "for 'XZ' projection, as part of the XYZ to UVW projection process", default=XTU_XZ_MAP_NAME)

if __name__ == "__main__":
    register()
