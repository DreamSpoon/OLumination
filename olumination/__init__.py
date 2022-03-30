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
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "View 3D -> Tools -> OLumin",
    "category": "Lighting",
}

import math
import bpy
from .sunlit_rig import (OLuminSL_CreateRig, OLuminSL_BakeSelectedSensors, OLuminSL_BakeRigSensors,
    OLuminSL_SensorImagePack, OLuminSL_SetSelectSunColor, OLuminSL_SetRigSunColor, OLuminSL_SetSelectSunAngle,
    OLuminSL_SetRigSunAngle, OLuminSL_SelectVisibleRigs, OLuminSL_SelectAllRigs, OLuminSL_SelectRigRegularSensors,
    OLuminSL_SelectRigODiskSensors, OLuminSL_SelectRigRegularLights, OLuminSL_SelectRigODiskLights)

AngularDiameterEnabled = False
if bpy.app.version < (2,80,0):
    from .imp_v27 import *
    Region = "TOOLS"
else:
    from .imp_v28 import *
    Region = "UI"
    AngularDiameterEnabled = True

class OLUMIN_PT_SunlitRig(bpy.types.Panel):
    bl_label = "Sunlit Rig"
    bl_space_type = "VIEW_3D"
    bl_region_type = Region
    bl_category = "OLumin"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        box = layout.box()
        box.label(text="Create Rig")
        box.operator("olumin_sl.create_sunlit_rig")
        box.prop(scn, "OLuminSL_Hemisphere")
        box.prop(scn, "OLuminSL_SunCount")
        box.prop(scn, "OLuminSL_SunEnergy")
        box.prop(scn, "OLuminSL_SunInitAngle")
        box.prop(scn, "OLuminSL_SunImageWidth")
        box.prop(scn, "OLuminSL_SunImageHeight")
        box.prop(scn, "OLuminSL_SunBlindsLen")
        box.prop(scn, "OLuminSL_ODiskCount")
        box.prop(scn, "OLuminSL_ODiskIncludeSun")
        box.prop(scn, "OLuminSL_ODiskSunEnergy")
        box.prop(scn, "OLuminSL_ODiskSunInitAngle")
        box.prop(scn, "OLuminSL_ODiskSunImageWidth")
        box.prop(scn, "OLuminSL_ODiskSunImageHeight")
        box.prop(scn, "OLuminSL_ODiskSunBlindsLen")
        box.prop(scn, "OLuminSL_ODiskAddTaperDriver")
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
        ##box.prop(scn, "OLuminSL_DeselectFirst")   # boolean, deselect objects before selecting desired objects

classes = [
    OLUMIN_PT_SunlitRig,
    OLuminSL_CreateRig,
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
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    register_props()

def register_props():
    bts = bpy.types.Scene
    bp = bpy.props

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
    bts.OLuminSL_ODiskAddTaperDriver = bp.BoolProperty(name="ODisk Taper Driver", description="Add taper driver to " +
        "Occluding Disk blinds so that scaling the Occluding Disk will taper the ODisk blinds properly. The " +
        "drawback to enabling this this option is that it requires 'Reload Trusted' or 'Make Trusted' when loading .Blend " +
        "files in some versions of Blender", default=True)

    bts.OLuminSL_BakeSamples = bp.IntProperty(name="Custom Bake Samples", description="Render sample value to use " +
        "while baking sensor images only. Cycles render sample count is temporarily changed during sensor image bake",
        default=128, min=1)
    bts.OLuminSL_BakeHideAllLights = bp.BoolProperty(name="Bake Hide All Lights", description="Hide all lights (not " +
        "just lights attached to Sunlit Rig) before baking sensor images", default=True)

    bts.OLuminSL_KeyframeColor = bp.BoolProperty(name="Keyframe Color", description="Add keyframe when setting " +
        "sun color, to enable animation of suns. E.g. Add keyframes when major changes in environment lighting " +
        "occur, such as lightning strikes, day/night changes, etc", default=False)
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

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()