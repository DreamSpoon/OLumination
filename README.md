# OLumination

## Blender Lighting Tools, EEVEE HDRI

General tools to help with HDRI in Cycles and EEVEE, and more to come.
Video tutorial coming soon.

### Sunlit Rig Create
Add the max number of suns in EEVEE (max of 8 sun lights as of Blender 3.0.1) to imrove HDRI lighting in Blender EEVEE.
This requires getting the average pixel colors for large parts of HDRIs, for multiple lights. Also, the angular diameter needs to be calculated and set.
Sunlit Rig automates the process of setting positions, angles (object angles, and the sun light's Angular Diameter), and color.
The whole setup can be easily copied from one Sunlit Rig to another by way of the Armature's Pose (select Sunlit Rig armature, and go to Pose mode, copy pose from/to Sunlit armatures)
Difficult to explain with words alone, tutorial video coming soon.

### Sunlit Rig Other
Various functions to use with a Sunlit Rig, e.g.
  - bake sensor images, to be used in sun color calculations
  - use sensor image to calculate sun color automatically
  - set sun lights' angular diameter automatically
  - select all sunlit rigs with one button
  - set 3D angles of suns / occluding disks using from middle of 3DView window (where you are looking), or Camera's point of view

### Proxy Metric
To make it easier to create geometry in Blender that matches an HDRI background, quickly create objects that can be used to "guess the geometry" more simply/accurately.
E.g. Add a human meta-rig to place in the scene and guess positions of points on uneven ground (e.g. nearby parts of grassy hill).
Note: This function requires the Rigify addon to be enabled. Rigify is included with Blender, so enable the addon:
  - Use Blender's 'Edit' menu (Blender version 2.8 and later), or 'File' menu (Blender version 2.79)
  - Click Preferences
  - Go to the Addons section, and search for Rigify
  - Enable Rigify addon

### World Envo
Two parts:
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

#### Object XYZ to UVW
Very useful when using soft body / cloth sims with procedural textures that need XYZ coordinates.
I.e. the procedural texture appears to stand still while the mesh moves/deforms.
Basically the function does:
  - each vertex has it's original XYZ coordinate stored, and
  - brings that XYZ coordinate with it even when it's deformed/transformed
  - the XYZ coordinate is being stored in two UV Maps that are combined with a custom material shader node setup
