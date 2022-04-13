# OLumination

## Blender Lighting Tools, EEVEE HDRI

General tools to help with HDRI in Cycles and EEVEE, and more to come.
Video tutorial coming soon.

### Sunlit Rig Create
EEVEE and HDRI - currently a bit complicated (as of Blender 3.0).
HDRIs look great in the background of EEVEE renders, but do not correctly add light to the foreground of EEVEE renders.
To work-around this problem, this scripted solution adds the maximum number of suns in EEVEE (max of 8 sun lights as of Blender 3.0.1) to imrove HDRI lighting in Blender EEVEE.
These "sun lights" will get their color, and brightness, from the HDRI image and approximate HDRI lighting in Blender EEVEE.
Each sun light needs light color, brightness, direction, and Angular Diameter (note #1) set correctly.
The last one, Angular Diameter, helps to "smear" the sun's color across an arc of sky - so that a blue sky light can be created with 1 sun light (just one!).
Also, very important, at least 1 sun light is needed to approximate a real "sun" in outdoors scenes (or a real moon, in outdoors night scenes - "lunatic" scenes?).
8 = 7 + 1
- 1 light is brighter than the rest
  - it comes with an Occluding Disk (ODisk) to block the bright "real sun" so that the other "sky suns" can have their colors calculated accurately
  - how to match the ODisk with the real sun in the HDRI, after creating the Sunlit Rig (Create Rig must happen first):
    1) look in the OLumin panel in Blender, and use the Sunlit Rig Other -> Point Cam at Odisk button
    2) Go to the Scene Properties tab in Blender
    3) Change scene's active Camera to: SunlitCamera
	4) View through the active camera (Blender's View3D window -> View -> Cameras -> Active Camera)
    5) select the Sunlit armature and switch from Object mode to Pose mode
    6) select the ODisk Target (looks like a wireframe cube), and move the ODisk Target to point at brightest light in the background environment image (the HDRI background)
    7) select the ODisk bone (looks like a wireframe circle), and increase the size of the Occluding Disk to match the HDRI sun's size
  - the ODisk (and the attached bright "sun" light) should now be pointed from the sun in the HDRI background, and the ODisk should cover the entire bright "real" sun in the background

This requires getting the average pixel colors for large parts of HDRIs, for multiple lights. Also, the Angular Diameter needs to be calculated and set.
Sunlit Rig automates the process of setting positions, angles (object angles, and the sun light's Angular Diameter), and color.
The whole setup can be easily copied from one Sunlit Rig to another by way of the Armature's Pose (select Sunlit Rig armature, and go to Pose mode, copy pose from/to Sunlit armatures)
Difficult to explain with words alone, tutorial video coming soon.

1) note 1: [Angular Diameter](https://en.wikipedia.org/wiki/Angular_diameter) is the apparent size of an object (like Earth's sun), as an arc in the sky, and is measured in radians (degrees angle)

### Sunlit Rig Other
Various functions to use with a Sunlit Rig, e.g.
  - bake sensor images, to be used in sun color calculations
  - use sensor image to calculate sun color automatically
  - set sun lights' angular diameter automatically
  - select all sunlit rigs with one button
  - set 3D angles of suns / occluding disks using from middle of 3DView window (where you are looking), or Camera's point of view

### Proxy Metric
Proxy Metric is still under construction, may be weird.
One button to create human sized rig, to estimate distances to points in HDRI background, to re-create geometry in HDRI.
E.g. use with "outdoor" HDRIs to re-create ground, hills, houses, etc.
Note: This function requires the Rigify addon to be enabled. Rigify is included with Blender, so enable the addon:
  - Use Blender's 'Edit' menu (Blender version 2.8 and later), or 'File' menu (Blender version 2.79)
  - Click Preferences
  - Go to the Addons section, and search for Rigify
  - Enable Rigify addon

### World Envo
World Environment, in two parts:
  - Mobile Background
  - Object XYZ to UVW

#### Mobile Background
Add some "depth" to flat HDRI environments with Mobile Background. Select the Camera that will control the background, and press the World Envo -> Mobile Background button.
This will add a world background material shader to simulate movement of camera within HDRI. Adjust the Scale part of the Vector mapping, in the world material shader, to set the distance to the "floor" plane. This is a bit of a difficult process and usually requires synchronizing with geometry in the scene. I.e. It's a good idea to set up the geometry in the scene with the HDRI before adjusting the "floor plane".

Notes:
  - the Scale part of the Vector Mapping is an inverse relationship with the distance to the "floor plane"
  - in other words, if the "floor plane" is 2 meters down (-Z), then set Scale vector in Vector Mapping node to (0.5, 0.5, 0.5)
    - the inverse of 2 is 1/2
    - use 0.5 because 0.5 = 1/2 meters
	- this is a rough estimate, modify the Scale as needed

#### Object XYZ to UVW
Summary:
Two reasons (of many) for this:
- prevent procedural texture "sliding" when mesh is deformed (note #1), or
- save the HDRI environment image to a mesh (note #2) and apply any deforms (note #1) to mesh, without warping/sliding of procedural texture
  - the environment image uses a 3D input, 2D alone would add warping/distortion of HDRI image
  - 3D coordinates are interpolated across face surface to produce original XYZ coordinates exactly
- multiple XYZ to UVW maps can be applied to the same mesh, at different times
  - e.g. before and after mesh is deformed, to enable blending between coordinate systems
    - e.g. fix texture slide/warp problem discovered while rendering long animation
1) note 1: Cloth Sim, Soft-Body Sim, Object Modifier, Shapekey
2) note 2: XYZ to UVW Color Texture Type=Environment

More info:
Saves the current XYZ locations of all vertexes (saved into two UV Maps), so that vertexes can be deformed and keep their original XYZ mapping.
If "Copy and Hide Modifiers" is enabled:
  - the "UV Project" object modifiers will be available after the XYZ to UVW map is created
  - un-hide the "UV Project" modifiers to see what would happen if XYZ to UVW was applied again
    - these modifiers can be copied and applied again, but manually - no "easy button" to do this yet
