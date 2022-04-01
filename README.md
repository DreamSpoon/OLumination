# OLumination

## Blender Lighting Tools, EEVEE HDRI

General tools to help with HDRI in Cycles and EEVEE, and more to come.
Video tutorial coming soon.

### Sunlit Rig prototype
Add the max number of suns in EEVEE (max of 8 sun lights as of Blender 3.0.1) to imrove HDRI lighting in Blender EEVEE.
This requires getting the average pixel colors for large parts of HDRIs, for multiple lights. Also, the angular diameter needs to be calculated and set.
Sunlit Rig automates the process of setting positions, angles (object angles, and the sun light's Angular Diameter), and color.
The whole setup can be easily copied from one Sunlit Rig to another by way of the Armature's Pose (select Sunlit Rig armature, and go to Pose mode, copy pose from/to Sunlit armatures)
Difficult to explain with words alone, tutorial video coming soon.

### Proxy Metric
To make it easier to create geometry in Blender that matches an HDRI background, quickly create objects that can be used to "guess the geometry" more simply/accurately.
E.g. Add a human meta-rig to place in the scene and guess positions of points on uneven ground (e.g. nearby parts of grassy hill).
